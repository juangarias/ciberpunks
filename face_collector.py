#!/usr/bin/python

import sys, time, Image, logging, argparse
import cv2
from common import configureLogging, detectFaces, calculateCenter, cropFace, loadCascadeClassifier

def configureArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--fileName', help="The file name of the video to process.")
  parser.add_argument('--outFolder', help="Folder for writing collected faces.", 
    default="/home/juan/ciberpunks/faces")
  parser.add_argument('--haarFolder', help="Folder for writing collected faces.", 
    default="/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades")
  parser.add_argument('--log', help="Log level for logging.", default="WARNING")
  return parser.parse_args()


def buildFileName(contador, folder=""):
  return folder + '/face_' + `contador` + '.jpg'


def buildVideoCapture(fileName):
  if fileName:
    return cv2.VideoCapture(fileName)
  else:
    return cv2.VideoCapture(0)
    

def main():
  args = configureArguments()
  configureLogging(args.log)

  logging.info("Starting face collector")
  windowTitle = "Face collector App"
  blue = (255, 0, 0)
  green = (0, 255, 0)
  red = (0, 0, 255)
  rectThickness = 2

  cv2.namedWindow(windowTitle)

  capture = buildVideoCapture(args.fileName)

  if not capture.isOpened():
    logging.error("Arrgghhh! The camera is not working!")
    return

  #faceCascade = cv.Load(haarDir + "haarcascade_frontalface_alt2.xml")
  #faceCascade = cv.Load(haarDir + "haarcascade_frontalface_default.xml")
  #faceCascade = cv.Load(haarDir + "haarcascade_frontalface_alt.xml")
  #faceCascade = cv.Load("haarcascades/haarcascade_frontalface_alt_tree.xml")
  #faceCascade = cv2.CascadeClassifier(haarDir + "haarcascade_profileface.xml")
  faceCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_frontalface_alt2.xml")
  leftEyeCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_lefteye_2splits.xml")
  rightEyeCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_righteye_2splits.xml")

  readOk = True
  contador = 1
  formatParams = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

  width = capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
  logging.debug("Image width {0}".format(width))
  minFaceSize = (int(width * 0.1), int(width * 0.1))
  minEyeSize = (12, 18)

  frameCount = 0

  logging.debug("Reading capture...")
  readOk, image = capture.read()

  while (cv2.waitKey(15)==-1 and readOk):

    #Skip 2 of 3 frames
    if frameCount % 3 == 0 :

      faces = detectFaces(image, faceCascade, leftEyeCascade, rightEyeCascade, minFaceSize, minEyeSize)

      for (x, y, w, h, leftEyes, rightEyes) in faces:
        lCenter = calculateCenter(leftEyes[0])
        rCenter = calculateCenter(rightEyes[0])
        logging.debug("Cropping face. Left eye center {0}. Right eye center {1}".format(lCenter, rCenter))
        cropped = cropFace(image[y:y+h, x:x+w], rCenter, lCenter)
        grayCropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(buildFileName(contador, args.outFolder), grayCropped, formatParams)
        contador += 1

        cv2.rectangle(image, (x,y), (x+w,y+h), blue, rectThickness)

    cv2.imshow(windowTitle, image)
    frameCount += 1

    logging.debug("Reading capture...")
    readOk, image = capture.read()


  del(capture)
  cv2.destroyWindow(windowTitle)


if __name__ == '__main__':
  main()