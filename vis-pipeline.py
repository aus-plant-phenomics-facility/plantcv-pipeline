data_server = '146.118.66.62'
data_user = 'readonlyuser'
data_password = 'readonlyuser'

image_server = '146.118.66.62'
image_user = 'ubuntu'
image_pkey = '/home/joyvan/.ssh/id_rsa'

dbname = '0000_Production_N'
measurement_label = '0467 Barley'

import sys, traceback
import cv2
import numpy as np
import argparse
import string
import paramiko
from plantcv import plantcv as pcv
import psycopg2
import psycopg2.extras
from matplotlib import pyplot as plt


# Connect to an existing database
conn = psycopg2.connect(host=data_server, dbname=dbname, user="readonlyuser", password="readonlyuser")

# Open a cursor to perform database operations
cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

# Query the database and obtain data as Python objects
cur.execute("""
SELECT
   snapshot.id_tag AS "Plant ID",
   metadata_view."Genotype ID",
   metadata_view."Watering Regime",
   metadata_view."Replicate",
   metadata_view."Smarthouse",
   metadata_view."Lane",
   metadata_view."Position",
   snapshot.time_stamp as "Time",
   DATE_PART('day', snapshot.time_stamp - '2019-01-09') as "Time After Planting",
   snapshot.water_amount AS "Water Amount",
   snapshot.weight_after AS "Weight After",
   snapshot.weight_before AS "Weight Before",
   camera_label,
   path
FROM
   snapshot 
   LEFT JOIN
      metadata_view 
      ON snapshot.id_tag = metadata_view.id_tag 
       JOIN tiled_image 
         ON snapshot.id = tiled_image.snapshot_id 
       JOIN tile 
         ON tiled_image.id = tile.tiled_image_id 
       JOIN image_file_table 
         ON tile.image_oid = image_file_table.id    
WHERE
   snapshot.id_tag ~ '^\d+ ?' 
   AND snapshot.measurement_label = '0467 Barley' 
   AND camera_label like '%RGB%'
ORDER BY
   "Plant ID",
   time_stamp
""".format(measurement_label=measurement_label))

results = cur.fetchall()

# Close communication with the database
cur.close()
conn.close()



