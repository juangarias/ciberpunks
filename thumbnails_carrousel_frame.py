import logging
import threading
from PIL import ImageTk
import tkFont
import Tkinter as tk
from web_data_iterator import ThumbnailsIterator

CARROUSEL_ROTATION_DELAY = 1000


class ThumbnailsCarrouselFrame(tk.Frame):

    def __init__(self, parent, size, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.size = size
        self.fontFamily = 'System'
        self.config(bg='black', bd=0)
        self.emptyIcon = ImageTk.PhotoImage(file='resources/empty16x16.png')
        self.emptyThumbnail = ImageTk.PhotoImage(file='resources/empty60x60.png')

        self.createWidgets()
        self.initialize()

    def createWidgets(self):
        labelFont = tkFont.Font(family=self.fontFamily, size=9)
        self.thumbnailsLabels = []
        self.iconsLabels = []
        self.descLabels = []

        for i in xrange(self.size):
            f = tk.Frame(self, bg='black', bd=0, padx=10)
            self.iconsLabels.append(tk.Label(f, bd=0, bg='white'))
            self.descLabels.append(tk.Label(f, bd=0, bg='white', fg='black', font=labelFont))
            self.thumbnailsLabels.append(tk.Label(f, bd=0))
            f.grid(row=0, column=i)

    def initialize(self):
        self.iconsTkImages = [None] * self.size
        self.thumbnailsTkImages = [None] * self.size
        self.descriptions = [None] * self.size
        self.rotateHandler = -1
        self.workerThread = None

        map((lambda l: l.config(text='')), self.descLabels)

    def start(self, thumbnails):
        logging.debug('Starting carrousel of thumbnails in thread {0}...'.format(threading.current_thread().ident))
        logging.debug('Carrousel of thumbnails count {0}'.format(len(thumbnails)))
        self.thumbnails = thumbnails
        self.thumbnailsIterator = ThumbnailsIterator(self.thumbnails)
        self.rotate()

    def stop(self):
        if self.isWorkingInBackground():
            self.workerThread.join()
        self.after_cancel(self.rotateHandler)
        self.initialize()

    def rotate(self):
        if self.isWorkingInBackground():
            self.workerThread.join()

        logging.debug('Rotating thumbnails in thread {0}...'.format(threading.current_thread().ident))
        self.thumbnailsTkImages.pop(0)
        self.thumbnailsTkImages.append(None)
        self.iconsTkImages.pop(0)
        self.iconsTkImages.append(None)
        self.descriptions.pop(0)
        self.descriptions.append('')

        for i in xrange(0, self.size - 2):
            self.showThumbnail(i)

        self.workerThread = threading.Thread(target=self.displayNextThumbnail)
        self.workerThread.start()

        # For windows, to avoid using threads
        # self.displayNextThumbnail()

    def isWorkingInBackground(self):
        return self.workerThread is not None and self.workerThread.is_alive()

    def displayNextThumbnail(self):
        logging.debug('Displaying netxt thumbnail in thread {0}...'.format(threading.current_thread().ident))
        if self.thumbnailsIterator.hasNext():
            icon, description, image = self.thumbnailsIterator.next()
            lastIndex = self.size - 1

            self.iconsTkImages[lastIndex] = ImageTk.PhotoImage(icon) if icon is not None else self.emptyIcon
            self.descriptions[lastIndex] = self.extractDisplayDescription(description)
            self.thumbnailsTkImages[lastIndex] = ImageTk.PhotoImage(image) if image is not None else self.emptyThumbnail

            self.showThumbnail(lastIndex)

        self.rotateHandler = self.after(CARROUSEL_ROTATION_DELAY, self.rotate)

    def extractDisplayDescription(self, description):
        if description is None:
            return ''

        sp = description.split('-')
        if len(sp) > 1:
            return sp[1].strip()
        else:
            return description

    def showThumbnail(self, i):
        try:
            iconLabel = self.iconsLabels[i]
            iconLabel.configure(image=self.iconsTkImages[i])
            iconLabel.grid(row=0, column=0)

            descLabel = self.descLabels[i]
            descLabel.configure(text=self.descriptions[i])
            descLabel.grid(row=0, column=1)

            thumbLabel = self.thumbnailsLabels[i]
            thumbLabel.configure(image=self.thumbnailsTkImages[i])
            thumbLabel.grid(row=1, column=0, columnspan=2)
        except:
            pass
