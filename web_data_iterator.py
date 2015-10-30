import logging
import urllib2
from PIL import Image
from io import BytesIO
from exceptions import StopIteration


class WebDataIterator(object):

    def __init__(self, webData):
        self.data = webData
        self.index = 0
        self.count = len(self.data)

    def hastNext(self):
        return self.index < self.count

    def next(self):
        if not self.hastNext():
            raise StopIteration

        data = self.internalNext()

        self.index += 1

        if self.hasReachedEnd():
            logging.debug('No more data. Restart counter.')
            self.reset()

        return data

    def hasReachedEnd(self):
        return self.index == self.count

    def reset(self):
        self.index = 0


class WebPicturesIterator(WebDataIterator):

    def __init__(self, webPictures):
        super(self.__class__, self).__init__(webPictures)
        self.cache = []

    def internalNext(self):
        if self.imageInCache():
            image = self.cache[self.index]
        else:
            photo = self.data[self.index]
            image = None

            if 'url' in photo:
                try:
                    url = photo.get('url')
                    logging.debug('Trying get image from {0}...'.format(url))
                    req = urllib2.urlopen(url)
                    if req is not None:
                        image = Image.open(BytesIO(req.read()))
                        req.close()
                        logging.debug('Image downloaded OK.')
                    else:
                        logging.warning('Call to urllib2.urlopen returned None.')
                except urllib2.URLError as e:
                    logging.exception('Error getting image from URL', e)
                    pass

            self.cache.append(image)

        return image

    def imageInCache(self):
        return self.index < len(self.cache)


class SocialNetworkIterator(WebDataIterator):

    def __init__(self, socialNetworkData):
        super(self.__class__, self).__init__(socialNetworkData)

    def extractValue(self, profile, key):
        if key in profile:
            return profile.get(key)
        else:
            return ''

    def internalNext(self):
        profile = self.data[self.index]

        profileType = self.extractValue(profile, 'typeName')
        username = self.extractValue(profile, 'username')
        followers = self.extractValue(profile, 'followers')
        following = self.extractValue(profile, 'following')
        url = self.extractValue(profile, 'url')
        bio = self.extractValue(profile, 'bio')

        return profileType, username, followers, following, url, bio
