#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 12:36:24 2018

@author: jcloud
"""

# In[Screen Parameters - SCANNER]:

#DISPSIZE = (1024,768)
#SCREENSIZE = (39.9, 29.9)
#SCREENDIST = 60.0
#REFRESH = 60

# In[Experiment Parameters - SCANNER]:

#SCAN = False #CHANGE THIS
#INSTRUCT = False
#SECONDS = 60 #CHANGE THIS
#TRACKER = False
#PULSEKEY = 4
#VALIDKEYS = [0,3]
#CYCLES = 7

# In[Screen Parameters - TEST]:

DISPSIZE = (1920,1080)
SCREENSIZE = (38.30, 0)
SCREENDIST = 46.0
REFRESH = 60

# In[Experiment Parameters - TEST]:

SCAN = False
INSTRUCT = True
SECONDS = 420
TRACKER = False
PULSEKEY = 4
VALIDKEYS = [0,3]
CYCLES = 7

# In[Tracker Parameters - TEST]:

FGC = (255,255,255)
BGC = (127,127,127)
SACCVELTHRESH = 35
SACCACCTHRESH = 9500
TRACKERTYPE = 'eyelink'