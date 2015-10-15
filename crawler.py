#!/usr/bin/python

import logging, argparse, urllib2, pyttsx
import common

from BeautifulSoup import BeautifulSoup
from facepy import GraphAPI


def ConfigureArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('name', help="Name to search the web.")
  parser.add_argument('--log', help="Log level for logging.", default="WARNING")
  return parser.parse_args()


def parseCuit(cuit):
  if (len(cuit) == 11):
    return (cuit[0:2], cuit[2:10], cuit[10:])


def main():
  args = ConfigureArguments()
  common.ConfigureLogging(args.log)

  logging.info("Starting web crawler")

  baseUrl = "http://www.buscar-cuit.com"

  q = args.name.replace(" ", "+")

  engine = pyttsx.init()
  engine.setProperty('voice', "spanish-latin-american")
  
  page = urllib2.urlopen("{0}?q={1}&view=resultados".format(baseUrl, q))
  soup = BeautifulSoup(page)

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
      engine.say(dni)
      engine.say(digitoVerificador)

      logging.debug("Running engine to speak...")
      engine.runAndWait()
      logging.debug("Speak finished.")

  
  access_token = ''
  graph = GraphAPI(access_token)
  result = graph.search(q, 'user')
  print result

  logging.info('END web crawler')
#end main

#----------
# M A I N
#----------
if __name__ == '__main__':
  main()