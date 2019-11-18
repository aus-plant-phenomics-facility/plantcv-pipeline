#!/usr/bin/env python

import cv2
import numpy as np
import paramiko
from plantcv import plantcv as pcv
import json
import argparse


### Parse command-line arguments
def options():
	parser = argparse.ArgumentParser(description="Imaging processing with opencv")
	parser.add_argument("-i", "--image", help="Input image file.", required=True)
	parser.add_argument("-m", "--metadata", help="Input metadata file.", required=True)
	parser.add_argument("-o", "--outdir", help="Output directory for image files.", required=False)
	parser.add_argument("-r", "--result", help="result file.", required=False)
	parser.add_argument("-w", "--writeimg", help="write out images.", default=False, action="store_true")
	parser.add_argument("-D", "--debug",
						help="can be set to 'print' or None (or 'plot' if in jupyter) prints intermediate images.",
						default=None)
	args = parser.parse_args()
	return args

#### Start of the Main/Customizable portion of the workflow.

### Main workflow
def main():
	# Get options
	args = options()

	pcv.params.debug = args.debug  # set debug mode
	pcv.params.debug_outdir = args.outdir  # set output directory

	# Read metadata
	with open (args.metadata, 'r', encoding='utf-8') as f:
	  md = json.load(f)

	camera_label = md['camera_label']

	# Read image
	img, path, filename = pcv.readimage(filename=args.image)

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

	#TODO: Update for plantCV metadata import
	for key in md.keys():
		if str(md[key]).isdigit():
			pcv.outputs.add_observation(variable=key, trait=key, method='', scale='', datatype=int, value=md[key], label='')
		else:
			pcv.outputs.add_observation(variable=key, trait=key, method='', scale='', datatype=str, value=md[key], label='')

	if obj is not None:

		# Find shape properties, output shape image (optional)
		shape_imgs = pcv.analyze_object(img=img, obj=obj, mask=mask)

		# Shape properties relative to user boundary line (optional)
		#boundary_img1 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, line_position=1680)

		# Determine color properties: Histograms, Color Slices, output color analyzed histogram (optional)
		color_histogram = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type='all')

		# Pseudocolor the grayscale image
		#pseudocolored_img = pcv.visualize.pseudocolor(gray_img=s, mask=kept_mask, cmap='jet')

		#print(pcv.outputs.images)
		if args.writeimg == True:
			for idx,item in enumerate(pcv.outputs.images[0]):
				pcv.print_image(item, "{}_{}.png".format(args.result[:-5],idx))

	# Write shape and color data to results file
	pcv.print_results(filename=args.result)

if __name__ == '__main__':
	main()