#!/usr/bin/python
# coding=utf-8

import os
import logging
import time
import argparse
import Queue
import urllib2
import speaker
import json
import webbrowser
import cv2
import numpy as np
from bs4 import BeautifulSoup
from common import configureLogging, decodeSubjectPictureName, validImage

if os.name == 'posix':
    from watchdog.observers import Observer
    from watchdogEventHandler import FileCreatedEventHandler
else:
    from pyinotifyEventHandler import FileCreatedEventHandler


def configureArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--newSubjectsFolder', help="Foder containing new faces files.",
                        default='/Users/juan/faces/news')
    parser.add_argument('--log', help="Log level for logging.", default="WARNING")
    return parser.parse_args()


class NewSubjectDetectedEventHandler():

    def newSubject(self, picturePath):
        (_, filename) = os.path.split(picturePath)
        name, email = decodeSubjectPictureName(filename)
        searchBuscarCUIT(name)
        searchFullContact(email)
        # searchPipl(email)

    def process_IN_CREATE(self, event):
        logging.debug("File {0}".format(event.pathname))
        self.newSubject(event.pathname)

    def process_IN_MOVED_TO(self, event):
        logging.debug("File {0}".format(event.pathname))
        self.newSubject(event.pathname)


def parseCuit(cuit):
    if (len(cuit) == 11):
        return (cuit[0:2], cuit[2:10], cuit[10:])


def searchBuscarCUIT(name):
    q = name.replace(" ", "+")
    url = "http://www.buscar-cuit.com/?q={0}".format(q)

    logging.debug('Trying to search {0}'.format(url))
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    # logging.debug('Search return OK {0}.'.format(soup.prettify()))

    engine = speaker.OSXSpeaker('Paulina')

    results = soup.findAll("div", {"class": "results"})

    logging.debug('Found {0} results for query.')

    for divResults in results:
        divs = divResults.findAll("div")

        for i in xrange(0, len(divs), 2):
            name = divs[i].a.string
            cuit = divs[i + 1].string.replace("CUIT: ", "")
            logging.info("Sujeto encontrado: [{0}] - CUIT [{1}]".format(name, cuit))

            cuitPre, dni, digitoVerificador = parseCuit(cuit)

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


def searchFullContact(email):
    # fullContactKey = '472aa9326ee7548'
    # fullContactURL = 'https://api.fullcontact.com/v2/person.json?email={0}&apiKey={1}'
    # response = json.load(urllib2.urlopen(fullContactURL.format(email, fullContactKey)))

    response = json.loads("""
    {
      "status" : 200, "requestId" : "d460b77f-cf9e-4576-b534-6209304f6c8a", "likelihood" : 0.88,
      "photos" : [ {"type" : "twitter", "typeId" : "twitter", "typeName" : "Twitter",
        "url" : "https://d2ojpxxtu63wzl.cloudfront.net/static/0e3bb7f79f1bb1c9653dd746a6ca0f37_ca0c4be442587a4a91067992a267dd077cb58ad1ed00f1ceaefb7e61eeae0f35",
        "isPrimary" : true
      },
                  {"type" : "twitter", "typeId" : "twitter", "typeName" : "Twitter",
        "url" : "http://www.linuxtopia.org/online_books/programming_books/art_of_unix_programming/graphics/kiss.png",
        "isPrimary" : true
      } ],
      "contactInfo" : {"fullName" : "Nicolás Buttarelli"  },
      "socialProfiles" : [ {
        "type" : "klout", "typeId" : "klout", "typeName" : "Klout",
        "url" : "http://klout.com/negrobuttara", "username" : "negrobuttara",
        "id" : "242912922014324395"
        }, {"followers" : 27,    "following" : 23,    "type" : "twitter",    "typeId" : "twitter",
            "typeName" : "Twitter",    "url" : "https://twitter.com/negrobuttara",    "username" : "negrobuttara",
            "id" : "384548068"
        } ],
      "digitalFootprint" : {
        "scores" : [ {"provider" : "klout",      "type" : "general",      "value" : 12
        } ],
        "topics" : [ {"provider" : "klout",      "value" : "Twitter"    },
        {"provider" : "klout",      "value" : "Politics"},
        {"provider" : "klout",      "value" : "Buenos Aires"},
        {"provider" : "klout",      "value" : "Argentina"},
        {"provider" : "klout",      "value" : "Elections"
        } ]
      }
    }""")


    """" JSON schema of the response
    socialProfiles":
    [
      {
        "typeId": {"type":"string"},
        "typeName": {"type":"string"},
        "id": {"type":"string"},
        "username": {"type":"string"},
        "url": {"type":"string"},
        "bio": {"type":"string"},
        "rss": {"type":"string"},
        "following": {"type":"number"},
        "followers": {"type":"number"}
      }
    ],"""

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


def getList(response, key):
    if response.get(key):
        return response.get(key)
    else:
        return []


def searchPipl(email):
    url = "https://pipl.com/search/?q={0}&l=argentina&sloc=&in=5".format(email)
    webbrowser.open(url)


def main():
    args = configureArguments()
    configureLogging(args.log)
    logging.info("Starting web crawler")

    subjectsQueue = Queue.Queue()
    newSubjectHandler = NewSubjectDetectedEventHandler()

    cv2.namedWindow('lalala')

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
        cv2.destroyAllWindows()

    observer.join()
    logging.info('END web crawler gracefully.')
# end main

# ----------
# M A I N
# ----------
if __name__ == '__main__':
    main()
