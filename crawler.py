#!/usr/bin/python
# coding=utf-8

import logging, argparse, urllib2, pyttsx, json, webbrowser
import pyinotify
from BeautifulSoup import BeautifulSoup
from facepy import GraphAPI
from common import configureLogging, decodeSubjectPictureName


def configureArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--newSubjectsFolder', help="Foder containing new faces files.", 
    default='/home/juan/ciberpunks/faces/news')
  parser.add_argument('--log', help="Log level for logging.", default="WARNING")
  return parser.parse_args()


class NewSubjectDetectedEventHandler(pyinotify.ProcessEvent):

  def newSubject(self, filename):
    name, email = decodeSubjectPictureName(filename)
    searchBuscarCUIT(name)
    searchFullContact(email)
    searchPipl(email)

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
  baseUrl = "http://www.buscar-cuit.com"

  q = name.replace(" ", "+")

  page = urllib2.urlopen("{0}?q={1}&view=resultados".format(baseUrl, q))
  soup = BeautifulSoup(page)

  engine = pyttsx.init()
  engine.setProperty('voice', "spanish-latin-american")

  for divResults in soup.findAll("div", { "class" : "results" }):
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
  #fullContactKey = '472aa9326ee7548'
  #fullContactURL = 'https://api.fullcontact.com/v2/person.json?email={0}&apiKey={1}'
  #response = json.load(urllib2.urlopen(fullContactURL.format(email, fullContactKey)))

  response = json.loads("""
  {
    "status" : 200, "requestId" : "d460b77f-cf9e-4576-b534-6209304f6c8a", "likelihood" : 0.88,
    "photos" : [ {"type" : "twitter", "typeId" : "twitter", "typeName" : "Twitter",
      "url" : "https://d2ojpxxtu63wzl.cloudfront.net/static/0e3bb7f79f1bb1c9653dd746a6ca0f37_ca0c4be442587a4a91067992a267dd077cb58ad1ed00f1ceaefb7e61eeae0f35",
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

  """"socialProfiles": 
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

  for photo in response['photos']:
    if 'url' in photo:
      webbrowser.open_new(photo.get('url'))


  for profile in response['socialProfiles']:
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


def searchPipl(email):
  url = "https://pipl.com/search/?q={0}&l=argentina&sloc=&in=5".format(email)
  webbrowser.open(url)


def main():
  args = configureArguments()
  configureLogging(args.log)
  logging.info("Starting web crawler")

  try:
    logging.debug('Creating custom event handler...')
    handler = NewSubjectDetectedEventHandler()

    wm = pyinotify.WatchManager() 
    eventsFlag = pyinotify.IN_MOVED_TO | pyinotify.IN_CREATE

    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch(args.newSubjectsFolder, eventsFlag)

    logging.debug('Starting notifier infinite loop...')
    notifier.loop()
  except KeyboardInterrupt:
    pass

  logging.info('END web crawler')
#end main

#----------
# M A I N
#----------
if __name__ == '__main__':
  main()