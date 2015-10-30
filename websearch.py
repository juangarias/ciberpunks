# coding=utf-8
import logging
import urllib2
from dataFullContactJSON import getDataFeo
from bs4 import BeautifulSoup
from httplib import IncompleteRead


def parseCuit(cuit):
    if (len(cuit) == 11):
        return (cuit[0:2], cuit[2:10], cuit[10:])


def searchBuscarCUIT(name):
    q = name.replace(' ', '+')
    url = 'http://www.buscar-cuit.com/?q={0}'.format(q)

    logging.debug('Trying to search {0}'.format(url))
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    # logging.debug('Search return OK {0}.'.format(soup.prettify()))

    webResults = soup.findAll('div', {'class': 'results'})
    subjects = []

    # logging.debug('Found {0} results for query.')

    for divResults in webResults:
        divs = divResults.findAll('div')

        for i in xrange(0, len(divs), 2):
            name = divs[i].a.string
            cuit = divs[i + 1].string.replace('CUIT: ', '')
            logging.info('Sujeto encontrado: [{0}] - CUIT [{1}]'.format(name, cuit))

            cuitPre, dni, digitoVerificador = parseCuit(cuit)

            subjects.append((name, cuitPre, dni, digitoVerificador))

    return subjects


def searchFullContact(email):
    # fullContactKey = '472aa9326ee7548'
    # fullContactURL = 'https://api.fullcontact.com/v2/person.json?email={0}&apiKey={1}'
    # response = json.load(urllib2.urlopen(fullContactURL.format(email, fullContactKey)))
    response = getDataFeo()

    return response


def searchPipl(email):
    url = 'https://pipl.com/search/?q={0}&l=argentina&sloc=&in=5'.format(email)
    page = urllib2.urlopen(url)

    try:
        soup = BeautifulSoup(page, 'html.parser')
        # logging.debug('Search return OK {0}.'.format(soup.prettify()))

        webResults = soup.find_all('div', class_='line1 truncate')
        links = map(extractSanitizedResultLink, webResults)
        linksGrouped = groupSimilarLinks(links)

        webResults = soup.find_all('img', class_='thumbnail single_person hidden')
        thumbnailsFull = map((lambda img: img['src']), webResults)
        thumbnails = filter((lambda imgSrc: not imgSrc.startswith('/static')), thumbnailsFull)

        profile = extractProfile(soup)

        return thumbnails, linksGrouped, profile

    except IncompleteRead as e:
        logging.exception('Incomplete read getting data from pipl.com', e)
        return [], [], dict()


def getList(response, key):
    if response.get(key):
        return response.get(key)
    else:
        return []


def extractSanitizedResultLink(div):
    stripped = div.string.strip()

    if not stripped.startswith('http://'):
        stripped = 'http://' + stripped

    return stripped


def groupSimilarLinks(links):
    categories = ['twitter.com', 'facebook.com', 'linkedin', 'youtube.com', 'picasaweb']

    groupedLinks = [(filterBy, [l for l in links if filterBy in l]) for filterBy in categories]
    others = [('others', [l for l in links if not any(filterBy in l for filterBy in categories)])]
    return filter((lambda (cat, links): len(links) > 0), groupedLinks + others)


def extractProfile(soup):
    profile = dict()
    profileDiv = soup.find('div', {'id': 'profile_container_middle'})
    if profileDiv:
        for row in profileDiv.find_all('div', class_='row group'):
            fieldLabelDiv = row.find('div', class_='field_label')
            valuesDiv = row.find('div', class_='values')

            fieldKey = ''
            fieldValue = ''

            for s in fieldLabelDiv.stripped_strings:
                fieldKey = s

            fieldKey = fieldKey.strip().replace(':', '').lower()

            for li in valuesDiv.find_all('li'):
                if li.string is not None:
                    fieldValue += ' ' + li.string.strip().encode('utf-8')
                elif li.a is not None:
                    fieldValue += ' ' + li.a.string.strip().encode('utf-8')

            profile[fieldKey] = fieldValue

    return profile
