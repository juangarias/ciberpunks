#!/usr/bin/python
# coding=utf-8

import argparse
import logging
import Queue
import Image
import ImageTk
from random import randint
import cv2
from Tkinter import Tk, Frame, Label, BOTH, YES, LEFT, RIGHT
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from common import *
from subjectHandler import NewSubjectDetectedEventHandler


def configureArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--facesFolder', help="Foder containing all faces files.",
                        default='/home/juan/ciberpunks/faces/at&t_database')
    parser.add_argument('--newSubjectsFolder', help="Foder containing new faces files.",
                        default='/home/juan/ciberpunks/faces/news')
    parser.add_argument('--haarFolder', help="Folder containing HAAR cascades.",
                        default="/home/juan/ciberpunks/opencv-2.4.11/data/haarcascades")
    parser.add_argument('--outputWidth', help="Output with for images to display in windows.",
                        type=int, default="450")
    parser.add_argument('--log', help="Log level for logging.", default="WARNING")

    return parser.parse_args()


def convertImageCVToTk(image):
    # Rearrang the color channel
    if len(image.shape) == 3:
        b, g, r = cv2.split(image)
        image = cv2.merge((r, g, b))
    else:
        b, g, r, a = cv2.split(image)
        image = cv2.merge((r, g, b, a))

    # Convert the Image object into a TkPhoto object
    im = Image.fromarray(image)
    return ImageTk.PhotoImage(image=im)


class FileCreatedEventHandler(FileSystemEventHandler):

    def __init__(self, subjectsQueue):
        self.subjectsQueue = subjectsQueue

    def on_created(self, event):
        logging.debug(event)
        self.subjectsQueue.put(event.src_path)


class FaceIDApp():

    def __init__(self, rootWindow, args):

        self.rootWindow = rootWindow
        self.rootWindow.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.haarFolder = args.haarFolder
        self.outputWidth = args.outputWidth
        self.rootWindow.title('Face Identification App')
        self.rootWindow.geometry('1000x700+440+0')

        self.mainFrame = Frame(self.rootWindow)
        self.mainFrame.configure(background="black")
        self.mainFrame.pack(fill=BOTH, expand=YES)

        self.subjectLabel = Label(self.mainFrame)
        self.subjectLabel.pack(side=LEFT)
        self.listFacesLabel = Label(self.mainFrame)
        self.listFacesLabel.pack(side=RIGHT)

        logging.debug('Loading faces from disk...')
        folders = [args.facesFolder]
        [self.faces, _, _] = readImages(folders)
        logging.debug('Faces loaded.')

        logging.debug('Creating new subject handler...')
        self.newSubjectHandler = NewSubjectDetectedEventHandler(self.haarFolder, self.outputWidth)

        self.subjectsQueue = Queue.Queue()
        handler = FileCreatedEventHandler(self.subjectsQueue)

        logging.debug('Creating observer for watchdog...')
        self.observer = Observer()
        self.observer.schedule(handler, args.newSubjectsFolder)
        self.observer.start()

        self.checkPendingWork()

    def checkPendingWork(self):
        """
        Check every 500 ms if there is something new in the queue.
        """
        logging.debug('Checking for pending work in the queue...')
        if not self.subjectsQueue.empty():
            logging.info('Subjects queue is not empty!')
            outputImage = self.newSubjectHandler.newSubject(self.subjectsQueue.get())
            self.subjectImage = convertImageCVToTk(outputImage)
            self.subjectLabel.configure(image=self.subjectImage)
            self.subjectLabel.pack()

            self.showCollectedFaces()

        self.rootWindow.after(500, self.checkPendingWork)

    def showCollectedFaces(self):
        pos = randint(0, len(self.faces) - 1)
        img = self.faces[pos]
        outputSize = calculateScaledSize(self.outputWidth, image=img)
        outputImage = cv2.resize(img, outputSize)

        self.randomSubjectImage = convertImageCVToTk(outputImage)

        self.listFacesLabel.configure(image=self.randomSubjectImage)
        self.listFacesLabel.pack()

        self.rootWindow.after(100, self.showCollectedFaces)

    def on_closing(self):
        logging.debug('Trying to exit FaceIDApp...')
        self.observer.stop()
        self.observer.join()
        self.rootWindow.destroy()
        logging.info('Exit FaceIDApp gracefully.')


def main():
    args = configureArguments()
    configureLogging(args.log)
    logging.info('Starting face ID UI...')

    logging.debug('Initializing Graphical UI...')
    rootWindow = Tk()
    FaceIDApp(rootWindow, args)

    logging.debug('Start the GUI')
    rootWindow.mainloop()

# end main

if __name__ == '__main__':
    main()
