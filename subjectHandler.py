import logging
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
        filename = getFilename(picturePath)
        name, email = decodeSubjectPictureName(filename)
        outputImage = None
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

        return name, email, outputImage

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
        cornerThickness = 4

        for (x, y, w, h, leftEyes, rightEyes) in detectedFaces:
            offset = int(w * 0.2)
            radius = int(offset / 3)
            # face = (x, y, w, h)
            # drawRectangle(image, face, color, thickness)

            self.drawCorner(image, x, y, offset, color, cornerThickness)
            self.drawCorner(image, x + w, y + h, -1 * offset, color, cornerThickness)
            self.drawReverseCorner(image, x, y + h, offset, color, cornerThickness)
            self.drawReverseCorner(image, x + w, y, -1 * offset, color, cornerThickness)

            self.drawEyeDecorations(image, leftEyes)
            self.drawEyeDecorations(image, rightEyes)

            center = calculateCenter((x, y, w, h))
            cv2.circle(image, center, radius - 5, color)
            (x1, y1) = center
            cv2.line(image, (x1 - radius, y1), (x1 + radius, y1), color, thickness)
            cv2.line(image, (x1, y1 - radius), (x1, y1 + radius), color, thickness)

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
