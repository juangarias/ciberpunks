#!/usr/bin/python
# coding=utf-8
import argparse
import logging
import Queue
import Image
import ImageTk
import urllib2
import base64
from random import randint
import cv2
import tkFont
from Tkinter import Tk, Frame, Label, BOTH, YES, LEFT, RIGHT, TOP, RIDGE
from watchdog.observers import Observer
from watchdogEventHandler import FileCreatedEventHandler
from common import *
from websearch import searchFullContact, getList
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
                        type=int, default="600")
    parser.add_argument('--log', help="Log level for logging.", default="WARNING")

    return parser.parse_args()


def convertImageCVToTk(image):
    # Rearrang the color channel
    b, g, r = cv2.split(image)
    image = cv2.merge((r, g, b))

    # Convert the Image object into a TkPhoto object
    im = Image.fromarray(image)
    return ImageTk.PhotoImage(image=im)


class FaceIDApp():

    def __init__(self, rootWindow, args):
        self.rootWindow = rootWindow
        self.rootWindow.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.haarFolder = args.haarFolder
        self.outputWidth = args.outputWidth
        self.rootWindow.title('Face Identification App')
        self.rootWindow.geometry('1000x700+440+0')

        self.mainFrame = Frame(self.rootWindow)
        im = Image.open('resources/background00.jpg')
        self.bgImage = ImageTk.PhotoImage(im)
        bgImageLabel = Label(self.mainFrame, image=self.bgImage)
        bgImageLabel.place(x=0, y=0)
        self.mainFrame.pack(fill=BOTH, expand=YES)

        self.buildLeftFrame()
        self.buildRightFrame()

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

    def buildLeftFrame(self):
        self.leftFrame = Frame(self.mainFrame)
        self.leftFrame.configure(background="black", padx=3, pady=3)

        rowCount = 0

        self.subjectPictureLabel = Label(self.leftFrame)
        self.subjectPictureLabel.grid(row=rowCount, column=0)
        rowCount += 1

        labelFont = tkFont.Font(family='Arial', size=30)
        self.subjectNameLabel = Label(self.leftFrame)
        self.subjectNameLabel.configure(font=labelFont, bg='black', fg='white')
        self.subjectNameLabel.grid(row=rowCount, column=0)
        rowCount += 1

        self.buildSubjectDataFrame(self.leftFrame, rowCount)
        rowCount += 1

        self.webPictureLabel = Label(self.leftFrame, height=200, width=200)
        self.webPictureLabel.grid(row=rowCount, column=0)
        rowCount += 1

        self.leftFrame.pack(side=LEFT)

    def buildRightFrame(self):
        self.rightFrame = Frame(self.mainFrame)
        self.rightFrame.configure(background="black", padx=3, pady=3)
        self.listFacesLabel = Label(self.rightFrame)
        self.listFacesLabel.config(borderwidth=0)
        self.listFacesLabel.pack(side=TOP)

        self.rightFrame.pack(side=RIGHT)

    def buildSubjectDataFrame(self, container, rowCount):
        self.subjectDataFrame = Frame(container)

        self.addSubjectField('Twitter account:', 'cimarronytabaco', 0)
        self.addSubjectField('Nombre:', 'Jota', 1)
        self.addSubjectField('Followers:', '45', 2)
        self.addSubjectField('Following:', '50', 3)

        self.subjectDataFrame.grid(row=rowCount, column=0)

    def addSubjectField(self, name, value, row):
        Label(self.subjectDataFrame, text=name).grid(row=row, column=0)
        self.nameLabel = Label(self.subjectDataFrame, text=value, relief=RIDGE, width=20)
        self.nameLabel.grid(row=row, column=1)

    def checkPendingWork(self):
        """
        Check every 500 ms if there is something new in the queue.
        """
        if not self.subjectsQueue.empty():
            logging.info('Subjects queue is not empty!')
            name, email, img = self.newSubjectHandler.newSubject(self.subjectsQueue.get())

            self.showDetectedSubject(name, img)
            self.showCollectedFaces()
            self.launchSearch(name, email)

        self.rootWindow.after(500, self.checkPendingWork)

    def showDetectedSubject(self, name, image):
        if image is not None:
            self.subjectImage = convertImageCVToTk(image)
            self.subjectPictureLabel.configure(image=self.subjectImage)
            self.subjectPictureLabel.pack()

        if name is not None:
            self.subjectNameLabel.configure(text=name.title())
            self.subjectNameLabel.pack()

    def showCollectedFaces(self):
        pos = randint(0, len(self.faces) - 1)
        img = self.faces[pos]
        outputSize = calculateScaledSize(int(self.outputWidth / 2), image=img)
        outputImage = cv2.resize(img, outputSize)

        self.randomSubjectImage = convertImageCVToTk(outputImage)
        self.listFacesLabel.configure(image=self.randomSubjectImage)
        self.listFacesLabel.pack()

        self.rootWindow.after(100, self.showCollectedFaces)

    def launchSearch(self, name, email):
        result = searchFullContact(email)

        self.webPicturesFound = getList(result, 'photos')
        self.webPicturesIndex = 0
        self.rotateWebPicture()

        self.showWebPages(result)

    def rotateWebPicture(self):
        if self.webPicturesIndex < len(self.webPicturesFound):
            photo = self.webPicturesFound[self.webPicturesIndex]

            if 'url' in photo:
                req = urllib2.urlopen(photo.get('url'))
                b64_data = base64.encodestring(req.read())
                self.currentWebPicture = ImageTk.PhotoImage(data=b64_data)
                req.close()

                self.webPictureLabel.configure(image=self.currentWebPicture)
                self.webPictureLabel.pack()

            self.webPicturesIndex += 1
            self.rootWindow.after(2000, self.rotateWebPicture)

        elif self.webPicturesIndex > 0:
            self.webPicturesIndex = 0
            self.rootWindow.after(2000, self.rotateWebPicture)

    def showWebPages(self, result):
        for profile in getList(result, 'socialProfiles'):
            print(profile.get('type'))
            print(profile.get('username'))

            if 'followers' in profile:
                print(profile.get('followers'))

            if 'following' in profile:
                print(profile.get('following'))

            if 'url' in profile:
                webbrowser.open_new(profile.get('url'))

            if 'bio' in profile:
                print(profile.get('bio'))

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
