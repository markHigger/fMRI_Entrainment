# In[Import - System and Math]:

import numpy as np
#import pickle
import argparse
import sys 
import os 
from fractions import gcd
import math
import random

# In[Import - PsychoPy]:

import psychopy.visual
from psychopy import core, event#, logging

# In[Import - PyGaze]:

from pygaze.libinput import Keyboard
import pygaze.libtime as timer
from pygaze.libscreen import Display, Screen
import pyxid
from pygaze.eyetracker import EyeTracker

# In[Import - Scanner]:

import nki3Tbasics as b3T
import constants as cst
import run as r

pulseKey = cst.PULSEKEY

kb = Keyboard()

dev = b3T.setupXID(pyxid)

def waitForPulseKey(dev,timer, kb, pulseKey):
    hasPulsed = False
    while hasPulsed == False:
        kPress = kb.get_key(keylist='q') # Allow clean escape by holding down 'q' key
        if kPress[0] != None:
            break
        dev.poll_for_response()
        if dev.response_queue_size() > 0:
            response = dev.get_next_response()
            print response['key']

waitForPulseKey(dev,timer,kb,pulseKey)
