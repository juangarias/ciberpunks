#!/usr/bin/python
# coding=utf-8

import os
import sys

if len(sys.argv) > 1:
    status = 9
    while status == 9:
        status = int(os.system("python " + sys.argv[1]) / 256)  # exit code is upper 8 bits

else:
    print "Usage: program_wrapper.py [your_program]"
