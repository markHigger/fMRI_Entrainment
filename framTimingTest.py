#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 09:56:10 2018

@author: markhigger
"""

from matplotlib import pyplot as plt
import numpy as np  
import pandas as pd

#set name of output file *must be directly in path
outfile = "20_0_5+"

f=open(outfile + "_flicker.ons")
flicker = f.read()
f.close()
# file needs to have the following format for each line
# {timing}, {flicker_t}, {flicker_nt}, {opacity_t}
#this can be done by putting the following after win.flip()
#    frames.append(time)
#    flicker_t.append(tcon)
#    flicker_nt.append(ntcon)
#    opacity.append(targetFade[frame])
#and saving the file as 
#   f = open(basename + '_flicker.ons', 'w')
#   for i in range(np.size(frames)):
#       f.write('{},{},{},{}\n'.format(frames[i],flicker_t[i], flicker_nt[i], opacity[i]))
#   f.close()


#get amount of frames
numFrames = np.size(flicker.split('\n')) - 1
frames = flicker.split('\n')[0:-1]

#initialize vars as empty arrays
frameTimes = np.zeros(numFrames)
flicker_t = np.zeros(numFrames)
flicker_nt = np.zeros(numFrames)
opacity = np.zeros(numFrames)

#set debug params to values in file
i = 0
for frameSlice in frames:
    frameTimes[i] = frameSlice.split(',')[0]
    flicker_t[i] = frameSlice.split(',')[1]
    flicker_nt[i] = frameSlice.split(',')[2]
    opacity[i] = frameSlice.split(',')[3]
    i+=1
    
#find differences in timing wetween frames
diff = []
for frameIdx in range(numFrames):
    if frameIdx > 0:
        diff.append(frameTimes[frameIdx] - frameTimes[frameIdx - 1])


#find amount of frames per flicker
i = 0
while flicker_t[i] ==flicker_t[i + 1]:
    i+=1
lenCon_t = i + 1
i=0
while flicker_nt[i] ==flicker_nt[i + 1]:
    i+=1
lenCon_nt = i + 1

#offset starting flicker to actual starting val
con_start_t = flicker_t[0]
theoCon_t = con_start_t * -1
i = 0
conFlag_t = 0
#check flicker doesnt skip frames
wrong_t = []
for con in flicker_t:
    if i%lenCon_t == 0:
        theoCon_t *= -1
    if not con == theoCon_t:
        conFlag_t = 1
        wrong_t.append(i)
    i += 1
    
con_start_nt = flicker_nt[0]
theoCon_nt = con_start_nt * -1
i = 0
conFlag_nt = 0
wrong_nt = []
for con in flicker_nt:
    if i%lenCon_nt == 0:
        theoCon_nt *= -1
    if not con == theoCon_nt:
        conFlag_nt = 1
        wrong_nt.append(i)
    i += 1

#find contiguos opacity *Only works for box fade
i=0
while opacity[i] == opacity[i + 1]:
    i+=1
lenOpacity = i + 1
#setting staring opacity
theoOp = 1 - opacity[0]

#find if opacity matches theoretical value
wrong_op = []
i=0
for op in opacity:
    if i%lenOpacity == 0:
        theoOp = 1 - theoOp
    #save index if opacity and theoretical opacity dont match
    if not (abs(op - theoOp) < 0.0001):
        opacityFlag = 1
        wrong_op.append(i)
    i += 1
        
    
plt.figure()
y = np.sin(np.multiply(frameTimes, 2. * np.pi * 12. / 2. - frameTimes[0])) * -1
plt.plot(frameTimes, flicker_t, '.-')
plt.plot(frameTimes, y)
plt.plot(frameTimes, opacity, '.-')
plt.figure()
plt.plot(diff)
plt.figure()

plt.figure()
pddiff = pd.Series(diff[1:-1])
pddiff.hist(log=True)
