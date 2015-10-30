import os
import pyttsx


class LinuxEspeak:

    def __init__(self, voice='', speed='90'):
        self.voice = voice
        self.speed = speed

    def say(self, phrase):
        voiceParam = ''
        if self.voice:
            voiceParam = ' -v {0} '.format(self.voice)

        speedParam = ' -s {0} '.format(self.speed)

        os.system('espeak ' + voiceParam + speedParam + '"' + phrase + '"')

    def runAndWait(self):
        pass


class OSXSpeaker:

    def __init__(self, voice=''):
        self.voice = voice

    def say(self, phrase):
        voiceParam = ''
        if self.voice:
            voiceParam = ' -v {0} '.format(self.voice)

        os.system('say ' + voiceParam + phrase)

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
