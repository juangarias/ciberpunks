#!/usr/bin/python
# coding=utf-8
import os
import logging
import time
import argparse
import Queue
import webbrowser
from watchdog.observers import Observer
from watchdogEventHandler import FileCreatedEventHandler
from speaker import LinuxEspeak
from common import configureLogging, decodeSubjectPictureName, getFilename
from websearch import searchPipl, searchBuscarCUIT


WEB_BROWSER_OPEN_DELAY = 6
SPANISH_VOICE = 'spanish-latin-am'


def configureArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--newSubjectsFolder', help="Foder containing new faces files.",
                        default='/home/juan/')
    parser.add_argument('--log', help="Log level for logging.", default="WARNING")
    return parser.parse_args()


class NewSubjectDetectedEventHandler():

    def newSubject(self, picturePath):
        filename = getFilename(picturePath)
        name, email = decodeSubjectPictureName(filename)
        # doFullContactSearch(email)
        doBuscarCUITSearch(name)
        doPiplSearch(email)

    def process_IN_CREATE(self, event):
        logging.debug("File {0}".format(event.pathname))
        self.newSubject(event.pathname)

    def process_IN_MOVED_TO(self, event):
        logging.debug("File {0}".format(event.pathname))
        self.newSubject(event.pathname)


def doBuscarCUITSearch(name):
    subjects = searchBuscarCUIT(name)

    engine = LinuxEspeak(SPANISH_VOICE)

    # only say 3 (three) subjects if we found more
    lastElem = len(subjects) -1 if len(subjects) <= 3 else 3

    for i in xrange(lastElem):
        name, cuitPre, dni, digitoVerificador = subjects[i]
        logging.info("Sujeto encontrado: [{0}] - CUIT [{1}-{2}-{3}]".format(name, cuitPre, dni, digitoVerificador))

        logging.debug("Queueing words to say...")
        engine.say("Sujeto encontrado")
        engine.say(name)
        engine.say("CUIT")
        engine.say(cuitPre)
        engine.say("guión")
        engine.say(dni)
        engine.say("guión")
        engine.say(digitoVerificador)

        logging.debug("Running engine to speak...")

    engine.runAndWait()
    logging.debug("Speak finished.")


'''
def doFullContactSearch(email):
    response = searchFullContact(email)

    for photo in getList(response, 'photos'):
        if 'url' in photo:
            req = urllib2.urlopen(photo.get('url'))
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            image = cv2.imdecode(arr, -1)  # 'load it as it is'

            if validImage(image):
                cv2.imshow('lalala', image)
                cv2.waitKey(200)

    for profile in getList(response, 'socialProfiles'):
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
'''


def doPiplSearch(email):
    os.system('pkill firefox')
    _, groupedLinks, profile = searchPipl(email)

    speaker = LinuxEspeak(SPANISH_VOICE)
    safeSay(speaker, profile, 'career', 'Experiencia laboral')
    safeSay(speaker, profile, 'education', 'Estudios')
    safeSay(speaker, profile, 'location', 'País')
    safeSay(speaker, profile, 'usernames', 'Nombres de usuario')
    safeSay(speaker, profile, 'associated with', 'En contacto con')

    print groupedLinks

    for i in xrange(2):
        for (category, subjectLinks) in groupedLinks:
            if category != 'twitter.com':
                for link in subjectLinks:
                    # logging.debug('Trying to open link {0}'.format(link))
                    webbrowser.open(link)
                    time.sleep(WEB_BROWSER_OPEN_DELAY)

    os.system('pkill firefox')


def safeSay(speaker, profile, key, title):
    if key in profile:
        speaker.say(title)
        speaker.say(profile.get(key, ''))


def main():
    args = configureArguments()
    configureLogging(args.log)
    logging.info("Starting web crawler")

    subjectsQueue = Queue.Queue()
    newSubjectHandler = NewSubjectDetectedEventHandler()

    try:
        logging.debug('Creating custom event handler...')
        handler = FileCreatedEventHandler(subjectsQueue)
        observer = Observer()
        observer.schedule(handler, args.newSubjectsFolder)
        observer.start()

        logging.debug('Starting notifier infinite loop...')
        while True:
            if not subjectsQueue.empty():
                newSubjectHandler.newSubject(subjectsQueue.get())

            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    logging.info('END web crawler gracefully.')
# end main

# ----------
# M A I N
# ----------
if __name__ == '__main__':
    main()
