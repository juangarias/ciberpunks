import logging
import os
import cv2
from common import *


class NewSubjectDetectedEventHandler():

    def __init__(self, haarFolder, outputWidth):
        self.faceCascade = loadCascadeClassifier(haarFolder + "/haarcascade_frontalface_alt2.xml")
        self.leftEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_lefteye_2splits.xml")
        self.rightEyeCascade = loadCascadeClassifier(haarFolder + "/haarcascade_righteye_2splits.xml")
        self.outputWidth = outputWidth

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

            logging.debug('Decorating face for display...')
            self.drawFaceDecorations(outputImage, detectedFaces, name)

            logging.debug('Returning decorated face.')
            return outputImage
        else:
            return None

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
        thickness = 1
        cornerThickness = 3
        offset = int(self.outputWidth * 0.2)
        halfOffset = int(offset / 2)

        for (x, y, w, h, leftEyes, rightEyes) in detectedFaces:
            face = (x, y, w, h)
            drawRectangle(image, face, color, thickness)

            self.drawCorner(image, x, y, offset, color, cornerThickness)
            self.drawCorner(image, x + w, y + h, -1 * offset, color, cornerThickness)

            self.drawReverseCorner(image, x, y + h, offset, color, cornerThickness)
            self.drawReverseCorner(image, x + w, y, -1 * offset, color, cornerThickness)

            self.drawEyeDecorations(image, leftEyes)
            self.drawEyeDecorations(image, rightEyes)

            center = calculateCenter((x, y, w, h))
            cv2.circle(image, center, halfOffset - 5, color)
            (x1, y1) = center
            cv2.line(image, (x1 - halfOffset, y1), (x1 + halfOffset, y1), color, thickness)
            cv2.line(image, (x1, y1 - halfOffset), (x1, y1 + halfOffset), color, thickness)

            drawLabel(name, image, (x, y))

    def drawCorner(self, image, x, y, offset, color, thickness):
        cv2.line(image, (x, y), (x + offset, y), color, thickness)
        cv2.line(image, (x, y), (x, y + offset), color, thickness)

    def drawReverseCorner(self, image, x, y, offset, color, thickness):
        cv2.line(image, (x, y), (x + offset, y), color, thickness)
        cv2.line(image, (x, y), (x, y - offset), color, thickness)

    def drawEyeDecorations(self, image, eyes):
        color = (120, 120, 120)
        thickness = 1

        for eye in eyes:
            drawRectangle(image, eye, color, thickness)
