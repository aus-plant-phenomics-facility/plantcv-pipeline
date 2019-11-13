#!/usr/bin/env python

import psycopg2
import psycopg2.extras
import json
import argparse

parser = argparse.ArgumentParser(description='Query Snapshots.')
parser.add_argument('db_server', metavar='db_server', type=str,
                    help='.')
parser.add_argument('db_name', metavar='db_name', type=str,
                    help='.')
parser.add_argument('db_user', metavar='db_user', type=str,
                    help='.')
parser.add_argument('db_password', metavar='db_password', type=str,
                    help='.')
parser.add_argument('measurement_label', metavar='measurement_label', type=str,
                    help='.')
parser.add_argument('--limit', metavar='limit', type=int,
                    help='.')



args = parser.parse_args()

# Connect to an existing database
conn = psycopg2.connect(host=args.db_server, dbname=args.db_name, user=args.db_user, password=args.db_password)

# Open a cursor to perform database operations
cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

# Query the database and obtain data as Python objects
query = """
SELECT
   snapshot.id_tag AS "Plant ID",
   metadata_view."Genotype ID",
   metadata_view."Watering Regime",
   metadata_view."Replicate",
   metadata_view."Smarthouse",
   metadata_view."Lane",
   metadata_view."Position",
   to_char(time_stamp,'YYYYmmddThhMMSS') as "Time",
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
   AND snapshot.measurement_label = '{measurement_label}'
   AND camera_label like '%RGB%'
ORDER BY
   camera_label,
   time_stamp desc,
   "Plant ID"
""".format(measurement_label=args.measurement_label)

if (args.limit):
  query = query + " LIMIT {limit}".format(limit=args.limit)

cur.execute(query)

results = cur.fetchall()

# Close communication with the database
cur.close()
conn.close()

#print(len(results))
#print(json.dumps(results[i]))

for result in results:
  with open("job_{}_{}_{}.json".format(result['Plant ID'],result['camera_label'],result['Time']), 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)