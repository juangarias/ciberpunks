#!/usr/bin/python
# coding=utf-8
import argparse
import logging
import Queue
from PIL import Image
from random import randint
import cv2
import tkFont
from Tkinter import Tk, Frame, Label, BOTH, YES, LEFT, RIGHT, TOP, BOTTOM, RIDGE
from ImageTk import PhotoImage
from watchdog.observers import Observer
from watchdogEventHandler import FileCreatedEventHandler
from common import *
from websearch import searchFullContact, getList
from subjectHandler import NewSubjectDetectedEventHandler
from web_data_iterator import WebPicturesIterator, SocialNetworkIterator


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
    return PhotoImage(image=im)


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
        self.bgImage = PhotoImage(im)
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
        self.subjectPictureLabel = Label(self.leftFrame, bd=0)
        self.subjectPictureLabel.grid(row=rowCount, column=0)
        rowCount += 1

        labelFont = tkFont.Font(family='Arial', size=30)
        self.subjectNameLabel = Label(self.leftFrame)
        self.subjectNameLabel.configure(font=labelFont, bg='black', fg='white')
        self.subjectNameLabel.grid(row=rowCount, column=0)
        rowCount += 1

        self.buildSubjectDataFrame(self.leftFrame)
        self.subjectDataFrame.grid(row=rowCount, column=0)
        rowCount += 1

        self.leftFrame.pack(side=LEFT)

    def buildRightFrame(self):
        self.rightFrame = Frame(self.mainFrame)
        self.rightFrame.configure(background="black", padx=3, pady=3)
        self.listFacesLabel = Label(self.rightFrame)
        self.listFacesLabel.config(borderwidth=0)
        self.listFacesLabel.pack(side=TOP)

        self.webPictureLabel = Label(self.rightFrame, height=200, width=200, bd=0)
        self.webPictureLabel.pack(side=BOTTOM)

        self.rightFrame.pack(side=RIGHT)

    def buildSubjectDataFrame(self, container):
        self.subjectDataFrame = Frame(container)

        self.snType = self.addSubjectField('Social network:', '', 0)
        self.snUsername = self.addSubjectField('Username:', '', 1)
        self.snFollowers = self.addSubjectField('Followers:', '', 2)
        self.snFollowing = self.addSubjectField('Following:', '', 3)
        self.snURL = self.addSubjectField('URL:', '', 4)
        self.snBio = self.addSubjectField('Bio:', '', 5)

    def addSubjectField(self, name, value, row):
        Label(self.subjectDataFrame, text=name).grid(row=row, column=0)
        label = Label(self.subjectDataFrame, text=value, relief=RIDGE, width=50)
        label.grid(row=row, column=1)
        return label

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
        logging.debug('Showing detected subject {0}'.format(name))
        if name is not None:
            self.subjectNameLabel.configure(text=name.title())
            self.subjectNameLabel.grid()

        if image is not None:
            self.subjectImage = convertImageCVToTk(image)
            self.subjectPictureLabel.configure(image=self.subjectImage)
            self.subjectPictureLabel.grid()

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

        self.webPicturesIterator = WebPicturesIterator(getList(result, 'photos'))
        self.socialNetworkIterator = SocialNetworkIterator(getList(result, 'socialProfiles'))
        self.rotateWebData()

        # self.showWebPages(result)

    def rotateWebData(self):
        size = 200, 200
        rotate = False

        logging.debug('Trying to iterate web image...')
        if self.webPicturesIterator.hastNext():
            logging.debug('Next image!')
            image = self.webPicturesIterator.next()
            # TODO: keep ratio when resizing image.- jarias
            image = image.resize(size)
            self.currentWebPicture = PhotoImage(image)
            self.webPictureLabel.configure(image=self.currentWebPicture)
            self.webPictureLabel.pack()
            rotate = True
        else:
            logging.debug('No images detected.')

        logging.debug('Trying to iterate social network...')
        if self.socialNetworkIterator.hastNext():
            logging.debug('Next social network!')
            profileType, username, followers, following, url, bio = self.socialNetworkIterator.next()
            self.snType.configure(text=profileType)
            self.snType.grid(row=0, column=1)
            self.snUsername.configure(text=username)
            self.snFollowers.configure(text=followers)
            self.snFollowing.configure(text=following)
            self.snURL.configure(text=url)
            self.snBio.configure(text=bio)
            rotate = True
        else:
            logging.debug('No social networks detected.')

        self.leftFrame.pack(side=LEFT)

        if rotate:
            self.rootWindow.after(2000, self.rotateWebData)

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
