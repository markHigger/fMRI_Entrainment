

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

#Trial Settings
parser.add_argument('-tside', dest='side', 
                    help = 'What side the target should appear on', 
                    default='r',choices=['r','l'],
                    type=str)

parser.add_argument('-tcpsec', dest='tcps', 
                    help='Cycles per second (hz)', 
                    choices=[0.1, .125, 0.2, .25, 0.5, 1.0], default=0.5, type=float)

parser.add_argument('-ntcpsec', dest='ntcps',
                    help='Cycles per second (hz)', 
                    choices=[0.1, .125, 0.2, .25, 0.5, 1.0], default=0.5, type=float)

parser.add_argument('-tfpsec',dest='tfcps',
                    help='Cycles per second (hz) of flicker', 
                    default=12., type=float)

parser.add_argument('-ntfpsec',dest='ntfcps',
                    help='Cycles per second (hz) of non-target flicker',
                    default=12.,type=float)

parser.add_argument('-phase',dest='ph',
                    help='Degrees of shift of non-target',
                    default=0, type=int)

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
#inst_text = 'The experiment will begin shortly. Once we begin, please keep your eyes on the central gray cross.'

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

run = r.RUN

#find interstimulus distance, based on resolution and view distance, for 
#4' viewing angle; since PsychoPy calculates distance on centerpoint, adding
#128 (half of stimulus width)
base_dist = (2 * dist * math.tan(math.radians(4)/2))
base_dist_half = base_dist / 2
pixpcm = res[0] / res[2]
base_dist_pix = int(base_dist_half * pixpcm) + 128

# In[Prep Output]:

cps_str = str(args.tcps).replace('.','_')
basename = "{}_{}".format(subid, cps_str)

direc_name = subid
folder_name = wtype + '_' + cps_str

cwd = os.getcwd()

subject_folder_path = os.path.join(cwd, direc_name)
session_folder_path = os.path.join(subject_folder_path,folder_name)
fmri_folder_path = os.path.join(session_folder_path,'fmri')
debug_folder_path = os.path.join(session_folder_path,'task debug')
tracker_folder_path = os.path.join(session_folder_path,'eyetracking')
task_folder_path = os.path.join(session_folder_path,'task')

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
if not os.path.exists(task_folder_path):
    os.mkdir(task_folder_path)
    
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
    
    LOGFILENAME = basename
    director = os.getcwd()
    LOGFILE = os.path.join(tracker_folder_path,LOGFILENAME)
    
    FGC = cst.FGC
    BGC = cst.BGC
    SACCVELTHRESH = cst.SACCVELTHRESH
    SACCACCTHRESH = cst.SACCACCTHRESH
    TRACKERTYPE = cst.TRACKERTYPE
    
# In[Tracker - Calibrate]:
    
if withTracker and run == 0:
    
    scr.draw_text('tracker instructions')
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
    pos = (base_dist_pix, 0)
)

ntimg = psychopy.visual.ImageStim(
    win=pygaze.expdisplay,
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
	text=inst_text,
	height=50.

)

target_obj = psychopy.visual.Circle(
    win=pygaze.expdisplay,
    units="pix",
    radius=10,
    fillColor=[-0.125, -0.125, -0.125],
    lineColor=[-0.5, -0.5, -0.5],
    pos=(round(base_dist_pix / 2.2),0)
	)

if check_tar != 'r':
    target_obj.pos=(-50,0)

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
flicker_time = int(refresh * (1/tflicker))
t[0::step] = 1
target_minimal = t.copy()
target_minimal[flicker_time::step] = -1
for x in range(flicker_time):
    t[0+x::step] = 1


# In[Calculate Checkerboards - Generate Flickers]:

#generate target-side flicker
target_side = np.zeros(SampleBase_target.shape)
for x in range(flicker_time):
    target_side[0+x::flicker_time*2] = 1

