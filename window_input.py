#!/usr/bin/python
# coding=utf-8
import argparse
import logging
import os
import sys
import cv2
import paramiko
from curses import *
from common import configureLogging, encodeSubjectPictureName, calculateScaledSize, drawLabel
from multiple_ssh_client import MultipleSSHClient


TAB_KEY = 9
ENTER_KEY = 10
BACKSPACE_KEY = 263


def configureArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sshHost', help='Remote host for writing collected faces.',
                        default='192.168.1.57,192.168.1.121')
    parser.add_argument('--sshUser', help='Remote user for writing collected faces in remote host.',
                        default='juan,juan')
    parser.add_argument('--sshPassword', help='Remote password for writing collected faces in remote host.',
                        default='juancito,juancito')
    parser.add_argument('--tempLocalFolder', help='Temporary local folder for writing collected faces.',
                        default='/home/juan/ciberpunks/faces/news')
    parser.add_argument('--remoteFolder', help='Remote folder for writing collected faces.',
                        default='/')
    parser.add_argument('--outputWidth', help='Output with for images to display in windows.',
                        default="600")
    parser.add_argument('--log', help='Log level for logging.', default='WARNING')
    return parser.parse_args()


def readInput(stdscr, y, x):
    startX = x
    stdscr.move(y, x)
    value = ''
    c = stdscr.getch()

    invalidChars = list('\\ºª!|·$%/()=¡^`[]{}*+:;<>,')
    logging.debug('Key is {0}'.format(c))

    while c != ENTER_KEY and c != TAB_KEY:
        if c == BACKSPACE_KEY:
            if x > startX:
                x -= 1
                stdscr.delch(y, x)
                value = value[:-1]
            else:
                stdscr.move(y, startX)
                value = ''
        else:
            if c < 256:
                if chr(c) in invalidChars:
                    stdscr.delch(y, x)
                else:
                    value += chr(c)
                    x += 1

        c = stdscr.getch()

    logging.debug('Read from input: {0}'.format(value))
    return value


def drawInputWindow(stdscr):
    stdscr.clear()
    (h, w) = stdscr.getmaxyx()
    yPos = int(h*0.4)
    xPos = int(w*0.4)

    stdscr.addstr(yPos, xPos, "================================")
    yPos += 1
    stdscr.addstr(yPos, xPos, "|| BIENVENIDOS A CyBerSiBeriA ||")
    yPos += 1
    stdscr.addstr(yPos, xPos, "================================")
    yPos += 3

    stdscr.addstr(yPos, xPos, "Ingrese su nombre y apellido: ")
    (nameY, nameX) = stdscr.getyx()
    yPos += 1
    stdscr.addstr(yPos, xPos, "Ingrese su e-mail: ")
    (emailY, emailX) = stdscr.getyx()
    yPos += 3
    stdscr.addstr(yPos, xPos, "===== NO enviamos spam ;) =====")
    yPos += 1

    echo()
    name = readInput(stdscr, nameY, nameX)
    email = readInput(stdscr, emailY, emailX)

    return name, email


def getUserPicture(outputWidth):

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        logging.error("Arrgghhh! The camera is not working!")
        return None

    outputSize = calculateScaledSize(outputWidth, capture=camera)
    logging.debug("Reading camera...")
    readOk, image = camera.read()

    picWin = "Sonria..."
    cv2.namedWindow(picWin)

    key = -1

    while key != ENTER_KEY and readOk:
        image = cv2.resize(image, outputSize)
        drawLabel("Presione [Enter]...", image, (int(outputWidth/3), 50))
        cv2.imshow(picWin, image)
        key = cv2.waitKey(5) % 256
        readOk, image = camera.read()

    cv2.destroyWindow(picWin)
    cv2.waitKey(1)

    logging.debug('Picture taken.')

    return image


def drawThanksWindow(stdscr):
    stdscr.clear()
    (h, w) = stdscr.getmaxyx()
    yPos = int(h*0.4)
    xPos = int(w*0.4)

    stdscr.addstr(yPos, xPos, "================================")
    yPos += 1
    stdscr.addstr(yPos, xPos, "||       MUCHAS GRACIAS       ||")
    yPos += 1
    stdscr.addstr(yPos, xPos, "================================")
    yPos += 3
    stdscr.addstr(yPos, xPos, "...Por favor, presione [Enter]...")

    noecho()

    c = 0
    while c != ENTER_KEY:
        c = stdscr.getch()


def savePicture(sshClient, image, name, email, tempFolder, remoteFolder):
    formatParams = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
    filename = encodeSubjectPictureName(name, email) + '.jpg'

    localpath = tempFolder + '/' + filename
    logging.debug('Trying to save local file to {0}'.format(localpath))
    ret = cv2.imwrite(localpath, image, formatParams)
    logging.debug('Local file written in {0} with result {1}.'.format(localpath, ret))

    sshClient.send(filename, localpath, remoteFolder)


def initCurses():
    stdscr = initscr()
    noecho()
    cbreak()
    start_color()
    stdscr.keypad(1)
    stdscr.border(0)
    stdscr.box()

    return stdscr


def destroyCurses():
    nocbreak()
    echo()
    endwin()
    os.system('stty sane')


def main():
    args = configureArguments()
    configureLogging(args.log, 'window_input.log')

    returnCode = 9
    sshClient = None
    name = ''
    email = ''

    try:
        stdscr = initCurses()
        sshClient = MultipleSSHClient(args.sshHost, args.sshUser, args.sshPassword)

        while not name or not email:
            (name, email) = drawInputWindow(stdscr)

        img = getUserPicture(int(args.outputWidth))
        savePicture(sshClient, img, name, email, args.tempLocalFolder, args.remoteFolder)

        # drawThanksWindow(stdscr)

    except KeyboardInterrupt:
        returnCode = 0
    except paramiko.SSHException:
        logging.error('Error when connecting to one or more SSH servers.')
    finally:
        if sshClient is not None:
            sshClient.close()
        cv2.destroyAllWindows()
        destroyCurses()
        sys.exit(returnCode)


if __name__ == '__main__':
    main()
