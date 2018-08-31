#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 10:11:33 2018

@author: jcloud
"""

# In[Import]:

# native
import os
import random
import argparse

# PyGaze
from constants import *
from pygaze.libscreen import Display, Screen
from pygaze.libinput import Keyboard
from pygaze.eyetracker import EyeTracker
from pygaze.liblog import Logfile
import pygaze.libtime as timer
from pygame import image
import pyxid
from collections import namedtuple
from nki3Tbasics import * 

# In[Set Up Parser]:

class MyParser(argparse.ArgumentParser):
    def error(self,message):
        sys.stderr.write('error: %s/n' % message)
        self.print_help()
        sys.exit(2)
        
parser = MyParser(prog="eyetracking")

parser.add_argument('-scanner',dest='scanner',
                    help='True if in scanner',
                    default=False)
                    
parser.add_argument('-subid',dest='subid',
                    help='ID num of subject',
                    required=True)


                    
# In[Parse]:

args = parser.parse_args()

inScanner = args.scanner
subID = args.subid

# In[Visuals]:

disp = Display()
scr = Screen()

# In[Input]:

tracker = EyeTracker(disp)
if inScanner:
    dev = setupXID(pyxid)
kb = Keyboard()

# In[Instructions]:
 
# load instructions from file

trackinst = open('trackerInstructions.txt')
trackerInstructions = trackinst.read()
trackinst.close()

#display instructions

scr.draw_text(text=trackerInstructions)
disp.fill(scr)
disp.show()

#wait for keypress

kb.get_key(keylist=None, timeout=None, flush=True)

# In[Calibrate]:

tracker.calibrate()

# In[Close Window]:

scr.clear()
disp.close()
