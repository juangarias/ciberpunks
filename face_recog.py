#!/usr/bin/python

import argparse, logging, os, sys, Image
import numpy as np
import cv2
from common import readImages, configureLogging, detectFaces, resizeImage, loadCascadeClassifier, drawLabel

def configureArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--videoFileName', help="Video's file name to process.")
  parser.add_argument('--haarFolder', help="Folder containing HAAR cascades.", 
    default="/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades")
  parser.add_argument('--log', help="Log level for logging.", default="WARNING")

  return parser.parse_args()


def recognizePictureCandidates(faceRecognizer, subjects, imageSize = None):
  path = "/home/juan/ciberpunks/faces/candidatos/"
  for filename in os.listdir(path):
    try:
      im = Image.open(os.path.join(path, filename))
      im = resizeImage(im.convert("L"), imageSize)
      image = np.asarray(im, dtype=np.uint8)
      (prediction, distance) = faceRecognizer.predict(image)
      print "Filename: {0} - Predicted = {1} with distance {2}".format(filename, subjects[prediction], distance)
    except IOError as e:
      print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
      print "Unexpected error:", sys.exc_info()[0]
      raise


def recognizeVideo(faceRecognizer, videoFileName, subjects, haarFolder):
  faceCascade = loadCascadeClassifier(haarFolder + "/haarcascade_frontalface_alt2.xml")
  leftEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_lefteye_2splits.xml")
  rightEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_righteye_2splits.xml")

  if not videoFileName:
    videoFileName = 0

  capture = cv2.VideoCapture(videoFileName)
  readOk, image = capture.read()

  if readOk:
    height, width, channels = image.shape
  else:
    logging.warning("Could not read capture!!")
    return

  minFaceSize = (int(width * 0.1), int(width * 0.1))
  rectColor = (255, 0, 0)
  rectThickness = 2
  fontColor = (255, 255, 255)
  fontScale = 0.8
  fontThickness = 1

  title = 'Face Recognizer App'
  cv2.namedWindow(title)

  while cv2.waitKey(10) == -1 and readOk:

    faces = detectFaces(image, faceCascade, leftEyeCascade, rightEyeCascade, minFaceSize)

    if len(faces) == 0 :
      for i in xrange(0, 3):
        cv2.imshow(title, image)
        _, image = capture.read()

    else:
      for (x, y, w, h, _, _) in faces:
        face = cv2.cvtColor(image[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
        faceGray = cv2.resize(face, (92, 112))
        (prediction, distance) = faceRecognizer.predict(faceGray)

        if distance > 140:
          predictionLegend = "Unknow subject"
        else:
          predictionLegend = "Predicted {0} - Distance {1}".format(subjects[prediction], distance)
        cv2.rectangle(image, (x,y), (x+w,y+h), rectColor, rectThickness)
        drawLabel(predictionLegend, image, (x-20, y-10))
    
    cv2.imshow(title, image)
    readOk, image = capture.read()

  cv2.destroyWindow(title)
  


def main():
  args = configureArguments()
  configureLogging(args.log)

  #faceSize = (100, 100)
  faceSize = None

  logging.debug('Creating face recognizer...')
  #fr = cv2.createFisherFaceRecognizer()
  fr = cv2.createLBPHFaceRecognizer()

  #modelFile = '/home/juan/ciberpunks/faces/lpbFaceModel'
  #if os.path.isfile(modelFile):
  #  fr.load(modelFile)
  #  logging.info('Loaded saved model state.')
  #else:
  trainPaths = [
    '/home/juan/ciberpunks/faces/at&t_database', 
    '/home/juan/ciberpunks/faces/lfw2', 
    '/home/juan/ciberpunks/faces/prestico']

  [images, labels, subjects] = readImages(trainPaths, faceSize)

  logging.debug('Training face recognizer...')
  fr.train(images, labels)
  #fr.save(modelFile)
  #logging.info('Saved a trained model state.')

  logging.debug('Staring face recognition...')
  #recognizePictureCandidates(fr, subjects, faceSize)
  recognizeVideo(fr, args.videoFileName, subjects, args.haarFolder)



if __name__ == '__main__':
  main()