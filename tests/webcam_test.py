#!/usr/bin/python

import argparse, logging, os, sys
from common import calculateScaledSize
import cv2

picWin = "Sonria..."

try:
  camera = cv2.VideoCapture(0)
  outputSize = calculateScaledSize(500, capture=camera)

  cv2.namedWindow(picWin)

  readOk, image = camera.read()
  key = -1

  while readOk:
    cv2.imshow(picWin, cv2.resize(image, outputSize))
    key = cv2.waitKey(5)
    if key != -1:
      print 'You pressed {1}, key code is {0}'.format(key % 256, repr(chr(key%256)))
    readOk, image = camera.read()

except KeyboardInterrupt:
  pass

cv2.destroyWindow(picWin)