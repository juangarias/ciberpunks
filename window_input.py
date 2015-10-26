#!/usr/bin/python
# coding=utf-8

import argparse, logging, os, sys
import cv2
from curses import *
from common import configureLogging, encodeSubjectPictureName, calculateScaledSize, drawLabel

ESCAPE_KEY = 27
BACKSPACE_KEY = 263

if os.name == 'posix':
  ENTER_KEY = 13
else:
  ENTER_KEY = 10


def configureArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--outFolder', help="Folder for writing collected faces.", 
    default="/home/juan/ciberpunks/faces/news")
  parser.add_argument('--outputWidth', help="Output with for images to display in windows.", default="600")
  parser.add_argument('--log', help="Log level for logging.", default="WARNING")
  return parser.parse_args()


def readInput(stdscr, y, x):
  stdscr.move(y, x)
  value = ''
  c = stdscr.getch()

  invalidChars = list('\\ºª!|·$%/()=¡^`[]{}*+:;<>,')

  while c != 10:
    if c < 256:
      if chr(c) in invalidChars:
        stdscr.delch(y, x)
      else:
        value += chr(c)
        x += 1
    c = stdscr.getch()

  return value


def drawInputWindow(stdscr):
  stdscr.clear()
  (h, w) = stdscr.getmaxyx()
  yPos = int(h*0.4)
  xPos = int (w*0.4)

  stdscr.addstr(yPos, xPos, "================================")
  yPos += 1
  stdscr.addstr(yPos, xPos, "|| BIENVENIDOS A CyBerSiBeriA ||")
  yPos += 1
  stdscr.addstr(yPos, xPos, "================================")
  yPos += 3

  stdscr.addstr(yPos, xPos, "Ingrese su nombre: ")
  (nameY, nameX) = stdscr.getyx()
  yPos += 1
  stdscr.addstr(yPos, xPos, "Ingrese su e-mail: ")
  (emailY, emailX) = stdscr.getyx()
  yPos += 3
  stdscr.addstr(yPos, xPos, "===== NO enviamos spam... =====")
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
  cv2.waitKey(2)
  cv2.waitKey(3)

  return image


def drawThanksWindow(stdscr):
  stdscr.clear()
  (h, w) = stdscr.getmaxyx()
  yPos = int(h*0.4)
  xPos = int (w*0.4)

  stdscr.addstr(yPos, xPos, "================================")
  yPos += 1
  stdscr.addstr(yPos, xPos, "||       MUCHAS GRACIAS       ||")
  yPos += 1
  stdscr.addstr(yPos, xPos, "================================")
  yPos += 3
  stdscr.addstr(yPos, xPos, "...Por favor, presione [Enter]...")

  noecho()

  c = 0 
  while c != 10:
    c = stdscr.getch()


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
  try:
    returnCode = 9
    args = configureArguments()
    configureLogging(args.log)

    stdscr = initCurses()

    name = ''
    email = ''

    while not name or not email:
      (name, email) = drawInputWindow(stdscr)

    img = getUserPicture(int(args.outputWidth))

    formatParams = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
    cv2.imwrite(args.outFolder + '/' + encodeSubjectPictureName(name, email) + '.jpg', img, formatParams)

    drawThanksWindow(stdscr)

  except KeyboardInterrupt:
    returnCode = 0
  finally:
    cv2.destroyAllWindows()
    destroyCurses()
    sys.exit(returnCode)

    
  
if __name__ == '__main__':
  main()