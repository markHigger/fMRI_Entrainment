
# In[Documentation]:

""" Function Description
to call :
    'python docheck_stim_12hz_split <args>'

Arguments:
    Required:
        -subid - id of subject
        -phase - Degrees of shift for non-target side
            -default: 60
        
"""

# In[Import - System and Math]:

import numpy as np
#import pickle
import argparse
import sys 
import os 
from fractions import gcd
import math
import time as tim

# In[Import - PsychoPy]:

import psychopy.visual
from psychopy import core, event#, logging

# In[Import - PyGaze]:

from pygaze.libinput import Keyboard
import pygaze.libtime as timer
from pygaze.libscreen import Display, Screen
import pyxid
from pygaze.eyetracker import EyeTracker
import pygaze

# In[Import - Scanner]:

import nki3Tbasics as b3T
import constants as cst
import run as r

# In[Helper]:

#finds least common multiple of a and b
def lcm(a, b):
    return (a * b) / gcd(a,b)
            
def find_nearest_val(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def find_nearest_idx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

# In[Initiate Parser]:

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser = MyParser(prog="docheck_stim")

#Run Settings
parser.add_argument('-subid', dest='subid', 
                    help="Subject ID. (Required)", required=True)

parser.add_argument('-fpsec',dest='fps',
                    help='Rate of flicker',
                    type=float, default = 12.)


args = parser.parse_args()

# In[Global Vars From Args]:

#instructions - show or not
show_inst = cst.INSTRUCT
inst_text = ['The experiment will begin shortly.',
			"Once we begin, please",
			"keep your eyes on the central gray cross."]

#refresh rate
refresh = cst.REFRESH

cycles = cst.CYCLES

flicker = args.fps
    
#scanner - in or out
inScanner = cst.SCAN
if inScanner:
    dev = b3T.setupXID(pyxid)

#display resolution
res = (cst.DISPSIZE[0], cst.DISPSIZE[1], cst.SCREENSIZE[0])

#view distance
dist = cst.SCREENDIST

#pulse key
pkey = cst.PULSEKEY

#subject id
subid = args.subid

#valid response keys
validKeys = cst.VALIDKEYS

#eye tracker
withTracker = cst.TRACKER

run = r.RUN

#find interstimulus distance, based on resolution and view distance, for 
#4' viewing angle; since PsychoPy calculates distance on centerpoint, adding
#128 (half of stimulus width)
base_dist = (2 * dist * math.tan(math.radians(4)/2))
base_dist_half = base_dist / 2
pixpcm = res[0] / res[2]
base_dist_pix = int(base_dist_half * pixpcm) + 128

# In[Prep Output]:

fps_str = str(flicker).replace('.','_')
basename = "{}_{}".format(subid, fps_str)

direc_name = subid
folder_name = 'standard_' + fps_str

cwd = os.getcwd()

subject_folder_path = os.path.join(cwd, direc_name)
session_folder_path = os.path.join(subject_folder_path,folder_name)
fmri_folder_path = os.path.join(session_folder_path,'fmri')
debug_folder_path = os.path.join(session_folder_path,'task debug')
tracker_folder_path = os.path.join(session_folder_path,'eyetracking')

if not os.path.exists(subject_folder_path):
    os.mkdir(subject_folder_path)
if not os.path.exists(session_folder_path):
    os.mkdir(session_folder_path)
if not os.path.exists(fmri_folder_path):
    os.mkdir(fmri_folder_path)
if not os.path.exists(debug_folder_path):
    os.mkdir(debug_folder_path)
if withTracker and not os.path.exists(tracker_folder_path):
    os.mkdir(tracker_folder_path)
    
while os.path.exists(os.path.join(debug_folder_path, basename + '_debug.log')):
    basename += '+'

# In[Initiate PyGaze Objects]:
disp = Display(disptype='psychopy')
scr = Screen(disptype='psychopy')

if inScanner or withTracker:
    kb = Keyboard()

if withTracker:
    tracker = EyeTracker(disp)
    
    DISPSIZE = cst.DISPSIZE
    
    LOGFILENAME = basename + '_eyetracker'
    LOGFILE = os.path.join(cwd,LOGFILENAME)
    
    FGC = cst.FGC
    BGC = cst.BGC
    SACCVELTHRESH = cst.SACCVELTHRESH
    SACCACCTHRESH = cst.SACCACCTHRESH
    TRACKERTYPE = cst.TRACKERTYPE
    SCREENSIZE = cst.SCREENSIZE
    
# In[Tracker - Calibrate]:

if withTracker and run == 0:
    
    scr.draw_text(text="""We will now calibrate the eyetracker. Dots will appear one at a time. Focus on them until they
                  disappear.""")
    disp.fill(scr)
    disp.show()
    
    kb.get_key(keylist = None, timeout = None, flush = True)
    
    if TRACKERTYPE != 'dummy':
        tracker.calibrate()
    
    scr.clear()
    
elif withTracker:
    scr.clear()

# In[Initiate PsychoPy Objects]:

psychopy.event.clearEvents()
    
timg = psychopy.visual.ImageStim(
    win=pygaze.expdisplay,
    image="right.png",
    units="pix",
    pos = (base_dist_pix, 0),
    opacity = 1
)

ntimg = psychopy.visual.ImageStim(
    win=pygaze.expdisplay,
    image="left.png",
    units="pix",
    pos = (base_dist_pix * -1,0),
    opacity = 1
)

fixate = psychopy.visual.ShapeStim(
    win=pygaze.expdisplay,
    units="pix",
    vertices=((-3,.5),(-.5,.5),
              (-.5,3),(.5,3),
              (.5,.5),(3,.5),
              (3,-.5),(.5,-.5),
              (.5,-3),(-.5,-3),
              (-.5,-.5),(-3,-.5)),
    size=5,
    fillColor=[-0.25, -0.25, -0.25],
    lineColor=[-1, -1, -1]
)

inst = psychopy.visual.TextStim(
	win=pygaze.expdisplay,
	text='',
	height=50.

)

event.Mouse(visible=False)

fmri_clock = core.Clock()
task_clock = core.Clock()

# In[Show Instructions]:

if show_inst:
	for txt in inst_text:
        	inst.text = txt
        	scr.clear()
        	scr.screen.append(inst)
        	disp.fill(screen=scr)
        	disp.show()
        	fmri_clock.reset()
        	while fmri_clock.getTime() < 2:
            		pass

scr.clear()
scr.screen.append(fixate)
disp.fill(screen=scr)
disp.show()
    
# In[Calculate Checkerboards - Initiate Variables]:

#find length of block that allows for full oscillations of target and non-target sides
cycle_len = 20
cycle_size = refresh * 20
flicker_time = int(refresh * (1/flicker))

# In[Calculate Checkerboards - Generate Flickers]:

#generate target-side flicker
flicker_cycle = np.ones(cycle_size)
for x in range(flicker_time):
    flicker_cycle[0+x::flicker_time*2] = -1
swap = cycle_size
#flicker_cycle[-1] = 2
#null_cycle = np.ones(len(flicker_cycle))
#null_cycle[-1] = 2


# In[Calculate Checkerboards - Compile Whole Trial]:

#flicker_block = []
#
#for x in range(cycles):
#    flicker_block.extend(null_cycle)
#    flicker_block.extend(flicker_cycle)
    
# In[Timing Debug]:

sec_from_hz = 1/float(refresh)
#timing = [sec_from_hz * trial for trial in range(len(flicker_block))]
timing = [sec_from_hz * trial for trial in range(len(flicker_cycle))]

# In[Wait for Pulse]:

if inScanner:
    b3T.waitForPulseKey(dev,timer,kb,pkey)
    timer.expstart()
    fmri_clock.reset()
    t0 = fmri_clock.reset()
else:
    event.waitKeys(keyList=['space'])
    timer.expstart()
    fmri_clock.reset()
    t0 = fmri_clock.reset()
    
if withTracker:
    tracker.start_recording()
    tracker.log("start trial %d" % 1)
    
# In[Tracker - Start]:
    
if withTracker:
    tracker.start_recording()
    tracker.status_msg("Pulse Received; Recording...")
    #timer.pause(waitTime) why the pause here?


# In[Initiate Trial Stimuli]:

#draw fixate point, will not change throughout experiment
fixate.size = 5
scr.clear()
scr.screen.append(fixate)
disp.fill(screen=scr)
disp.show()

#wait half a second before starting 
while fmri_clock.getTime() < 0.5:
	pass

#fixate point drawn again, smaller
fixate.size = 3
scr.clear()
scr.screen.append(fixate)
disp.fill(screen=scr)
disp.show()

# In[Initiate Trial Variables]

debug = []
flick = []
fix = []
swap_bool = None
s_onset = None
s_offset = None
f_onset = None
f_offset = None
abort = False
time2 = 0
cycle_count = 0

# In[Run Trial]:

cont = True

task_clock.reset()
#check_time = core.Clock()

while cont and cycle_count < cycles:
    
    debug_frame = []
    
    if time2 == 0:
        time2 = task_clock.getTime()
        
    timing_val = find_nearest_val(timing,time2)
    timing_index = find_nearest_idx(timing,time2)
    
    debug_frame.append(task_clock.getTime())
    debug_frame.append(timing_val)
    
    #set alternating contrast on both checkerboards
    if flicker_cycle[timing_index] == 1:
        timg.contrast = 1
        ntimg.contrast = 1
        swap_bool = False
    elif flicker_cycle[timing_index] == -1:
        timg.contrast = -1
        ntimg.contrast = -1
        swap_bool = False
        
    debug_frame.append(swap_bool)
    debug_frame.append(timg.contrast)
    
    #draw checkerboards
    scr.clear()
    scr.screen.append(timg)
    scr.screen.append(ntimg)
    scr.screen.append(fixate)
    
    #write to screen and record time written
    while task_clock.getTime() < timing[timing_index]:
        pass
    disp.fill(screen=scr)
    disp.show()
    
    time = fmri_clock.getTime()
    time2 = task_clock.getTime()
    debug_frame.append(task_clock.getTime())
    
    if f_onset == None:
        f_onset = time
        timg.opacity = 1
        ntimg.opacity = 1
        
    if time2 > timing[-1]:
        scr.clear()
        scr.screen.append(fixate)
        disp.fill(screen=scr)
        disp.show()
        f_offset = time
        flick.append([f_onset, (f_offset-f_onset), 1])
        task_clock.reset()
        while task_clock.getTime() < 20:
            pass
        f_onset = None
        f_offset = None
        cycle_count += 1
        task_clock.reset()
        time2 = task_clock.getTime()

    response = event.getKeys()
    if 'escape' in response:
        abort = True
        cont = False
    
    debug.append(debug_frame)

scr.clear()
disp.fill(screen=scr)
disp.show()
event.waitKeys(keyList=['space'])

t1 = fmri_clock.getTime()

# In[Export Files - Variables and Folder Org]:

if abort:
    basename += '_abort'
    
# In[Edit Run Count]:
os.chdir(cwd)

f = open("run.py", 'w')
f.write('RUN = ' + str(run + 1))
f.close()

# In[Export Files - Eyetracker Run Log]:

os.chdir(subject_folder_path)

f = open(direc_name + '.log', 'a')
f.write('{},{},{},{},{},{}\n'.format(str(run),'standard',fps_str,abort,str(t0),str(t1)))
f.close()

# In[Export Files - Flicker/Fix Feat]:

os.chdir(fmri_folder_path)

f = open(basename + '_flicker.feat', 'w')
for k in flick:
    f.write('{}\t{}\t{}\n'.format(k[0],k[1],k[2]))
f.close()

# In[Debug - Frame by Frame]:

os.chdir(debug_folder_path)

f = open(basename + '_debug.log', 'w')
f.write("""Start Time\tNearest Frame\tSwap?\tCon\tTime Post Flip\tSwap Debug List\n""")
for v in debug:
    for x in v:
        f.write('{}\t'.format(x))
    f.write('\n')
f.close()

# In[Debug - Target Onsets]: 

#Write trigger_onset, trigger_duration, expected_onset, expected_duration
#f = open(basename + '_debug.ons','w')
#for k in debug:
#    f.write('{},{},{},{}\n'.format(k[0],k[2],k[3],k[5]))
#f.close()

# In[Exit]:
disp.close()

if withTracker:
    tracker.stop_recording()
    tracker.close()
