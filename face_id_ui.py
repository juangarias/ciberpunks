#!/usr/bin/python
# coding=utf-8

import argparse
import logging
import time
import os
import Queue
from random import randint
from watchdog.observers import Observer
import cv2
from common import *

if os.name == 'posix':
    from watchdogEventHandler import FileCreatedEventHandler
else:
    from pyinotifyEventHandler import FileCreatedEventHandler


def configureArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--facesFolder', help="Foder containing all faces files.",
                        default='/Users/juan/faces/at&t_database')
    parser.add_argument('--newSubjectsFolder', help="Foder containing new faces files.",
                        default='/Users/juan/faces/news')
    parser.add_argument('--haarFolder', help="Folder containing HAAR cascades.",
                        default="/usr/local/Cellar/opencv/2.4.12/share/OpenCV/haarcascades")
    parser.add_argument('--outputWidth', help="Output with for images to display in windows.", default="350")
    parser.add_argument('--log', help="Log level for logging.", default="WARNING")

    return parser.parse_args()


def showCollectedFaces(faces, outputWidth, listFacesWindow):

    lenFaces = len(faces)

    logging.debug('Showing list of {0} faces randomly...'.format(lenFaces))
    for i in xrange(30):
        pos = randint(0, lenFaces - 1)
        img = faces[pos]
        outputSize = calculateScaledSize(outputWidth, image=img)
        cv2.imshow(listFacesWindow, cv2.resize(img, outputSize))
        cv2.waitKey(75)


class NewSubjectDetectedEventHandler():

    def __init__(self, faces, haarFolder, outputWidth):
        self.mainWindow = "Sujeto detectado"
        self.faces = faces
        self.faceCascade = loadCascadeClassifier(haarFolder + "/haarcascade_frontalface_alt2.xml")
        self.leftEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_lefteye_2splits.xml")
        self.rightEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_righteye_2splits.xml")
        self.outputWidth = outputWidth

        logging.debug('Creating main window...')
        cv2.namedWindow(self.mainWindow)

    def newSubject(self, picturePath):
        logging.debug('New subject detected. Filename {0}'.format(picturePath))
        image = cv2.imread(picturePath)
        (_, filename) = os.path.split(picturePath)
        name, _ = decodeSubjectPictureName(filename)
        logging.debug('Image read OK. Name is: {0}'.format(name))

        # Wait for filesystem to finish write the data.- jarias
        cv2.waitKey(100)

        if image is not None:
            detectedFaces = detectFaces(image, self.faceCascade, self.leftEyeCascade, self.rightEyeCascade, (50, 50))

            outputSize = calculateScaledSize(self.outputWidth, image=image)
            detectedFaces = self.scaleFaceCoords(detectedFaces, image)
            outputImage = cv2.resize(image, outputSize)

            logging.debug('Decorating face and showing it...')
            self.drawFaceDecorations(outputImage, detectedFaces, name)

            cv2.imshow(self.mainWindow, outputImage)
            cv2.waitKey(5)

    def scaleFaceCoords(self, facesCoords, image):
        ret = []

        for (x, y, w, h, leftEyes, rightEyes) in facesCoords:
            (sx, sy, sw, sh) = scaleCoords((x, y, w, h), image, self.outputWidth)
            scaledLeftEyes = self.scaleEyes(leftEyes, image)
            scaledRightEyes = self.scaleEyes(rightEyes, image)

            ret.append((sx, sy, sw, sh, scaledLeftEyes, scaledRightEyes))

        return ret

    def scaleEyes(self, eyes, image):
        ret = []

        for i in eyes:
            ret.append(scaleCoords(i, image, self.outputWidth))

        return ret

    def drawFaceDecorations(self, image, detectedFaces, name):
        color = (120, 120, 120)
        thickness = 2

        for (x, y, w, h, leftEyes, rightEyes) in detectedFaces:
            face = (x, y, w, h)
            drawRectangle(image, face, color, thickness)

            self.drawEyeDecorations(image, leftEyes)
            self.drawEyeDecorations(image, rightEyes)

            drawLabel(name, image, (x, y))

    def drawEyeDecorations(self, image, eyes):
        color = (120, 120, 120)
        thickness = 2

        for eye in eyes:
            drawRectangle(image, eye, color, thickness)


def main():
    args = configureArguments()
    configureLogging(args.log)
    logging.info('Starting face ID UI...')

    logging.debug('Loading faces from disk...')
    folders = [args.facesFolder]
    [faces, _, _] = readImages(folders)
    logging.debug('Faces loaded.')

    outputWidth = int(args.outputWidth)

    subjectsQueue = Queue.Queue()
    newSubjectHandler = NewSubjectDetectedEventHandler(faces, args.haarFolder, outputWidth)

    try:
        handler = FileCreatedEventHandler(faces, args.haarFolder, outputWidth, subjectsQueue)
        observer = Observer()
        observer.schedule(handler, args.newSubjectsFolder)
        observer.start()

        while True:
            if not subjectsQueue.empty():
                newSubjectHandler.newSubject(subjectsQueue.get())

            showCollectedFaces(faces, outputWidth, 'Buscando objetivo...')

            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    logging.debug('Stopping and destroy all windows...')
    observer.join()
    cv2.destroyAllWindows()
    cv2.waitKey(10)
    logging.info('Exit face ID UI gracefully.')


if __name__ == '__main__':
    main()