#generate nontarget-side flicker
ntarget_side = np.zeros(SampleBase_ntarget.shape)
n_flicker_time = int(refresh * (1/ntflicker))
for x in range(n_flicker_time):
    ntarget_side[0+x::n_flicker_time * 2] = 1

# In[Calculate Checkerboards - Compile Whole Trial]:

#initiate list variables
targetFade = []
ntargetFade = []
draw_target = []
targetFlicker = []
ntargetFlicker = []
draw_target_min = []

#stack blocks into trial
for block in range(block_num):
    targetFade.extend(targetFade_block)
    ntargetFade.extend(ntargetFade_block)
    targetFlicker.extend(target_side)
    ntargetFlicker.extend(ntarget_side)
    
    copy_t = t.copy()
    copy_t_min = target_minimal.copy()
    mult = cycles // orate
    x_list = range(cycles)
    x_list.remove(0)
    for y in range(mult):
        l = 0
        x_choice = random.choice(x_list)
        x_list.remove(x_choice)
        copy_t_min[step*x_choice] = 2
        for x in range(flicker_time):
            copy_t[(step*x_choice) + x] = 2
    draw_target.extend(copy_t)
    draw_target_min.extend(copy_t_min)
    
# In[Timing Debug]:

sec_from_hz = 1/float(refresh)
timing = [sec_from_hz * trial for trial in range(len(targetFlicker))]
dur = np.ones(len(targetFade)) * sec_from_hz
t

# In[Wait for Pulse]:

if inScanner:
    event.waitKeys(keyList=['='])
    timer.expstart()
    fmri_clock.reset()
    t0 = fmri_clock.reset()
else:
    event.waitKeys(keyList=['space'])
    timer.expstart()
    fmri_clock.reset()
    t0 = fmri_clock.getTime()
    
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
debug = []
abort = False
target_fade_list = []
ntarget_fade_list = []
time2 = 0
count = 0

# In[Run Trial]:

cont = True

task_clock.reset()

while cont:
    
    debug_frame = []
    target_fade_frame = []
    ntarget_fade_frame = []
    
    if time2 == 0:
        time2 = task_clock.getTime()
        
    timing_val = find_nearest_val(timing,time2)
    timing_index = find_nearest_idx(timing,time2)
    
    debug_frame.append(task_clock.getTime())
    debug_frame.append(timing_val)
    
    
    #set alternating contrast on both checkerboards
    if targetFlicker[timing_index] == 1:
        timg.contrast = .8
    else:
        timg.contrast = -.8
    if ntargetFlicker[timing_index] == 1:
        ntimg.contrast = .8
    else:
        ntimg.contrast = -.8
        
    debug_frame.append(timg.contrast)
    debug_frame.append(ntimg.contrast)
    
    #set opacity to fade
    timg.setOpacity(targetFade[timing_index])
    ntimg.setOpacity(targetFade[timing_index])
    
    
    #Draw target at given times, this should occur every time the fade finishes
    #   an occilation
    t_timing = task_clock.getTime()
    if draw_target[timing_index] == 1:
        target_obj.setOpacity(1)
        target_obj.fillColor = [-.25,-.25,-.25]
        t_crit = 0
    elif draw_target[timing_index] == 2:
        target_obj.setOpacity(1)
        target_obj.fillColor = [.2,.2,.2]
        t_crit = 1
    elif draw_target[timing_index] == 0:
        target_obj.setOpacity(0)
    debug_frame.append(draw_target[find_nearest_idx(timing,time2)])
    
    #redraw fixation point
    scr.clear()
    scr.screen.append(timg)
    scr.screen.append(ntimg)
    scr.screen.append(fixate)
    scr.screen.append(target_obj)
    
    target_fade_frame.append(t_timing)
    ntarget_fade_frame.append(t_timing)
    
    #write to screen and record time written
    while task_clock.getTime() < timing[timing_index]:
        pass
    disp.fill(screen=scr)
    disp.show()
    time = fmri_clock.getTime()
    time2 = task_clock.getTime()
    debug_frame.append(task_clock.getTime())
    
    if t_onset == None and d_onset == None and (draw_target[timing_index] == 1 or draw_target[timing_index] == 2):
        t_onset = time
        d_onset = timing[find_nearest_idx(timing,time2)]
        debug_frame.append(t_onset)

    elif t_offset == None and d_offset == None and t_onset != None and draw_target[timing_index] == 0:
        t_offset = time
        d_offset = timing[timing_index]
        debug_frame.append(t_offset)
        
    else:
        debug_frame.append(None)
        
    if t_onset != None and t_offset != None:
        targetlist.append([t_onset,(t_offset-t_onset),t_crit])
        debug_frame.append([t_onset,t_offset,(t_offset-t_onset),d_onset,d_offset,(d_offset-d_onset)])
        t_onset = None
        t_offset = None
        d_onset = None
        d_offset = None
    else:
        debug_frame.append(None)
        
    task_time = task_clock.getTime()
    
    target_fade_frame.append((task_time - t_timing))
    ntarget_fade_frame.append((task_time - t_timing))
    target_fade_frame.append(timg.opacity)
    ntarget_fade_frame.append(ntimg.opacity)

    response = event.getKeys()
    if 'space' in response:
        resp = 1
        resp_time = fmri_clock.getTime()
    if 'escape' in response:
        abort = True
        cont = False
    
    resplist.append([resp,resp_time])
        
    resp = 0
    resp_time = 0
    
    debug.append(debug_frame)
    target_fade_list.append(target_fade_frame)
    ntarget_fade_list.append(target_fade_frame)
    
    if time2 > timing[-1]:
        cont = False

