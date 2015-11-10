#!/usr/bin/python
# coding=utf-8
import argparse
import logging
import Queue
from PIL import Image
from random import randint
import cv2
import tkFont
import Tkinter as tk
from PIL.ImageTk import PhotoImage
from watchdog.observers import Observer
from watchdogEventHandler import FileCreatedEventHandler
from common import *
from websearch import searchFullContact, searchPipl, getList
from subjectHandler import NewSubjectDetectedEventHandler
from web_data_iterator import WebPicturesIterator, SocialNetworkIterator
from thumbnails_carrousel_frame import ThumbnailsCarrouselFrame
from face_ui_frames import AlertPopup


DISPLAY_ALARM_DELAY = 30000
TOGGLE_ALARM_DELAY = 250
MAX_TOGGLE_ALAM_COUNT = 41
CHECK_PENDING_WORK_DELAY = 2000
ROTATE_WEB_PICTURE_DELAY = 2000


def configureArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--facesFolder', help="Foder containing all faces files.",
                        default='c:/Users/admin/ciberpunks/faces/att_database')
    parser.add_argument('--newSubjectsFolder', help="Foder containing new faces files.",
                        default='c:/Users/admin/ciberpunks/faces/news')
    parser.add_argument('--haarFolder', help="Folder containing HAAR cascades.",
                        default='c:/Users/admin/ciberpunks/opencv-2.4.11/sources/data/haarcascades')
    parser.add_argument('--outputWidth', help='Output with for images to display in windows.',
                        type=int, default="500")
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

        height = int(self.rootWindow.winfo_screenheight() * 0.9)
        width = int(self.rootWindow.winfo_screenwidth() * 0.85)
        self.top = 0
        self.left = self.rootWindow.winfo_screenwidth() - width - 10

        self.rootWindow.title('Face Identification App')
        self.rootWindow.geometry('{0}x{1}+{2}+{3}'.format(width, height, self.left, self.top))
        self.rootWindow.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.haarFolder = args.haarFolder
        self.outputWidth = args.outputWidth
        self.facesFolder = ['c:/Users/admin/ciberpunks/faces/att_database', 'c:/Users/admin/ciberpunks/faces/news']
        self.fontFamily = 'System'

        self.mainFrame = self.buildMainFrame()

        contentFrame = tk.Frame(self.mainFrame, bg='black', bd=0)
        self.leftFrame = self.buildLeftFrame(contentFrame)
        self.rightFrame = self.buildRightFrame(contentFrame)
        contentFrame.pack(side=tk.TOP)

        self.thumbnailsCarrousel = ThumbnailsCarrouselFrame(self.mainFrame, 8)
        self.thumbnailsCarrousel.pack(side=tk.BOTTOM, pady=100)

        self.alertPopup = None

        self.loadFaces()

        logging.debug('Creating new subject handler...')
        self.newSubjectHandler = NewSubjectDetectedEventHandler(self.haarFolder, self.outputWidth)

        self.subjectsQueue = Queue.Queue()
        handler = FileCreatedEventHandler(self.subjectsQueue)

        logging.debug('Creating observer for watchdog...')
        self.observer = Observer()
        self.observer.schedule(handler, args.newSubjectsFolder)
        self.observer.start()

        self.checkPendingWork()

    def loadFaces(self):
        logging.debug('Loading faces from disk...')
        [self.faces, _, _] = readImages(self.facesFolder)
        logging.debug('Faces loaded.')

    def buildMainFrame(self):
        f = tk.Frame(self.rootWindow)
        im = Image.open('resources/background00.jpg')
        self.bgImage = PhotoImage(im)
        bgImageLabel = tk.Label(f, image=self.bgImage, bd=0)
        bgImageLabel.place(x=0, y=0)
        f.pack(fill=tk.BOTH, expand=tk.YES)
        return f

    def buildLeftFrame(self, container):
        f = tk.Frame(container)
        f.configure(background="black", padx=5, pady=5)

        rowCount = 0
        self.subjectPictureLabel = tk.Label(f, bd=0)
        self.subjectPictureLabel.grid(row=rowCount, column=0)
        rowCount += 1

        labelFont = tkFont.Font(family=self.fontFamily, size=26)
        self.subjectNameLabel = tk.Label(f)
        self.subjectNameLabel.configure(font=labelFont, bg='black', fg='white')
        self.subjectNameLabel.grid(row=rowCount, column=0)
        rowCount += 1

        self.buildSubjectDataFrame(f)
        self.subjectDataFrame.grid(row=rowCount, column=0)
        rowCount += 1

        f.pack(side=tk.LEFT)
        return f

    def buildRightFrame(self, container):
        f = tk.Frame(container)
        f.configure(background="black", padx=5, pady=5)
        self.listFacesLabel = tk.Label(f)
        self.listFacesLabel.config(borderwidth=0)
        self.listFacesLabel.pack(side=tk.TOP)

        #self.webPictureLabel = tk.Label(f, height=200, width=200, bd=0, bg='black')
        #self.webPictureLabel.pack(side=tk.BOTTOM)

        f.pack(side=tk.RIGHT)
        return f

    def buildSubjectDataFrame(self, container):
        self.subjectDataFrame = tk.Frame(container)

        self.snType = self.addSubjectField(self.subjectDataFrame, 'Social network:', '', 0)
        self.snUsername = self.addSubjectField(self.subjectDataFrame, 'Username:', '', 1)
        self.snFollowers = self.addSubjectField(self.subjectDataFrame, 'Followers:', '', 2)
        self.snFollowing = self.addSubjectField(self.subjectDataFrame, 'Following:', '', 3)
        self.snURL = self.addSubjectField(self.subjectDataFrame, 'URL:', '', 4)
        self.snBio = self.addSubjectField(self.subjectDataFrame, 'Bio:', '', 5)

    def addSubjectField(self, container, name, value, row):
        labelFont = tkFont.Font(family=self.fontFamily, size=12)

        descLabel = tk.Label(container, text=name, bg='black', fg='white', font=labelFont)
        descLabel.grid(row=row, column=0, sticky=tk.W + tk.E + tk.N + tk.S)

        label = tk.Label(container, text=value, relief=tk.RIDGE, width=30, bg='black', fg='white', bd=0, font=labelFont)
        label.grid(row=row, column=1, sticky=tk.W + tk.E + tk.N + tk.S)

        return label

    def checkPendingWork(self):
        if self.subjectsQueue.empty():
            # Check every configured ms if there is something new in the queue.
            self.rootWindow.after(CHECK_PENDING_WORK_DELAY, self.checkPendingWork)
        else:
            self.thumbnailsCarrousel.stop()
            self.closeAlarmAlert()
            logging.info('New subject found!')
            name, email, img = self.newSubjectHandler.newSubject(self.subjectsQueue.get())

            self.showDetectedSubject(name, img)
            self.showCollectedFaces()
            self.launchSearch(name, email)
            self.rootWindow.after(DISPLAY_ALARM_DELAY, self.showAlarm)

    def closeAlarmAlert(self):
        self.changeSubjectFramesColor('black')

    def showAlarm(self):
        self.alertPopup = AlertPopup(-800, 0)
        self.toggleAlarmCount = 0
        self.toggleAlarm()

    def toggleAlarm(self):
        if self.toggleAlarmCount == MAX_TOGGLE_ALAM_COUNT:
            self.rootWindow.after(CHECK_PENDING_WORK_DELAY, self.checkPendingWork)
        else:
            color = 'red' if self.toggleAlarmCount % 2 == 0 else 'black'
            self.changeSubjectFramesColor(color)
            self.toggleAlarmCount += 1
            self.rootWindow.after(TOGGLE_ALARM_DELAY, self.toggleAlarm)

    def changeSubjectFramesColor(self, color):
        self.leftFrame.config(bg=color)
        self.leftFrame.pack()
        self.subjectDataFrame.config(bg=color)
        self.subjectDataFrame.grid()

        fgColor = 'black' if color == 'red' else 'white'

        self.subjectNameLabel.configure(bg=color, fg=fgColor)
        self.subjectNameLabel.grid()

        for w in self.subjectDataFrame.winfo_children():
            w.configure(bg=color, fg=fgColor)
            w.grid()

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
        if len(self.faces) <= 0:
            return

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

        photoUrls = [photo.get('url', '') for photo in getList(result, 'photos')]
        thumbnails, _, profile = searchPipl(email)

        if 'mainPicture' in profile:
            photoUrls.append(profile.get('mainPicture'))

        # self.webPicturesIterator = WebPicturesIterator(photoUrls)
        self.webPicturesIterator = WebPicturesIterator([])
        # self.socialNetworkIterator = SocialNetworkIterator(getList(result, 'socialProfiles'))
        self.socialNetworkIterator = SocialNetworkIterator([])
        self.rotateWebData()

        twitterThumbs = [t for t in thumbnails if 'twitter.com' in t[2]]
        others = [t for t in thumbnails if 'twitter.com' not in t[2]]

        self.thumbnailsCarrousel.start(twitterThumbs[:2] + others)

    def rotateWebData(self):
        size = 200, 200
        rotate = False

        logging.debug('Trying to iterate web image...')
        if self.webPicturesIterator.hasNext():
            logging.debug('Next image found!')
            image = self.webPicturesIterator.next()
            if image is not None:
                # TODO: keep ratio when resizing image.- jarias
                image = image.resize(size)
                self.currentWebPicture = PhotoImage(image)
                self.webPictureLabel.configure(image=self.currentWebPicture)
                self.webPictureLabel.pack()
            rotate = True
        else:
            logging.debug('No images detected.')

        logging.debug('Trying to iterate social network...')
        if self.socialNetworkIterator.hasNext():
            logging.debug('Next social network found!')
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

        self.leftFrame.pack()

        if rotate:
            self.rootWindow.after(ROTATE_WEB_PICTURE_DELAY, self.rotateWebData)

    def on_closing(self):
        logging.debug('Trying to exit FaceIDApp...')
        self.closeAlarmAlert()
        self.thumbnailsCarrousel.stop()
        self.observer.stop()
        self.observer.join()
        self.rootWindow.destroy()
        logging.info('Exit FaceIDApp gracefully.')


def main():
    args = configureArguments()
    configureLogging(args.log)
    logging.info('Starting face ID UI...')

    logging.debug('Initializing Graphical UI...')
    rootWindow = tk.Tk()
    FaceIDApp(rootWindow, args)

    logging.debug('Start the GUI')
    rootWindow.mainloop()
# end main

if __name__ == '__main__':
    main()
