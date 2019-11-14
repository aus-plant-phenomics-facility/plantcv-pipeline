#!/usr/bin/env python

import cv2
import numpy as np
import paramiko
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
  result = json.load(f)


path = result['path']
camera_label = result['camera_label']

os.symlink('{image_base_dir}/{path}'.format(image_base_dir=args.image_base_dir,path=path),'input_image.png')

# Read image
img, path, filename = pcv.readimage(filename='input_image.png')

#print(type(img))

# check image not blank
if np.count_nonzero(img) == 0:
    exit(15)
else:
    pass