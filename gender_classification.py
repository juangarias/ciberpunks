#!/usr/bin/python
# coding=utf-8

import argparse, logging, csv, numpy
from numpy import genfromtxt
from time import sleep
import cv2
import common

def ConfigureArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('videoFileName', help="Video's file name to process.")
  parser.add_argument('--log', help="Log level for logging.", default="WARNING")
  parser.add_argument('--trainFileName', help="Training CSV's file name for the program.", 
    default="entrenamiento_genero.csv")
  parser.add_argument('--haarFolder', help="Folder for writing collected faces.", 
    default="/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades")
  return parser.parse_args()

def main():
  args = ConfigureArguments()
  common.ConfigureLogging(args.log)

  title = "Gender classificator"
  cv2.namedWindow(title)

  trainData = genfromtxt(args.trainFileName, delimiter=';', dtype=[('mystring','S100'),('myint','i8')])
  images = [None] * len(trainData)
  labels = [None] * len(trainData)
  contador = 0

  for (imgFile, label) in trainData:
    images[contador] = cv2.imread(imgFile)
    labels[contador] = label
    contador += 1

  recognizer = cv2.createFisherFaceRecognizer()
  recognizer.train(numpy.array(images), numpy.array(labels))

  faceCascade = cv2.CascadeClassifier(args.haarFolder + "/haarcascade_frontalface_alt2.xml")
  leftEyeCascade = cv2.CascadeClassifier(args.haarFolder + "/haarcascade_lefteye_2splits.xml")
  rightEyeCascade = cv2.CascadeClassifier(args.haarFolder + "/haarcascade_righteye_2splits.xml")
  minFaceSize = (100, 100)
  minEyeSize = (12, 18)

  capture = cv2.VideoCapture(args.videoFileName)
  readOk = True
  color = (255, 0, 0)

  while (cv2.waitKey(15)==-1 and readOk):
    readOk, image = capture.read()

    faces = common.DetectElements(image, faceCascade, minFaceSize)

    for (x, y, w, h) in faces:
      logging.info("Detected face: ({0} {1} {2} {3})".format(x,y,w,h))
      tempFace = image[y:y+h, x:x+w]
      faceUpper = tempFace[0:int(6*h/10), 0:w]

      leftEyes = common.DetectElements(faceUpper, leftEyeCascade, minEyeSize, 0)
      logging.info("Detected {0} left eyes".format(len(leftEyes)))

      rightEyes = common.DetectElements(faceUpper, rightEyeCascade, minEyeSize, 0)
      logging.info("Detected {0} right eyes".format(len(rightEyes)))

      if len(leftEyes) > 0 and len(rightEyes) > 0:
        lCenter = common.CalculateCenter(leftEyes[0])
        rCenter = common.CalculateCenter(rightEyes[0])
        logging.debug("Cropping face. Left eye center {0}. Right eye center {1}".format(lCenter, rCenter))
        cropped = common.CropFace(tempFace, rCenter, lCenter)

        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        prediction = recognizer.predict(gray)
        print "Prediction says {0}".format(prediction)

      cv2.rectangle(image, (x,y), (x+w,y+h), color, 5, 8, 0)

    cv2.imshow(title, image)

  cv2.destroyWindow(title)
#end main

if __name__ == '__main__':
  main()