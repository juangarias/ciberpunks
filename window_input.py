#!/usr/bin/python

import argparse, logging, os, sys
from curses import *
import curses.textpad

ESCAPE_KEY = 27
ENTER_KEY = 10
BACKSPACE_KEY = 263

stdscr = initscr()
noecho()
cbreak()
stdscr.keypad(1)
stdscr.border(0)
start_color()

stdscr.addstr(4, 20, "================================")
stdscr.addstr(5, 20, "|| BIENVENIDOS A CIBERSYBERIA ||")
stdscr.addstr(6, 20, "================================")

stdscr.addstr(9, 20, "Ingrese su nombre: ")
echo()

while c != 10:
  c = stdscr.getch()

  

  stdscr.addstr(y, 20, "Key: {0}".format(c))
  y += 1


'''
begin_x = 20; begin_y = 7
height = 5; width = 40
win = newwin(height, width, begin_y, begin_x)
win.border(0)

c = 1
while c != ord('q'):
  c = win.getch()
  if ord('w') == c:
    begin_y -= 1
  elif ord('s') == c:
    begin_y += 1
  elif ord('a') == c:
    begin_x -= 1
  elif ord('d') == c:
    begin_x += 1

  stdscr.clear()
  win.mvwin(begin_y, begin_x)
'''

stdscr.keypad(0)
nocbreak()
echo()
endwin()
os.system('stty sane')
