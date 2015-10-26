import logging
from watchdog.events import FileSystemEventHandler


class FileCreatedEventHandler(FileSystemEventHandler):

    def __init__(self, faces, haarFolder, outputWidth, subjectsQueue):
        self.faces = faces
        self.haarFolder = haarFolder
        self.outputWidth = outputWidth
        self.subjectsQueue = subjectsQueue

    def on_created(self, event):
        logging.debug(event)
        self.subjectsQueue.put(event.src_path)
