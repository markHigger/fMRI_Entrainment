import psychopy.visual
import numpy as np
from psychopy import core, event, logging
import pickle
import argparse
import sys 
from os import path 
from fractions import gcd
import math
from nki3Tbasics import *
import pyxid

#add triggers
#keep track of triggers in separate file
#trigger with critical stimuli 

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

""" Function Description
to call :
    'python docheck_stim_12hz_split <args>'

Arguments:
    Required:
        -subid - id of subject
        -seconds - aproxamate length of video in seconds (will round up to required val)
            -default: 60s
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
        -refresh - The refresh rate of the monitor
            -default: 60
        -odd_rate - The rate you want the critical target to appear
            -default: 5
        -instruct - True if you want to show the instructions before running
            -default: True
        -resolution - Monitor dimensions in pixels (w, h) and width of screen in cm
            -default (2560,1600,33.782)
        -distance - Viewing distance from monitor in cm
            -default = 46.
        
"""
#true if in scanner
inScanner = False

###############################################################################
#lcm function

def lcm(a, b):
    return (a * b) / gcd(a,b)
###############################################################################
#Parse Inputs

parser = MyParser(prog="docheck_stim")

parser.add_argument('-subid', dest='subid', 
                    help="Subject ID. (Required)", required=True)

parser.add_argument('-seconds', dest='secs', 
                    help="Approximate number of seconds you want the task to last (will be rounded up to generate full target cycle).", 
                    default=60)

parser.add_argument('-tside', dest='side', 
                    help = 'What side the target should appear on', 
                    default='r',type=str)

#how fast the opacity changes/how often the dot appears
parser.add_argument('-tcpsec', dest='tcps', 
                    help='Cycles per second (hz)', 
                    choices=[0.1, 0.2, 0.5, 1.0], default=0.5, type=float)

parser.add_argument('-ntcpsec', dest='ntcps',
                    help='Cycles per second (hz)', 
                    choices=[0.1, 0.2, 0.5, 1.0], default=0.5, type=float)

#how fast the flicker goes
parser.add_argument('-tfpsec',dest='tfcps',
                    help='Cycles per second (hz) of flicker', 
                    default=12., type=float)

parser.add_argument('-ntfpsec',dest='ntfcps',
                    help='Cycles per second (hz) of non-target flicker',
                    default=12.,type=float)

#phase shift of non-target
parser.add_argument('-phase',dest='ph',
                    help='Degrees of shift of non-target',
                    default=60, type=int)

parser.add_argument('-refresh',dest='refresh',
                    help='Refresh rate of monitor',
                    default=60, type=int)

parser.add_argument('-odd_rate',dest='orate',
                    help='Rate of oddball appearance, where the int entered is the denominator',
                    default = 5, type=int)

parser.add_argument('-instruct',dest='ins',
                    help='True to show instructions before running',
                    default = True, type=bool)

parser.add_argument('-resolution',dest='res',
                    help='Monitor width, height, width in pixels, pixels, cm',
                    default=(1440,900,33.782), type=tuple)

parser.add_argument('-distance',dest='view_dist',
                    help='Viewing distance from monitor',
                    default = 46., type=float)

parser.add_argument('-scan',dest='scanner',
                    help='True if in scanner',
                    default=False, type=bool)

args = parser.parse_args()

#true if should show instructions
show_inst = args.ins
inst_text = ['The experiment will begin shortly.',
			"Once we begin, please",
			"keep your eyes on the central gray cross."]

psychopy.event.clearEvents()

#get arguments
tflicker = float(args.tfcps)
ntflicker = float(args.ntfcps)
seconds = float(args.secs)
tcps = args.tcps 
ntcps = args.ntcps 
phase_degrees = args.ph
phase_radians = phase_degrees * (np.pi / 180)
orate = args.orate
if orate < 10:
    cycles = orate * 2
else:
    cycles = orate
    
#true if in scanner
inScanner = args.scanner
if inScanner:
    dev = setupXID(pyxid)
    
res = args.res
dist = args.view_dist
#find the distance in cm the two halfs should be apart
base_dist = (2 * dist * math.tan(math.radians(4)/2))
#find the distance from center each half should be, in cm
base_dist_half = base_dist / 2
#convert cm to pixels
pixpcm = res[0] / res[2]
#convert base distance to pixels (add 128 to adjust for image size)
base_dist_pix = int(base_dist_half * pixpcm) + 128

###############################################################################
#setup psychopy objects
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
    pos=(base_dist_pix / 2,0)
	)
if check_tar != 'r':
    target_obj.pos=(-50,0)

event.Mouse(visible=False)

##
#Setup clock for timing
clock = core.Clock()
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
    
###############################################################################
#Calculate Checkerboards

