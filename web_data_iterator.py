import logging
import urllib2
from PIL import Image
from io import BytesIO
from exceptions import StopIteration


class WebDataIterator(object):

    def __init__(self, items):
        self.data = items
        self.index = 0
        self.count = len(self.data)

    def hasNext(self):
        return self.index < self.count

    def next(self):
        if not self.hasNext():
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

    def __init__(self, items):
        super(WebPicturesIterator, self).__init__(items)
        self.cache = []

    def internalNext(self):
        if self.elementInCache():
            element = self.cache[self.index]
        else:
            item = self.data[self.index]
            element = self.buildElement(item)

            # If an error occurs append None in the cache anyway, to keep the synchro with index.- jarias
            self.cache.append(element)

        return element

    def buildElement(self, photoUrl):
        image = None

        try:
            logging.debug('Trying download image from {0}...'.format(photoUrl))
            req = urllib2.urlopen(photoUrl)
            if req is not None:
                image = Image.open(BytesIO(req.read()))
                req.close()
                logging.debug('Image downloaded OK.')
            else:
                logging.warning('Call to urllib2.urlopen returned None.')
        except urllib2.HTTPError as e:
            logging.error('HTTP Error getting image from URL {0}'.format(photoUrl))
            logging.error('HTTP Error message {0}'.format(e.message))
        except urllib2.URLError as e:
            logging.error('Error getting image from URL {0}'.format(photoUrl))
            logging.error('Error message {0}'.format(e.message))
        finally:
            return image

    def elementInCache(self):
        return self.index < len(self.cache)


class ThumbnailsIterator(WebPicturesIterator):

    def __init__(self, items):
        super(ThumbnailsIterator, self).__init__(items)

    def buildElement(self, thumbnail):
        iconUrl, description, photoUrl = thumbnail

        icon = super(ThumbnailsIterator, self).buildElement(iconUrl)
        image = super(ThumbnailsIterator, self).buildElement(photoUrl)

        return icon, description, image


class SocialNetworkIterator(WebDataIterator):

    def __init__(self, socialNetworkData):
        super(SocialNetworkIterator, self).__init__(socialNetworkData)

    def getValue(self, profile, key):
        value = ''
        if key in profile:
            value = profile.get(key)
            if isinstance(value, basestring):
                logging.debug('Removing special chars from {0}'.format(value))
                value = value.replace("\r", '').replace("\n", ' ')
                logging.debug('Result {0}'.format(value))

        return value

    def internalNext(self):
        profile = self.data[self.index]

        profileType = self.getValue(profile, 'typeName')
        username = self.getValue(profile, 'username')
        followers = self.getValue(profile, 'followers')
        following = self.getValue(profile, 'following')
        url = self.getValue(profile, 'url')
        bio = self.getValue(profile, 'bio')

        return profileType, username, followers, following, url, bio