count = 1178
#for result in results:
while(count < len(results)):

  result = results[count]
  count=count+1
  print("Analysing {} of {}.".format(count,len(results)))
  path = result['path']
  camera_label = result['camera_label']

  # # Load image via SFTP

  mykey = paramiko.RSAKey.from_private_key_file(image_pkey)
  server = image_server
  sshuser = image_user

  client = paramiko.SSHClient()
  #client.load_system_host_keys()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  client.connect(server, username = sshuser, pkey = mykey)
  client.get_transport().window_size = 3 * 1024 * 1024

  pcv.params.debug = 'none'

  sftp = client.open_sftp()
  with sftp.open('/plantdb/ftp-2019/{dbname}/{path}'.format(dbname=dbname,path=path)) as f:

    file_size = f.stat().st_size
    f.prefetch(file_size)
    img = cv2.imdecode(np.frombuffer(f.read(file_size), np.uint8), 1)



  # Convert RGB to HSV and extract the value channel
  s = pcv.rgb2gray_hsv(rgb_img=img, channel='v')

  # Threshold the saturation image removing highs and lows and join
  s_thresh_1 = pcv.threshold.binary(gray_img=s, threshold=10, max_value=255, object_type='light')
  s_thresh_2 = pcv.threshold.binary(gray_img=s, threshold=245, max_value=255, object_type='dark')
  s_thresh = pcv.logical_and(bin_img1=s_thresh_1, bin_img2=s_thresh_2)

  # Median Blur
  s_mblur = pcv.median_blur(gray_img=s_thresh, ksize=5)


  # Convert RGB to LAB and extract the Blue channel
  b = pcv.rgb2gray_lab(rgb_img=img, channel='b')

  # Threshold the blue image
  b_cnt = pcv.threshold.binary(gray_img=b, threshold=128, max_value=255, object_type='light')

  # Fill small objects
  b_fill = pcv.fill(b_cnt, 10)


  # Join the thresholded saturation and blue-yellow images
  bs = pcv.logical_or(bin_img1=s_mblur, bin_img2=b_fill)


  # Apply Mask (for VIS images, mask_color=white)
  masked = pcv.apply_mask(rgb_img=img, mask=bs, mask_color='white')

  # Convert RGB to LAB and extract the Green-Magenta and Blue-Yellow channels
  # Threshold the green-magenta and blue images

  masked_a = pcv.rgb2gray_lab(rgb_img=masked, channel='a')
  maskeda_thresh = pcv.threshold.binary(gray_img=masked_a, threshold=127, max_value=255, object_type='dark')

  # Convert RGB to LAB and extract the Green-Magenta and Blue-Yellow channels
  # Threshold the green-magenta and blue images
  masked_b = pcv.rgb2gray_lab(rgb_img=masked, channel='b')
  maskedb_thresh = pcv.threshold.binary(gray_img=masked_b, threshold=128, max_value=255, object_type='light')

  # Join the thresholded saturation and blue-yellow images (OR)
  ab = pcv.logical_or(bin_img1=maskeda_thresh, bin_img2=maskedb_thresh)

  # Fill small objects
  ab_fill = pcv.fill(bin_img=ab, size=200)

  # Apply mask (for VIS images, mask_color=white)
  masked2 = pcv.apply_mask(rgb_img=masked, mask=ab_fill, mask_color='white')

  # Identify objects
  id_objects, obj_hierarchy = pcv.find_objects(img=masked2, mask=ab_fill)

  # Define ROI

  W = 2472
  H = 3296

  if "far" in camera_label:
      # SIDE FAR
      w = 1600
      h = 1200
      pot = 230#340
      roi1, roi_hierarchy= pcv.roi.rectangle(img=masked2, x=(W-w)/2, y=(H-h-pot), h=h, w=w)
  elif "lower" in camera_label:
      # SIDE LOWER 
      w = 800
      h = 2400
      pot = 340
      roi1, roi_hierarchy= pcv.roi.rectangle(img=masked2, x=1000-w/2, y=(H-h-pot), h=h, w=w)
  elif "upper" in camera_label:
      # SIDE UPPER
      w = 600
      h = 800
      pot = 550
      roi1, roi_hierarchy= pcv.roi.rectangle(img=masked2, x=1400-w/2, y=(H-h-pot), h=h, w=w)
  elif "top" in camera_label:
      # TOP
      w = 450
      h = 450
      roi1, roi_hierarchy= pcv.roi.rectangle(img=masked2, x=(H-h)/2, y=(W-w)/2, h=h, w=w)

  # Decide which objects to keep
  roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img=img, roi_contour=roi1, 
                                                             roi_hierarchy=roi_hierarchy, 
                                                             object_contour=id_objects, 
                                                             obj_hierarchy=obj_hierarchy,
                                                             roi_type='partial')

  # Object combine kept objects
  obj, mask = pcv.object_composition(img=img, contours=roi_objects, hierarchy=hierarchy3)

  if obj is not None:

    # Find shape properties, output shape image (optional)
    shape_imgs = pcv.analyze_object(img=img, obj=obj, mask=mask)

    #if args.writeimg == True:

    #pcv.print_image(img=shape_imgs,filename="{}_shape.png".format(results_file[:-5]))
    #pcv.print_image(img=masked2,filename="{}_obj_on_img.png".format(results_file[:-5]))

    # Shape properties relative to user boundary line (optional)
    #boundary_img1 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, line_position=1680)

    # Determine color properties: Histograms, Color Slices, output color analyzed histogram (optional)
    color_histogram = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type='all')

    # Pseudocolor the grayscale image
    #pseudocolored_img = pcv.visualize.pseudocolor(gray_img=s, mask=kept_mask, cmap='jet')

    for key in result.keys():
      if str(result[key]).isdigit():
        pcv.outputs.add_observation(variable=key, trait=key, method='', scale='', datatype=int, value=result[key], label='')
      else:
        pcv.outputs.add_observation(variable=key, trait=key, method='', scale='', datatype=str, value=result[key], label='')

    # Write shape and color data to results file
    #pcv.print_results(filename="0467/{}_{}_{}.json".format(result[2],result[3],result[4].strftime("%Y-%m-%d %I:%M")))

    print(pcv.outputs.observations)

  exit()