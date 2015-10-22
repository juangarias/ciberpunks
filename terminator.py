#!/usr/bin/python
import sys, time, Image, logging, argparse
sys.path.append("../")
import numpy
import cv2
from common import (overlayImage, detectElements, configureLogging, detectFaces, calculateCenter, cropFace, 
  loadCascadeClassifier, calculateScaledSize, drawRectangle, drawLabel)


def configureArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--haarFolder', help="Folder for writing collected faces.", 
    default="/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades")
  parser.add_argument('--outputWidth', help="Output with for images to display in windows.", default="800")
  parser.add_argument('--log', help="Log level for logging.", default="WARNING")
  return parser.parse_args()


def main():
  args = configureArguments()
  configureLogging(args.log)

  windowTitle = "Terminator view app"
  cv2.namedWindow(windowTitle)

  faceCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_frontalface_alt2.xml")
  leftEyeCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_lefteye_2splits.xml")
  rightEyeCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_righteye_2splits.xml")

  capture = cv2.VideoCapture(0)
  if not capture.isOpened():
    print("Arrgghhh! The camera is not working!")
    return

  width = int(capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
  logging.debug("Image width {0}".format(width))
  minFaceSize = (int(width * 0.1), int(width * 0.1))
  minEyeSize = (12, 18)
  color = (200,200,200)
  thickness = 1

  outputWidth = int(args.outputWidth)

  readOk, image = capture.read()
  outputSize = calculateScaledSize(outputWidth, image=image)

  scanning = cv2.imread('/home/juan/ciberpunks/faces/scanning.png', cv2.IMREAD_UNCHANGED)
  scanning = cv2.resize(scanning, calculateScaledSize(int(outputWidth / 3), image=scanning))

  overlay = cv2.imread('/home/juan/ciberpunks/faces/red.jpg', cv2.IMREAD_UNCHANGED)
  overlay = cv2.resize(overlay, outputSize)
  opacity = 0.5
  overlayImage(overlay, scanning, int(outputWidth / 3), outputSize[1] * 0.9)


  while (cv2.waitKey(5)==-1 and readOk):

    faces = detectFaces(image, faceCascade, leftEyeCascade, rightEyeCascade, minFaceSize, minEyeSize)

    for (x,y,w,h,l,r) in faces:
      cv2.line(image, (x,0), (x, outputSize[1]), color, thickness)
      cv2.line(image, (x+w,0), (x+w, outputSize[1]), color, thickness)
      cv2.line(image, (0,y), (outputWidth, y), color, thickness)
      cv2.line(image, (0,y+h), (outputWidth, y+h), color, thickness)

    image = cv2.resize(image, outputSize)
    cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)
    cv2.imshow(windowTitle, image)
    readOk, image = capture.read()
    
  cv2.destroyWindow(windowTitle)


#MAIN
if __name__ == '__main__':
  main()
