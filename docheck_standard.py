# In[TODO]:

"""
~send trigger (where?) with critical stimuli
"""

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
import time

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

# In[Initiate PyGaze Objects]:

if withTracker:
    kb = Keyboard()
    disp = Display()
    scr = Screen()
    tracker = EyeTracker(disp)
    
# In[Tracker - Calibrate]:
    
if withTracker and run == 0:
    trackinst = open('trackerInstructions.text')
    trackerInstructions = trackinst.read()
    trackinst.close()
    
    scr.draw_text(text=trackerInstructions)
    disp.fill(scr)
    disp.show()
    
    kb.get_key(keylist = None, timeout = None, flush = True)
    
    tracker.calibrate()
    
    scr.clear()
    disp.close()
    
elif withTracker:
    scr.clear()
    disp.close()

# In[Initiate PsychoPy Objects]:

psychopy.event.clearEvents()

win = psychopy.visual.Window(
    size=[res[0], res[1]], 
    units="pix",
    fullscr=True,
    waitBlanking=True
)
    
timg = psychopy.visual.ImageStim(
    win=win,
    image="right.png",
    units="pix",
    pos = (base_dist_pix, 0)
)

ntimg = psychopy.visual.ImageStim(
    win=win,
    image="left.png",
    units="pix",
    pos = (base_dist_pix * -1,0)
)

fixate = psychopy.visual.ShapeStim(
    win=win,
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
	win=win,
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
		inst.draw()
		win.flip()
        	time.sleep(2)
	fixate.draw()
	win.flip()
    
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
null = np.zeros(cycle_size)

# In[Calculate Checkerboards - Compile Whole Trial]:

#initiate list variables
flicker_list = []

#stack blocks into trial
for block in range(cycles):
    flicker_list.extend(flicker_cycle)
    flicker_list.extend(null)
    
# In[Timing Debug]:

sec_from_hz = 1/float(refresh)
timing = [sec_from_hz * trial for trial in range(len(flicker_list))]

# In[Wait for Pulse]:

if inScanner:
    event.waitKeys(keyList=['0'])
    timer.expstart()
    fmri_clock.reset()
    t0 = fmri_clock.reset()
else:
    event.waitKeys(keyList=['space'])
    timer.expstart()
    fmri_clock.reset()
    t0 = fmri_clock.reset()
    
# In[Tracker - Start]:
    
if withTracker:
    tracker.start_recording()
    tracker.status_msg("Pulse Received; Recording...")
    #timer.pause(waitTime) why the pause here?


# In[Initiate Trial Stimuli]:

#draw fixate point, will not change throughout experiment
fixate.size = 5
fixate.draw()
win.flip()

#wait half a second before starting 
while fmri_clock.getTime() < 0.5:
	pass

#fixate point drawn again, smaller
fixate.size = 3
fixate.draw()
win.flip()

# In[Initiate Trial Variables]

debug = []
flick = []
fix = []
cycle_type = None
s_onset = None
s_offset = None
abort = False

# In[Run Trial]:

cont = True

task_clock.reset()

for frame in timing:
    
    debug_frame = []
    
    debug_frame.append(task_clock.getTime())
    debug_frame.append(find_nearest_val(timing,task_clock.getTime()))
    
    if not cont:
        break
    
    #set alternating contrast on both checkerboards
    if flicker_list[find_nearest_idx(timing,task_clock.getTime())] == 1:
        timg.contrast = 1
        ntimg.contrast = 1
        cycle_type = 'f'
    elif flicker_list[find_nearest_idx(timing,task_clock.getTime())] == -1:
        timg.contrast = -1
        ntimg.contrast = -1
        cycle_type = 'f'
    else:
        timg.contrast = 1
        ntimg.contrast = 1
        cycle_type = 's'
        
    debug_frame.append(timg.contrast)
    
    #draw checkerboards
    timg.draw()
    ntimg.draw()
    
    #redraw fixation point
    fixate.draw()
    
    #write to screen and record time written
    while task_clock.getTime() < frame:
        pass
    win.flip()
    time = fmri_clock.getTime()
    debug_frame.append(task_clock.getTime())
    
    if cycle_type == 'f' and s_onset == None:
        s_onset = time
        debug_frame.append('flicker on')
    elif cycle_type == 's' and s_onset != None and s_offset == None:
        s_offset = time
        flick.append([s_onset, (s_offset-s_onset), 1])
        debug_frame.append([s_onset, (s_offset-s_onset), 1])
        s_onset = None
        s_offset = None
    elif cycle_type == 's' and s_onset == None:
        s_onset = time
        debug_frame.append('fix on')
    elif cycle_type == 'f' and s_onset != None and s_offset == None:
        s_offset = time
        fix.append([s_onset, (s_offset-s_onset), 1])
        debug_frame.append([s_onset, (s_offset-s_onset), 1])
        s_onset = None
        s_offset = None

    response = event.getKeys()
    if 'escape' in response:
        abort = True
        cont = False
    
    debug.append(debug_frame)

timg.setOpacity(0)
ntimg.setOpacity(0)
timg.draw()
ntimg.draw()
fixate.draw()
win.flip()
event.waitKeys(keyList=['space'])

t1 = fmri_clock.getTime()

# In[Export Files - Variables and Folder Org]:

fps_str = str(flicker).replace('.','_')
basename = "{}_{}".format(subid, fps_str)
if abort:
    basename += '_abort'

direc_name = subid
folder_name = 'standard_' + fps_str

cwd = os.getcwd()

if not os.path.exists(cwd + '/' + direc_name):
    os.mkdir(cwd + '/' + direc_name)
if not os.path.exists(cwd + '/' + direc_name + '/' + folder_name):
    os.mkdir(cwd + '/' + direc_name + '/' + folder_name)
    
# In[Edit Run Count]:
    
f = open("run.py", 'w')
f.write('RUN = ' + str(run + 1))
f.close()

# In[Export Files - Folder Org Pt. 2]
    
os.chdir(cwd + '/' + direc_name)

# In[Export Files - Eyetracker Run Log]:

f = open(direc_name + '.log', 'a')
f.write('{},{},{},{}\n'.format('standard',fps_str,abort,str(t0),str(t1)))
f.close()

# In[Folder Org Pt. 3]:

os.chdir(cwd + '/' + direc_name + '/' + folder_name)

while os.path.exists(basename + '_flicker.feat'):
    basename = basename + '+'

# In[Export Files - Flicker/Fix Feat]:

f = open(basename + '_flicker.feat', 'w')
for k in int(flicker):
    f.write('{}\t{}\t{}\n'.format(k[0],k[1],k[2]))
f.close()

f = open(basename + '_fix.feat', 'w')
for k in fix:
    f.write('{}\t{}\t{}\n'.format(k[0],k[1],k[2]))
f.close()

# In[Debug - Frame by Frame]:

f = open(basename + '_debug.log', 'w')
f.write("""Start Time\tNearest Frame\tCon\tTime Post Flip\tSwap Debug List\n""")
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

win.close()