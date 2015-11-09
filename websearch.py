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
    logging.debug('Searching pipl.com with email: [{0}]'.format(email))
    url = 'https://pipl.com/search/?q={0}&l=argentina&sloc=&in=5'.format(email)
    page = urllib2.urlopen(url)

    try:
        soup = BeautifulSoup(page, 'html.parser')
        # logging.debug('Search return OK {0}.'.format(soup.prettify()))

        linkDivs = soup.find_all('div', class_='line1 truncate')
        links = map(extractSanitizedResultLink, linkDivs)
        links = filter(None, links)

        thumbnails = []
        webResults = soup.find_all('div', class_='profile_result group')
        for result in webResults:
            div = result.find('div', class_='line2 truncate')
            img = result.find('img', class_='thumbnail single_person hidden')

            if div is not None and img is not None and not img['src'].startswith('/static'):
                description = ''
                for s in div.stripped_strings:
                    description = s

                iconUrl = 'https://pipl.com' + div.img['src']
                thumbnails.append((iconUrl, description, img['src']))

        profile = extractProfile(soup)

        return thumbnails, links, profile

    except IncompleteRead as e:
        logging.exception('Incomplete read getting data from pipl.com', e)
        return [], [], dict()


def getList(response, key):
    if response.get(key):
        return response.get(key)
    else:
        return []


def extractSanitizedResultLink(div):
    possibleLink = div.string

    if possibleLink is not None:
        stripped = possibleLink.strip()
        if not stripped.startswith('http://'):
            stripped = 'http://' + stripped

        return stripped
    else:
        return None


def groupSimilarLinks(links):
    categories = ['twitter.com', 'facebook.com', 'linkedin', 'youtube.com', 'picasaweb']

    groupedLinks = [(filterBy, [l for l in links if filterBy in l]) for filterBy in categories]
    others = [('others', [l for l in links if not any(filterBy in l for filterBy in categories)])]
    return filter((lambda (cat, links): len(links) > 0), groupedLinks + others)


def extractProfile(soup):
    profile = dict()
    logging.debug('Trying to extract profile from pipl.com search result...')

    profileTopDiv = soup.find('div', {'id': 'profile_container_top'})
    if profileTopDiv is not None:
        logging.debug('Profile top div found!')
        profileImageDiv = profileTopDiv.find('div', {'id': 'profile_image'})
        if profileImageDiv is not None and profileImageDiv.img is not None and 'src' in profileImageDiv.img:
            logging.debug('Profile_image found!')
            profile['mainPicture'] = profileImageDiv.img['src']

    profileMiddleDiv = soup.find('div', {'id': 'profile_container_middle'})
    if profileMiddleDiv is not None:
        logging.debug('Profile container middle found!')
        for row in profileMiddleDiv.find_all('div', class_='row group'):
            fieldLabelDiv = row.find('div', class_='field_label')
            valuesDiv = row.find('div', class_='values')

            fieldKey = ''
            fieldValue = ''

            if fieldLabelDiv is not None and valuesDiv is not None:
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
