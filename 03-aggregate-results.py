# docker run -v "$PWD":/home/joyvan/pcv -v "$HOME"/.ssh/:/home/joyvan/.ssh appf/plantcv python /home/joyvan/pcv/03-aggregate-results.py

from plantcv import utils as pcv_utils
from plantcv import parallel as pcv_parallel

results_dir = "/home/joyvan/pcv/0467-results/"

json_file = "/home/joyvan/pcv/merged.json"
csv_file = "/home/joyvan/pcv/merged"

pcv_parallel.process_results(results_dir, json_file)

pcv_utils.json2csv(json_file=json_file, csv_file=csv_file)