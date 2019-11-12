#!/usr/bin/env python
# docker run -v "$PWD":/home/joyvan/pcv -v "$HOME"/.ssh/:/home/joyvan/.ssh appf/plantcv python /home/joyvan/pcv/01-query-snapshots.py

from distutils.sysconfig import get_python_lib
print(get_python_lib())

import psycopg2
import psycopg2.extras
import json

db_server = '146.118.66.62'
db_user = 'readonlyuser'
db_password = 'readonlyuser'

db_name = '0000_Production_N'
measurement_label = '0467 Barley'

# Connect to an existing database
conn = psycopg2.connect(host=db_server, dbname=db_name, user=db_user, password=db_password)

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
   trim(both '"' from to_json(time_stamp)::text) as "Time",
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
   camera_label,
   time_stamp desc,
   "Plant ID"
LIMIT 100
""".format(measurement_label=measurement_label))

results = cur.fetchall()

# Close communication with the database
cur.close()
conn.close()

#print(len(results))
#print(json.dumps(results[i]))

#for result in results:
with open("/home/joyvan/pcv/0467-jobs.json", 'w', encoding='utf-8') as f:
  json.dump(results, f, ensure_ascii=False, indent=4)