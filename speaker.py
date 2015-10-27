import os
import pyttsx


class OSXSpeaker:

    def __init__(self, voice=''):
        self.voice = voice

    def say(self, phrase):
        os.system('say ' + self.voice + ' ' + phrase)

    def runAndWait(self):
        pass


class PyTtsxSpeaker:

    def __init__(self, voice='spanish-latin-american'):
        self.engine = pyttsx.init()
        self.engine.setProperty('voice', voice)

    def say(self, phrase):
        self.engine.say(phrase)

    def runAndWait(self):
        self.engine.runAndWait()
