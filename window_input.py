#!/usr/bin/python

import argparse, logging, os, sys
from curses import *

screen = initscr()
noecho()
screen.keypad(1)

begin_x = 20; begin_y = 7
height = 5; width = 40
win = newwin(height, width, begin_y, begin_x)
win.border(0)

c = 1
while c != 27:
  c = win.getch()
  if ord('w') == c:
    begin_y -= 1
  elif ord('s') == c:
    begin_y += 1
  elif ord('a') == c:
    begin_x -= 1
  elif ord('d') == c:
    begin_x += 1

  screen.clear()
  win.mvwin(begin_y, begin_x)

screen.keypad(0) 
echo()
endwin()
os.system('stty sane')
