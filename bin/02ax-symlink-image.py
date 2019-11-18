#!/usr/bin/env python

import numpy as np
from plantcv import plantcv as pcv
import json
import argparse
import os

parser = argparse.ArgumentParser(description='Analyse a job.')
parser.add_argument('job_file', metavar='job_file', type=str,
					help='json job file')
parser.add_argument('image_base_dir', metavar='image_base_dir', type=str,
					help='.')


args = parser.parse_args()

with open (args.job_file, 'r', encoding='utf-8') as f:
	job = json.load(f)

os.symlink('{image_base_dir}/{path}'.format(image_base_dir=args.image_base_dir,path=job['path']),'input_image.png')

# Read image
img, path, filename = pcv.readimage(filename='input_image.png')

# if image is blank, error with specific code.
if np.count_nonzero(img) == 0:
	exit(15)