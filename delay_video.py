#!/usr/bin/python
import logging
import argparse
import cv2
from common import configureLogging, calculateScaledSize


def configureArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--delay', help="Seconds to delay the video.", default="15", type=int)
    parser.add_argument('--outputWidth', help="Output width.", default="500", type=int)
    parser.add_argument('--log', help="Log level for logging.", default="WARNING")
    return parser.parse_args()


def main():
    args = configureArguments()
    configureLogging(args.log)
    logging.info("Starting video delay...")
    picWin = "Sonria..."

    try:
        camera = cv2.VideoCapture('/home/juan/ciberpunks/videos/brad_pitt.mp4')
        outputSize = calculateScaledSize(args.outputWidth, capture=camera)

        if not camera.isOpened():
            logging.error('Arrrgggghhhh! Camera is not open...')
            return

        cv2.namedWindow(picWin)

        DELAY_FRAMES = 30 * args.delay
        framesBuffer = [None] * DELAY_FRAMES

        logging.debug('Start reading and buffering...')
        for i in xrange(DELAY_FRAMES):
            readOk, image = camera.read()
            framesBuffer.append(image)

        logging.debug('Start display of buffered images and queue new ones...')
        while cv2.waitKey() == -1:
            for i in xrange(DELAY_FRAMES):
                readOk, image = camera.read()
                delayedImage = framesBuffer[i]
                framesBuffer[i] = image

                outputImage = cv2.resize(delayedImage, outputSize)
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
