import logging
import pyinotify


def startPyInotify(newSubjectsFolder, haarFolder, outputWidth):
    logging.debug('Creating custom event handler...')
    handler = None  # NewFaceDetectedEventHandler(mainWindow, listFacesWindow, faces, haarFolder, outputWidth)

    wm = pyinotify.WatchManager()
    eventsFlag = pyinotify.IN_MOVED_TO | pyinotify.IN_CREATE

    notifier = pyinotify.Notifier(wm, handler)
    wm.add_watch(newSubjectsFolder, eventsFlag)

    logging.debug('Starting notifier infinite loop...')
    notifier.loop()


class FileCreatedEventHandler(pyinotify.ProcessEvent):

    def __init__(self, newSubjectHandler):
        self.newSubjectHandler = newSubjectHandler

    def process_IN_CREATE(self, event):
        logging.debug("File {0}".format(event.pathname))
        self.stopThread()
        self.newSubjectHandler.newSubject(event.pathname)

    def process_IN_MOVED_TO(self, event):
        logging.debug("File {0}".format(event.pathname))
        self.stopThread()
        self.newSubjectHandler.newSubject(event.pathname)
