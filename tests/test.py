#!/usr/bin/python
# coding=utf-8

import sys, time, Image, logging, argparse
sys.path.append("../")
import numpy
import cv2
from common import (detectElements, configureLogging, detectFaces, calculateCenter, cropFace, 
  loadCascadeClassifier, calculateScaledSize, drawRectangle, drawLabel)


def main():
  windowTitle = "Test draw app"
  cv2.namedWindow(windowTitle)

  haarFolder = "/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades"
  faceCascade = loadCascadeClassifier(haarFolder + "/haarcascade_frontalface_alt2.xml")
  leftEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_lefteye_2splits.xml")
  rightEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_righteye_2splits.xml")
  mouthCascade = loadCascadeClassifier(haarFolder + '/haarcascade_mcs_mouth.xml')

  color = (120,120,255)
  thickness = 2

  for i in xrange(1, 10):
    image = cv2.imread('/home/juan/ciberpunks/faces/at&t_database/s10/{0}.pgm'.format(i))
    image = cv2.resize(image, calculateScaledSize(400, image=image))

    if image is None:
      print 'ERROR: no se pudo leer la imagen.'
      return

    minFaceSize = (10, 10)
    minEyeSize = (12, 18)

    faces = detectFaces(image, faceCascade, leftEyeCascade, rightEyeCascade, minFaceSize, minEyeSize, None)

    for (x, y, w, h, leftEye, rightEye, mouths) in faces:
      center = calculateCenter((x,y,w,h))
      box = None
      cv2.ellipse(image, (center, (w, h + 100), 0), color, thickness)

      #drawRectangle(image, rightEye, color, thickness)
      #drawRectangle(image, leftEye, color, thickness)
     
      reCenter = calculateCenter(rightEye)
      cv2.circle(image, reCenter, 5, color, 0)
      cv2.ellipse(image, (reCenter, (rightEye[2], rightEye[3] - 30), 0), color, thickness)

      leCenter = calculateCenter(leftEye)
      cv2.circle(image, leCenter, 5, color, 0)
      cv2.ellipse(image, (leCenter, (leftEye[2], leftEye[3] - 30), 0), color, thickness)

      cv2.line(image, leCenter, reCenter, color, 2)

      if not mouths is None:
        for m in mouths:
          drawRectangle(image, m, (0, 255, 0), thickness)

    drawLabel("Scanning...", image, (100, 50), cv2.FONT_HERSHEY_SIMPLEX)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    cv2.imshow(windowTitle, image)
    cv2.waitKey(1000)
    
  cv2.destroyWindow(windowTitle)


if __name__ == '__main__':
  main()
