#!/usr/bin/python
# coding=utf-8

import sys, time, Image, logging, argparse
sys.path.append("../")
import numpy
import cv2
from common import (detectElements, configureLogging, detectFaces, calculateCenter, cropFace, 
  loadCascadeClassifier, calculateScaledSize, drawRectangle, drawLabel)


def configureArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--log', help="Log level for logging.", default="WARNING")
  return parser.parse_args()


def main():
  args = configureArguments()
  configureLogging(args.log)

  windowTitle = "Test draw app"
  cv2.namedWindow(windowTitle)

  haarFolder = "/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades"
  faceCascade = loadCascadeClassifier(haarFolder + "/haarcascade_frontalface_alt2.xml")
  leftEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_lefteye_2splits.xml")
  rightEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_righteye_2splits.xml")
  mouthCascade = loadCascadeClassifier(haarFolder + '/haarcascade_mcs_mouth.xml')

  color = (120,120,130)
  thickness = 2

  width = 600

  image = cv2.imread('/home/juan/ciberpunks/faces/news/jota-juangarias@gmail.com.jpg')
  image = cv2.resize(image, calculateScaledSize(width, image=image))

  if image is None:
    print 'ERROR: no se pudo leer la imagen.'
    return

  minFaceSize = (10, 10)
  minEyeSize = (5, 5)

  faces = detectFaces(image, faceCascade, leftEyeCascade, rightEyeCascade, minFaceSize, minEyeSize)

  for (x, y, w, h, leftEyes, rightEyes) in faces:
    center = calculateCenter((x,y,w,h))

    cv2.line(image, (x,0), (x, width), color, 2)
    cv2.line(image, (x+w,0), (x+w, width), color, 2)
    cv2.line(image, (0,y), (width, y), color, 2)
    cv2.line(image, (0,y+h), (width, y+h), color, 2)

    drawLabel("Juan Gabriel", image, (x, y+20))

    cv2.imshow(windowTitle, image)
    cv2.waitKey(6000)
    
  cv2.destroyWindow(windowTitle)


if __name__ == '__main__':
  main()
