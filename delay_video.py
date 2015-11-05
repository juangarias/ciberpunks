#!/usr/bin/python
import logging
import argparse
import cv2
from common import configureLogging, calculateScaledSize


def configureArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--delay', help="Seconds to delay the video.", default="10", type=int)
    parser.add_argument('--outputWidth', help="Output width.", default="500", type=int)
    parser.add_argument('--log', help="Log level for logging.", default="WARNING")
    return parser.parse_args()


def main():
    args = configureArguments()
    configureLogging(args.log)
    logging.info("Starting video delay...")
    picWin = "Sonria..."

    try:
        camera = cv2.VideoCapture(0)
        outputSize = calculateScaledSize(args.outputWidth, capture=camera)

        if not camera.isOpened():
            logging.error('Arrrgggghhhh! Camera is not open...')
            return None

        cv2.namedWindow(picWin)

        fps = camera.get(cv2.cv.CV_CAP_PROP_FPS)
        logging.debug('Detected {0} FPS'.format(fps))
        fps = fps if fps > 0 else 30
        logging.debug('Using {0} FPS'.format(fps))

        frameBufferSize = fps * args.delay
        framesBuffer = [None] * frameBufferSize

        logging.debug('Start reading and buffering {0} frames...'.format(frameBufferSize))
        i = 0
        while cv2.waitKey(1) and i < frameBufferSize:
            readOk, image = camera.read()
            framesBuffer[i] = image
            i += 1

        logging.debug('Start display of buffered images and queue new ones...')
        while True:
            for i in xrange(frameBufferSize):
                readOk, image = camera.read()
                delayedImage = framesBuffer[i]
                framesBuffer[i] = image

                outputImage = delayedImage  # cv2.resize(delayedImage, outputSize)
                cv2.imshow(picWin, outputImage)
                cv2.waitKey(1)

    except KeyboardInterrupt:
        pass

    logging.debug('Trying to exit app gracefuly.')
    camera.release()
    cv2.destroyWindow(picWin)
    logging.info('Exit video delay OK.')
# end main

if __name__ == '__main__':
    main()
