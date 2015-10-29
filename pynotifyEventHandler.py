import logging
import pyinotify


def startDirectoryMonitor(newSubjectsFolder, newSubjectHandler):
    logging.debug('Creating custom event handler for pyinotify...')
    handler = FileCreatedEventHandler(newSubjectHandler)

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
