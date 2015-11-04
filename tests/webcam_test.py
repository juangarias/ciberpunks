#!/usr/bin/python

import sys
import cv2
sys.path.append("../")
from common import *

picWin = "Sonria..."

try:
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        logging.error("Arrgghhh! The camera is not working!")
        exit(0)

    outputSize = calculateScaledSize(500, capture=camera)

    cv2.namedWindow(picWin)

    readOk, image = camera.read()
    key = -1

    while readOk:
        print('Image size {0}'.format(image.shape))
        newImage = cv2.resize(image, outputSize)
        cv2.imshow(picWin, newImage)
        print('Image size {0}'.format(image.shape))
        key = cv2.waitKey(5)
        if key != -1:
            print 'You pressed {1}, key code is {0}'.format(key % 256, repr(chr(key % 256)))
            print image.shape
            print('Image size {0}'.format(image.shape))
            scaled = scaleCoords((0, 0, 50, 50), image, outputSize)
            print('Scaled out size {0}'.format(scaled))
        readOk, image = camera.read()

except KeyboardInterrupt:
    pass

cv2.destroyWindow(picWin)
