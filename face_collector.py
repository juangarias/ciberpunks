#!/usr/bin/python
# coding=utf-8

import logging
import argparse
import cv2
from common import *


def configureArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fileName', help="The file name of the video to process.")
    parser.add_argument('--outFolder', help="Folder for writing collected faces.",
                        default="/home/juan/ciberpunks/faces/news")
    parser.add_argument('--haarFolder', help="Folder for writing collected faces.",
                        default="/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades")
    parser.add_argument('--outputWidth', help="Output with for images to display in windows.",
                        default="600", type=int)
    parser.add_argument('--log', help="Log level for logging.", default="WARNING")
    return parser.parse_args()


def buildFileName(contador, folder=""):
    return folder + '/face_' + str(contador) + '.jpg'


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

    cv2.namedWindow(windowTitle)

    capture = buildVideoCapture(args.fileName)
    if not capture.isOpened():
        logging.error("Arrgghhh! The camera is not working!")
        return

    faceCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_frontalface_alt2.xml")
    leftEyeCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_lefteye_2splits.xml")
    rightEyeCascade = loadCascadeClassifier(args.haarFolder + "/haarcascade_righteye_2splits.xml")

    rectColor = (120, 120, 120)
    rectThickness = 2
    formatParams = [int(cv2.IMWRITE_JPEG_QUALITY), 100]

    width = capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    logging.debug("Image width {0}".format(width))
    minFaceSize = (int(width * 0.1), int(width * 0.1))
    minEyeSize = (12, 18)

    contador = 1
    frameCount = 0

    logging.debug("Reading capture...")
    readOk, image = capture.read()
    outputSize = calculateScaledSize(args.outputWidth, image=image)

    try:
        while (cv2.waitKey(5) == -1 and readOk):

            # Skip 2 of 3 frames
            if frameCount % 3 == 0:

                faces = detectFaces(image, faceCascade, leftEyeCascade, rightEyeCascade, minFaceSize, minEyeSize)

                for (x, y, w, h, leftEye, rightEye) in faces:
                    lCenter = calculateCenter(leftEye[0])
                    rCenter = calculateCenter(rightEye[0])
                    logging.debug("Cropping face. Left eye center {0}. Right eye center {1}".format(lCenter, rCenter))
                    cropped = cropFace(image, rCenter, lCenter)
                    grayCropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                    cv2.imwrite(buildFileName(contador, args.outFolder), grayCropped, formatParams)
                    contador += 1

                    drawRectangle(image, (x, y, w, h), rectColor, rectThickness)

            cv2.imshow(windowTitle, cv2.resize(image, outputSize))
            frameCount += 1

            logging.debug("Reading capture...")
            readOk, image = capture.read()

    except KeyboardInterrupt:
        pass
    finally:
        del(capture)
        cv2.destroyWindow(windowTitle)


if __name__ == '__main__':
    main()
