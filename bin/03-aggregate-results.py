#!/usr/bin/env python

from plantcv import utils as pcv_utils
from plantcv import parallel as pcv_parallel

results_dir = "."

json_file = "merged.json"
csv_file = "merged"


# TODO: do I need to delete the file first?
# does process results correctly ignore job files that have already been added?


pcv_parallel.process_results(results_dir, json_file)

pcv_utils.json2csv(json_file=json_file, csv_file=csv_file)