#Cut time into repeated blocks to allow for even divisibility by different freqs
block_len = lcm((1/tcps),(1/ntcps)) * (cycles)
#length of total video in s
seconds += (seconds % block_len)
#length of video in blocks
block_num = int(seconds / block_len)
#refresh rate
refresh = args.refresh

#used to calculate aount of cycles per block
tnum_pi = float(tcps) * block_len
ntnum_pi = float(ntcps) * block_len

#Calculate times where fade is calculated
SampleBase_target = np.linspace(0,tnum_pi * 2 * np.pi, (refresh*block_len))
SampleBase_ntarget = np.linspace(0,ntnum_pi * 2 * np.pi, (refresh*block_len)) 

#caclulate checkerboard fade
# *Fade ranges from 0 to 1 in sin wave 
targetFade_block = ((np.cos(SampleBase_target)* -1)+1) * 0.5
targetFade_block  = (targetFade_block  * 0.96) + 0.02
ntargetFade_block = ((np.cos(SampleBase_ntarget + phase_radians)* -1)+1) * 0.5
ntargetFade_block = (ntargetFade_block * 0.96) + 0.02


#find when to draw the target in each block
#the target is drawn 
t = np.zeros(SampleBase_target.shape)
step = int((refresh*block_len) / (tnum_pi))
step_flick = int(refresh * (1/tflicker))
t[0::step] = 1
t[step_flick::step] = -1

target_side = np.zeros(SampleBase_target.shape)
target_side_step = int((refresh*block_len) / (tflicker * block_len))
target_side[0:-1:target_side_step] = 1

ntarget_side = np.zeros(SampleBase_ntarget.shape)
ntarget_side_step = int((refresh*block_len) / (ntflicker * block_len))
ntarget_side[0:-1:ntarget_side_step] = 1

#find fade values for the whole video by adding each block together
targetFade = []
ntargetFade = []
draw_target = []
targetFlicker = []
ntargetFlicker = []
for block in range(block_num):
    targetFade.extend(targetFade_block)
    ntargetFade.extend(ntargetFade_block)
    targetFlicker.extend(target_side)
    ntargetFlicker.extend(ntarget_side)
    
    copy_t = t.copy()
    mult = cycles // orate
    for y in range(mult):
        l = 0
        x = np.random.randint(0,(cycles)-1)
        copy_t[step*x] = 2
    draw_target.extend(copy_t)
    

#establishes flicker rate
sl = 1/float(args.refresh) #.0833, or ~12Hz
timing = [sl * trial for trial in range(len(targetFlicker))]

###############################################################################
#Wait for pulse

if inScanner:
    t0 = waitForPulse(dev)
    clock.reset()
else:
    clock.reset()
    t0 = clock.getTime()

##############################################################################
#setup experiment

#wait for user to press spacebar to start experiment
waiting = True
while waiting:
	if event.getKeys(keyList=["space"]):
		waiting = False
clock.reset()

#draw fixate point, will not change throughout experiment
fixate.size = 4
fixate.draw()
win.flip()

#wait half a second before starting 
while clock.getTime() < 0.5:
	pass
clock.reset()

#fixate point drawn again
fixate.size = 3
fixate.draw()
win.flip()

#set starting checkerboard contrast to 1
tcon = 1
ntcon = 1

#create empty timing, target timing list
tlist = []
targetlist = []
debug = []
t_onset = None
t_offset = None
d_onset = None
d_offset = None
t_crit = None
###############################################################################
#run experiment

for frame in range(len(timing)):
    
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
        target_obj.fillColor = [0,0,0]
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
    
    #quit program and close window when esc is pressed
    if event.getKeys(keyList=["escape"]):
        win.close() 
        core.quit()
        
win.close()


###############################################################################
#save timings in output file

t1 = clock.getTime()

dur = np.ones(len(targetFade)) * sl # theoretical duration between frames

#convert target fade rate to file-readable format
cps_str = str(args.tcps).replace('.','_')

#get output file name as <subjectid>_<target_rate>
outname = "{}_{}.ons".format(args.subid, cps_str)

#add + to file name if filename already exists
while path.exists(outname) is True:
	base = outname.split('.')[0]
	outname = base+'+.ons'

#Write trigger_onset, trigger_duration, expected_onset, expected_duration
#f = open(outname,'w')
#for k in debug:
#    f.write('{},{},{},{}\n'.format(k[0],k[2],k[3],k[5]))
#f.close()

#Feat format for triggers
outname = outname.rstrip('.ons')
f = open(outname+'_events.ons','w')
for k in targetlist:
    f.write('{},{},{}\n'.format(k[0],k[1],k[2]))
f.close()

#Write to participant run log file, onset and offset time of run
log_name = args.subid + '.log'
f = open(log_name,'a')
f.write(cps_str + ' time on: ' + str(t0))
f.write(cps_str + ' time off: ' + str(t1) + '\n')

pickle.dump(tlist,open('test.p','w'))




