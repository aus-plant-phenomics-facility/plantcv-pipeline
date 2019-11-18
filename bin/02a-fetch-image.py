#!/usr/bin/env python

import numpy as np
from plantcv import plantcv as pcv
import json
import argparse
import os
import paramiko

parser = argparse.ArgumentParser(description='Analyse a job.')
parser.add_argument('job_file', metavar='job_file', type=str,
					help='json job file')
parser.add_argument('image_server', metavar='image_server', type=str,
					help='.')
parser.add_argument('image_user', metavar='image_user', type=str,
					help='.')
parser.add_argument('image_pkey', metavar='image_pkey', type=str,
					help='.')
parser.add_argument('image_base_dir', metavar='image_base_dir', type=str,
					help='.')


args = parser.parse_args()

with open (args.job_file, 'r', encoding='utf-8') as f:
	job = json.load(f)

ssh_key = paramiko.RSAKey.from_private_key_file(args.image_pkey)
ssh_server = args.image_server
ssh_user = args.image_user

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(ssh_server, username = ssh_user, pkey = ssh_key)
client.get_transport().window_size = 3 * 1024 * 1024

sftp = client.open_sftp()
sftp.get('{full_image_path}'.format(full_image_path=os.path.join(args.image_base_dir,job['path'])),'input_image.png')

img, path, filename = pcv.readimage(filename='input_image.png')

# if image is blank, error with specific code.
if np.count_nonzero(img) == 0:
	exit(15)