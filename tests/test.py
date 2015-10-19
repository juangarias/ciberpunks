#!/usr/bin/python

import sys, time, Image, logging, argparse
import cv2
from common import detectElements, configureLogging, detectFaces, calculateCenter, cropFace, loadCascadeClassifier, calculateScaledSize


def main():
  windowTitle = "Test draw app"
  cv2.namedWindow(windowTitle)

  haarFolder = "/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades"
  faceCascade = loadCascadeClassifier(haarFolder + "/haarcascade_frontalface_alt2.xml")
  leftEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_lefteye_2splits.xml")
  rightEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_righteye_2splits.xml")
  mouthCascade = loadCascadeClassifier(haarFolder + '/haarcascade_mcs_mouth.xml')
  

  color = (120,120,120)
  thickness = 1

  for i in xrange(1, 10):
    image = cv2.imread('/home/juan/ciberpunks/faces/at&t_database/s12/{0}.pgm'.format(i))
    image = cv2.resize(image, calculateScaledSize(400, image=image))

    if image is None:
      print 'ERROR: no se pudo leer la imagen.'
      return

    minFaceSize = (10, 10)
    minEyeSize = (12, 18)

    faces = detectFaces(image, faceCascade, leftEyeCascade, rightEyeCascade, minFaceSize, minEyeSize, mouthCascade)

    for (x, y, w, h, leftEye, rightEye, mouth) in faces:
      center = calculateCenter((x,y,w,h))
      box = None
      cv2.ellipse(image, (center, (w, h + 15), 0), color, thickness)

      (centerRX, centerRY) = calculateCenter(rightEye)
      (centerLX, centerLY) = calculateCenter(leftEye)

      (a,b,c,d) = rightEye
      cv2.rectangle(image, (x+a,y+b), (x+a+c,y+b+d), color, thickness)
      (a,b,c,d) = leftEye
      cv2.rectangle(image, (x+a,y+b), (x+a+c,y+b+d), color, thickness)

      le = (x+centerLX,y+centerLY)
      re = (x+centerRX,y+centerRY)
      
      cv2.circle(image, re, 5, color, 0)
      cv2.circle(image, le, 5, color, 0)

      cv2.line(image, le, re, color, 2)

      baseY = int(6.5*h/10)
      for (mx, my, mw, mh) in mouth:
        cv2.rectangle(image, (x+mx,y+baseY+my), (x+mx+mw,y+baseY+my+mh), (0, 0, 255), thickness)

    cv2.imshow(windowTitle, image)
    cv2.waitKey(1000)
    cv2.destroyWindow(windowTitle)


if __name__ == '__main__':
  main()