t1 = fmri_clock.getTime()

# In[Export Files - Variables and Folder Org]:

if abort:
    basename += '_abort'
    
# In[Edit Run Count]:
    
os.chdir(cwd)
    
f = open('run.py','w')
f.write('RUN = ' + str(run + 1))
f.close()

# In[Export Files - Eyetracker Run Log]:

os.chdir(subject_folder_path)

f = open(direc_name + '.log', 'a')
f.write('{},{},{},{},{},{}\n'.format(str(run),wtype,cps_str,abort,str(t0),str(t1)))
f.close()

# In[Export Files - Trigger Feat]:

os.chdir(task_folder_path)

f = open(basename + '_target.feat', 'w')
for k in targetlist:
    f.write('{}\t{}\t{}\n'.format(k[0],k[1],k[2]))
f.close()

# In[Export Files - Fade Feat]:
os.chdir(fmri_folder_path)

f = open(basename + '_tside.feat', 'w')
for k in target_fade_list:
    f.write('{}\t{}\t{}\n'.format(k[0],k[1],k[2]))
f.close()

f = open(basename + '_ntside.feat', 'w')
for k in target_fade_list:
    f.write('{}\t{}\t{}\n'.format(k[0],k[1],k[2]))
f.close()

# In[Export Files - Response QC Log]:

os.chdir(task_folder_path)

count = 0
crit = False
target = False
resp_acc = []
tar = 0

for frame in range(len(draw_target)):
    if draw_target_min[frame] == 1:
        crit = False
        target = True
        count = 0
    elif draw_target_min[frame] == 2:
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
        try:
            if crit:
                resp_acc.append([targetlist[tar][0],resplist[frame][1],crit,0])
            else:
                resp_acc.append([targetlist[tar][0],resplist[frame][1],crit,1])
            count = 0
            target = False
            tar += 1
        except (IndexError):
            pass
        
f = open(basename + '_qc.log', 'w')
f.write('Onset, Resp, Crit?, Acc\n')
for k in resp_acc:
    f.write('{},{},{},{}\n'.format(k[0],k[1],k[2],k[3]))
f.close()

# In[Debug - Frame by Frame]:

os.chdir(debug_folder_path)

f = open(basename + '_debug.log', 'w')
f.write("""Start Time\tNearest Frame\tTCon\tNTCon\tTarget\tTime Post Flip\tTOnset/Offset?\tTarget Off Debug List\n""")
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
