import threading


class StoppableThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """

    def __init__(self, faces, outputWidth):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()
        self.listFacesWindow = "Buscando en la base de datos..."
        self.faces = faces
        self.outputWidth = outputWidth

    def run(self):
        pass

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
