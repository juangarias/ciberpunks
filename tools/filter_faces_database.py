#!/usr/bin/python
import os, shutil

# get a prediction for the candidates
path = '/home/juan/ciberpunks/faces/lfw2/'
for filename in os.listdir(path):
  fullPath = path + filename
  if os.path.isdir(fullPath) and len(os.listdir(fullPath)) < 8:
    shutil.rmtree(fullPath)