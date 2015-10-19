#!/usr/bin/python

import argparse, logging, os, sys
import cv2
from common import detectFaces

def configureArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--facesFolder', help="Foder containing faces files.")
  parser.add_argument('--newSubjectsFolder', help="Foder containing new faces files.")
  parser.add_argument('--haarFolder', help="Folder containing HAAR cascades.", 
    default="/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades")
  parser.add_argument('--log', help="Log level for logging.", default="WARNING")

  return parser.parse_args()

def main():
  args = configureArguments()
  configureLogging(args.log)

  #faceSize = (100, 100)
  faceSize = None

  logging.info('Starting face ID UI...')

  faceCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_frontalface_alt2.xml")
  leftEyeCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_lefteye_2splits.xml")
  rightEyeCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_righteye_2splits.xml")

  




if __name__ == '__main__':
  main()