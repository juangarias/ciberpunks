# coding=utf-8
import logging
import urllib2
import json
import webbrowser
from bs4 import BeautifulSoup


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

    webResults = soup.findAll("div", {"class": "results"})
    subjects = []

    logging.debug('Found {0} results for query.')

    for divResults in webResults:
        divs = divResults.findAll("div")

        for i in xrange(0, len(divs), 2):
            name = divs[i].a.string
            cuit = divs[i + 1].string.replace("CUIT: ", "")
            logging.info("Sujeto encontrado: [{0}] - CUIT [{1}]".format(name, cuit))

            cuitPre, dni, digitoVerificador = parseCuit(cuit)

            subjects.append((name, cuitPre, dni, digitoVerificador))

    return subjects


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

    return response


def getList(response, key):
    if response.get(key):
        return response.get(key)
    else:
        return []


def searchPipl(email):
    url = "https://pipl.com/search/?q={0}&l=argentina&sloc=&in=5".format(email)
    webbrowser.open(url)
