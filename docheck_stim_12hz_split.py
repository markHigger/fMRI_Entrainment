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
        -tside - side target should apear on
            -default: right
        -tcpsec - Freq of target side checkerboard fading in Hz
            -either: 0.1, 0.2, 0.5 or 1.0
            -default: 0.5
        -ntcpsec - Freq of non-target side checkerboard fading in Hz
            -either: 0.1, 0.2, 0.5 or 1.0
            -default: 0.5
        -tfpsec - Freq of target carrier
            -default: 12.
        -ntfpsec - Freq of non-target carrier
            -default: 12.
        -phase - Degrees of shift for non-target side
            -default: 60
        -odd_rate - The rate you want the critical target to appear
            -default: 5
        -type - type of wave
            -either: box, sine
            -default: sine
        
"""

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

# In[Helper]:

#finds least common multiple of a and b
def lcm(a, b):
    return (a * b) / gcd(a,b)

#waits for pulse key from scanner
def waitForPulseKey(dev, timer, kb, pulseKey):
    hasPulsed = False
    while hasPulsed == False:
        kPress = kb.get_key(keylist='q') # Allow clean escape by holding down 'q' key
        if kPress[0] != None:
            break
        dev.poll_for_response()
        if dev.response_queue_size() > 0:
            response = dev.get_next_response()
            if response['pressed'] == True and response['key'] == pulseKey:
                hasPulsed = True
                dev.con.flush_input()
                return timer.get_time()

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

#Trial Settings
parser.add_argument('-tside', dest='side', 
                    help = 'What side the target should appear on', 
                    default='r',choices=['r','l'],
                    type=str)

parser.add_argument('-tcpsec', dest='tcps', 
                    help='Cycles per second (hz)', 
                    choices=[0.1, 0.2, 0.5, 1.0], default=0.5, type=float)

parser.add_argument('-ntcpsec', dest='ntcps',
                    help='Cycles per second (hz)', 
                    choices=[0.1, 0.2, 0.5, 1.0], default=0.5, type=float)

parser.add_argument('-tfpsec',dest='tfcps',
                    help='Cycles per second (hz) of flicker', 
                    default=12., type=float)

parser.add_argument('-ntfpsec',dest='ntfcps',
                    help='Cycles per second (hz) of non-target flicker',
                    default=12.,type=float)

parser.add_argument('-phase',dest='ph',
                    help='Degrees of shift of non-target',
                    default=60, type=int)

parser.add_argument('-odd_rate',dest='orate',
                    help='Rate of oddball appearance, where the int entered is the denominator',
                    default = 5, type=int)

parser.add_argument('-type', dest='wtype',
                    help='Box or sine',
                    choices = ['box','sine'], default='sine',
                    type=str)

args = parser.parse_args()

# In[Global Vars From Args]:

#instructions - show or not
show_inst = cst.INSTRUCT
inst_text = ['The experiment will begin shortly.',
			"Once we begin, please",
			"keep your eyes on the central gray cross."]

#rate of target-side flicker
tflicker = float(args.tfcps)

#rate of nontarget-side flicker
ntflicker = float(args.ntfcps)

#how long the task will last
seconds = cst.SECONDS

#rate of target-side oscillations
tcps = args.tcps 

#rate of nontarget-side oscillations
ntcps = args.ntcps 

#phase shift of nontarget-side
phase_degrees = args.ph
phase_radians = phase_degrees * (np.pi / 180)

#rate of appearance of critical stimulus
orate = args.orate

#refresh rate
refresh = cst.REFRESH

#to increase appearance of 'randomization', if oddball rate is too low, will
#convert from 1 in oddball to 2 in (oddball * 2)
if orate < 10:
    cycles = orate * 2
else:
    cycles = orate
    
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

#wave type
wtype = args.wtype

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
    
if withTracker:
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

check_tar = str(args.side)
if check_tar != 'r':
    timg.image='left.png'
    timg.pos=(base_dist_pix * -1,0)
    ntimg.image='right.png'
    ntimg.pos=(base_dist_pix,0)


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
	text='Placeholder Text',
	height=50.,
	flipVert=inScanner

)

target_obj = psychopy.visual.Circle(
    win=win,
    units="pix",
    radius=10,
    fillColor=[-0.125, -0.125, -0.125],
    lineColor=[-0.5, -0.5, -0.5],
    pos=(round(base_dist_pix / 2.2),0)
	)

if check_tar != 'r':
    target_obj.pos=(-50,0)

event.Mouse(visible=False)

clock = core.Clock()

# In[Show Instructions]:

if show_inst:
	for txt in inst_text:
		inst.text = txt
		inst.draw()
		win.flip()
		clock.reset()
		while clock.getTime() < 2:
			pass
	fixate.draw()
	win.flip()
    
# In[Calculate Checkerboards - Initiate Variables]:

#find length of block that allows for full oscillations of target and non-target sides
block_len = lcm((1/tcps),(1/ntcps)) * (cycles)

#determines if a block fits evenly into the trial duration; if not, generates new 
#trial time that does fit a whole number of blocks
seconds += (seconds % block_len)

#finds the number of blocks in a trial
block_num = int(seconds / block_len)

#finds the number of oscillations per block
tnum_pi = float(tcps) * block_len
ntnum_pi = float(ntcps) * block_len

# In[Calculate Checkerboards - Generate Sine Wave]:

#generate sine wave base
SampleBase_target = np.linspace(0,tnum_pi * 2 * np.pi, (refresh*block_len))
SampleBase_ntarget = np.linspace(0,ntnum_pi * 2 * np.pi, (refresh*block_len)) 

#create sine wave
targetFade_block = ((np.cos(SampleBase_target)* -1)+1) * 0.5
ntargetFade_block = ((np.cos(SampleBase_ntarget + phase_radians)* -1)+1) * 0.5

#limit ceiling and floor of sine wave; shift above 0
targetFade_block  = (targetFade_block  * 0.96) + 0.02
ntargetFade_block = (ntargetFade_block * 0.96) + 0.02

    
# In[Calculate Checkerboards - Generate Box Wave]:
    
if wtype != 'sine':
    
    t_box_step = int((refresh * block_len) / tnum_pi)
    nt_box_step = int((refresh * block_len) / ntnum_pi)
    t_box_step_half = int(t_box_step / 2)
    nt_box_step_half = int(nt_box_step / 2)
    
    t = np.zeros(SampleBase_target.shape)
    nt = np.zeros(SampleBase_ntarget.shape)
    
    t[0::t_box_step] = 1
    t[t_box_step_half::t_box_step] = -1
    nt[0::nt_box_step] = 1
    nt[t_box_step_half::nt_box_step] = -1
    
    on_val = .98
    off_val = .02
    on = False
    
    for x in range(len(targetFade_block)):
        if t[x] == 1:
            on = False
        elif t[x] == -1:
            on = True
        if on:
            targetFade_block[x] = on_val
        else:
            targetFade_block[x] = off_val
    
    for x in range(len(ntargetFade_block)):
        if nt[x] == 1:
            on = False
        elif nt[x] == -1:
            on = True
        if on:
            ntargetFade_block[x] = on_val
        else:
            ntargetFade_block[x] = off_val
        

# In[Calculate Checkerboards - Generate Targets]:

t = np.zeros(SampleBase_target.shape)
step = int((refresh*block_len) / (tnum_pi))
step_flick = int(refresh * (1/tflicker))
t[0::step] = 1
t[step_flick::step] = -1

# In[Calculate Checkerboards - Generate Flickers]:

#generate target-side flicker
target_side = np.zeros(SampleBase_target.shape)
target_side_step = int((refresh*block_len) / (tflicker * block_len))
target_side[0:-1:target_side_step] = 1

#generate nontarget-side flicker
ntarget_side = np.zeros(SampleBase_ntarget.shape)
ntarget_side_step = int((refresh*block_len) / (ntflicker * block_len))
ntarget_side[0:-1:ntarget_side_step] = 1

# In[Calculate Checkerboards - Compile Whole Trial]:

#initiate list variables
targetFade = []
ntargetFade = []
draw_target = []
targetFlicker = []
ntargetFlicker = []

#stack blocks into trial
for block in range(block_num):
    targetFade.extend(targetFade_block)
    ntargetFade.extend(ntargetFade_block)
    targetFlicker.extend(target_side)
    ntargetFlicker.extend(ntarget_side)
    
    copy_t = t.copy()
    mult = cycles // orate
    x_list = range(cycles)
    x_list.remove(0)
    for y in range(mult):
        l = 0
        x = random.choice(x_list)
        x_list.remove(x)
        copy_t[step*x] = 2
    draw_target.extend(copy_t)
    
# In[Timing Debug]:

sec_from_hz = 1/float(refresh)
timing = [sec_from_hz * trial for trial in range(len(targetFlicker))]
dur = np.ones(len(targetFade)) * sec_from_hz

# In[Wait for Pulse]:

if inScanner:
    timer.expstart()
    clock.reset()
    t0 = waitForPulseKey(dev, timer, kb, pkey)
else:
    event.waitKeys(keyList=['space'])
    timer.expstart()
    clock.reset()
    t0 = timer.get_time()
    
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
while clock.getTime() < 0.5:
	pass
clock.reset()

#fixate point drawn again, smaller
fixate.size = 3
fixate.draw()
win.flip()

#set starting checkerboard contrast to 1
tcon = 1
ntcon = 1

# In[Initiate Trial Variables]

tlist = []
targetlist = []
debug = []
resplist = []
t_onset = None
t_offset = None
d_onset = None
d_offset = None
t_crit = None
resp = None
resp_time = None

# In[Run Trial]:

cont = True

for frame in range(len(timing)):
    
    if not cont:
        break
    
    #set alternating contrast on both checkerboards
    if targetFlicker[frame] == 1:
        timg.contrast = tcon
        tcon *= -1
    if ntargetFlicker[frame] == 1:
        ntimg.contrast = ntcon
        ntcon *= -1
    
    #set opacity to calculated fade
    timg.setOpacity(targetFade[frame])
    ntimg.setOpacity(ntargetFade[frame])
    
    #draw checkerboards
    timg.draw()
    ntimg.draw()
    
    #Draw target at given times, this should occur every time the fade finishes
    #   an occilation
    if draw_target[frame] == 1:
        target_obj.setOpacity(1)
        target_obj.fillColor = [-.25,-.25,-.25]
        t_crit = 0
    elif draw_target[frame] == 2:
        target_obj.setOpacity(1)
        target_obj.fillColor = [.2,.2,.2]
        t_crit = 1
    elif draw_target[frame] == -1:
        target_obj.setOpacity(0)
    target_obj.draw()
    
    #redraw fixation point
    fixate.draw()
    
    #write to screen and record time written
    win.flip()
    time = clock.getTime()
    tlist.append(time)
    
    if draw_target[frame] == 1 or draw_target[frame] == 2:
        t_onset = time
        d_onset = timing[frame]

    elif draw_target[frame] == -1:
        t_offset = time
        d_offset = timing[frame]
        
    if t_onset != None and t_offset != None:
        targetlist.append([t_onset,(t_offset-t_onset),t_crit])
        debug.append([t_onset,t_offset,(t_offset-t_onset),d_onset,d_offset,(d_offset-d_onset)])
        t_onset = None
        t_offset = None
        
    if inScanner:
        dev.poll_for_response()
        if dev.response_queue_size() > 0:
            response = dev.get_next_response()
            if response['pressed'] == True:
                kv = response['key']
                rt = timer.get_time()
                if kv in validKeys:
                    resp = 1
                    resp_time = rt
    else:
        response = event.getKeys()
        if 'space' in response:
            resp = 1
            resp_time = clock.getTime()
        if 'escape' in response:
            cont = False
    
    resplist.append([resp,resp_time])
        
    if inScanner:
        dev.con.flush_input()
    resp = 0
    resp_time = 0

t1 = timer.get_time()

# In[Export Files - Variables and Folder Org]:

cps_str = str(args.tcps).replace('.','_')
basename = "{}_{}".format(subid, cps_str)

direc_name = subid
folder_name = wtype + '_' + cps_str

cwd = os.getcwd()

if not os.path.exists(cwd + '/' + direc_name):
    os.mkdir(cwd + '/' + direc_name)
if not os.path.exists(cwd + '/' + direc_name + '/' + folder_name):
    os.mkdir(cwd + '/' + direc_name + '/' + folder_name)
    
os.chdir(cwd + '/' + direc_name)

# In[Export Files - Eyetracker Run Log]:

f = open(direc_name + '.log', 'a')
f.write(cps_str + ' time on: ' + str(t0))
f.write(', time off: ' + str(t1) + '\n')
f.close()

# In[Folder Org P. 2]:

os.chdir(cwd + '/' + direc_name + '/' + folder_name)

while os.path.exists(basename + '.feat'):
    basename = basename + '+'

# In[Export Files - Trigger Feat]:

f = open(basename + '.feat', 'w')
for k in targetlist:
    f.write('{},{},{}\n'.format(k[0],k[1],k[2]))
f.close()

# In[Export Files - Response QC Log]:

count = 0
crit = False
target = False
resp_acc = []
tar = 0

for frame in range(len(draw_target)):
    if draw_target[frame] == 1:
        crit = False
        target = True
        count = 0
    elif draw_target[frame] == 2:
        target = True
        crit = True
        count = 0
    
    if count < round(refresh * .75) and target:
        try:
            if resplist[frame][0] == 1:
                if crit:
                    resp_acc.append([targetlist[tar][0],resplist[frame][1],crit,1])
                else:
                    resp_acc.append([targetlist[tar][0],resplist[frame][1],crit,0])
                count = 0
                target = False
                tar += 1
            else:
                count += 1
        except (IndexError):
            pass
        
    elif target:
        if crit:
            resp_acc.append([targetlist[tar][0],resplist[frame][1],crit,0])
        else:
            resp_acc.append([targetlist[tar][0],resplist[frame][1],crit,1])
        count = 0
        target = False
        tar += 1
        
f = open(basename + '_qc.log', 'w')
f.write('Onset, Resp, Crit?, Acc\n')
for k in resp_acc:
    f.write('{},{},{},{}\n'.format(k[0],k[1],k[2],k[3]))
f.close()

# In[Debug - Target Onsets]: 

#Write trigger_onset, trigger_duration, expected_onset, expected_duration
#f = open(basename + '_debug.ons','w')
#for k in debug:
#    f.write('{},{},{},{}\n'.format(k[0],k[2],k[3],k[5]))
#f.close()

# In[Debug - Frame Onsets]:

#pickle.dump(tlist,open('frame_onsets.txt','w'))

# In[Exit]:

win.close()






