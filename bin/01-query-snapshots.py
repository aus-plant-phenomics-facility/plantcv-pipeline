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
parser.add_argument('query_file', metavar='query_file', type=str,
					help='.')
parser.add_argument('--limit', metavar='limit', type=int,
					help='.')



args = parser.parse_args()

conn = psycopg2.connect(host=args.db_server, dbname=args.db_name, user=args.db_user, password=args.db_password)
cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

with open(args.query_file, 'r') as file:
	query = file.read()
	query = query.format(measurement_label=args.measurement_label)

if (args.limit):
	query = query + " LIMIT {limit}".format(limit=args.limit)

cur.execute(query)
results = cur.fetchall()
cur.close()
conn.close()


for result in results:
	with open("job_{}_{}_{}.json".format(result['Plant ID'],result['camera_label'],result['Time']), 'w', encoding='utf-8') as f:
		json.dump(result, f, ensure_ascii=False, indent=4)