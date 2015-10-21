#!/usr/bin/python
# coding=utf-8

import argparse, logging, os, sys, threading
from random import randint
import pyinotify
import cv2
from common import (configureLogging, loadCascadeClassifier, calculateScaledSize, readImages, detectFaces, 
  decodeSubjectPictureName, drawLabel)

def configureArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--facesFolder', help="Foder containing all faces files.", 
    default='/home/juan/ciberpunks/faces/at&t_database')
  parser.add_argument('--newSubjectsFolder', help="Foder containing new faces files.", 
    default='/home/juan/ciberpunks/faces/news')
  parser.add_argument('--haarFolder', help="Folder containing HAAR cascades.", 
    default="/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades")
  parser.add_argument('--outputWidth', help="Output with for images to display in windows.", default="350")
  parser.add_argument('--log', help="Log level for logging.", default="WARNING")

  return parser.parse_args()


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, listFacesWindow, faces, outputWidth):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()
        self.listFacesWindow = listFacesWindow
        self.faces = faces
        self.outputWidth = outputWidth

    def run(self):
      #for img in self.faces:
      while not self.stopped():
        pos = randint(0, len(self.faces) - 1)
        img = self.faces[pos]
        outputSize = calculateScaledSize(self.outputWidth, image=img)
        cv2.imshow(self.listFacesWindow, cv2.resize(img, outputSize))
        cv2.waitKey(50)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class NewFaceDetectedEventHandler(pyinotify.ProcessEvent):

  def __init__(self, mainWindow, listFacesWindow, faces, haarFolder, outputWidth):
    self.mainWindow = mainWindow
    self.listFacesWindow = listFacesWindow
    self.faces = faces
    self.faceCascade = loadCascadeClassifier(haarFolder + "/haarcascade_frontalface_alt2.xml")
    self.leftEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_lefteye_2splits.xml")
    self.rightEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_righteye_2splits.xml")
    self.outputWidth = outputWidth
    self.thread = None


  def drawFaceDecorations(self, image, detectedFaces, name):
    color = (120, 120, 120)
    thickness = 2

    for (x, y, w, h, leftEye, rightEye, _) in detectedFaces:
      cv2.rectangle(image, (x,y), (x+w,y+h), color, thickness)

      (eyeX, eyeY, eyeW, eyeH) = leftEye
      cv2.rectangle(image, (x+eyeX, y+eyeY), (x+eyeX+eyeW,y+eyeY+eyeH), color, thickness)

      (eyeX, eyeY, eyeW, eyeH) = rightEye
      cv2.rectangle(image, (x+eyeX, y+eyeY), (x+eyeX+eyeW,y+eyeY+eyeH), color, thickness)

      drawLabel(image, name, (x,y))


  def newSubject(self, pictureFilename):
    logging.debug('New subject detected. Filename {0}'.format(pictureFilename))

    cv2.waitKey(100)
    image = cv2.imread(pictureFilename)
    name, _ = decodeSubjectPictureName(pictureFilename)

    if not image is None:
      outputSize = calculateScaledSize(self.outputWidth, image=image)

      detectedFaces = detectFaces(image, self.faceCascade, self.leftEyeCascade, self.rightEyeCascade, (50, 50))
      image = cv2.resize(image, outputSize)
      
      self.drawFaceDecorations(image, detectedFaces, name)

      cv2.imshow(self.mainWindow, image)

      self.thread = StoppableThread(self.listFacesWindow, self.faces, self.outputWidth)
      self.thread.start()


  def process_IN_CREATE(self, event):
    logging.debug("File {0}".format(event.pathname))
    self.stopThread()
    self.newSubject(event.pathname)

  def process_IN_MOVED_TO(self, event):
    logging.debug("File {0}".format(event.pathname))
    self.stopThread()
    self.newSubject(event.pathname)

  def stopThread(self):
    if not self.thread is None:
      self.thread.stop()
      self.thread.join()


def main():
  args = configureArguments()
  configureLogging(args.log)
  
  logging.info('Starting face ID UI...')

  logging.debug('Loading faces from disk...')
  folders = [args.facesFolder]
  [faces, _, _] = readImages(folders)
  logging.debug('Faces loaded.')

  outputWidth = int(args.outputWidth)

  try:
    mainWindow = "Sujeto detectado"
    cv2.namedWindow(mainWindow)

    listFacesWindow = "Buscando en la base de datos..."
    cv2.namedWindow(listFacesWindow)

    logging.debug('Creating custom event handler...')
    handler = NewFaceDetectedEventHandler(mainWindow, listFacesWindow, faces, args.haarFolder, outputWidth)

    wm = pyinotify.WatchManager() 
    eventsFlag = pyinotify.IN_MOVED_TO | pyinotify.IN_CREATE

    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch(args.newSubjectsFolder, eventsFlag)

    logging.debug('Starting notifier infinite loop...')
    notifier.loop()
  except KeyboardInterrupt:
    pass

  logging.debug('Stopping and destroy all windows.')
  handler.stopThread()
  cv2.destroyAllWindows()


if __name__ == '__main__':
  main()