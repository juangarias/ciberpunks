#!/usr/bin/python
# coding=utf-8
import argparse
import Tkinter as tk
from common import *
from face_id_ui import FaceIDApp


def configureArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--haarFolder', help="Folder containing HAAR cascades.",
                        default='/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades')
    parser.add_argument('--newSubjectsFolder', help="Foder containing new faces files.",
                        default='/home/juan/ciberpunks/faces/news')
    parser.add_argument('--outputWidth', help='Output with for images to display in windows.',
                        type=int, default="500")
    parser.add_argument('--log', help="Log level for logging.", default="WARNING")

    return parser.parse_args()


class FaceCollectorApp(FaceIDApp):

    def loadFaces(self):
        logging.debug('Loading faces from disk...')
        self.faces = readImages(self.facesFolder)
        logging.debug('Faces loaded.')

    def addSubjectField(self, container, name, value, row):
        pass

    def showDetectedSubject(self, name, image, rawImage):
        logging.debug('Showing detected subject {0}'.format(name))
        self.faces.append(rawImage)
        self.showDetectedSubjectPicture(image)

    def launchSearch(self, name, email):
        pass

    def rotateWebData(self):
        pass


def main():
    args = configureArguments()
    configureLogging(args.log)
    logging.info('Starting face ID UI...')

    logging.debug('Initializing Graphical UI...')
    rootWindow = tk.Tk()
    FaceCollectorApp(rootWindow, args)

    logging.debug('Start the GUI')
    rootWindow.mainloop()
# end main

if __name__ == '__main__':
    main()
