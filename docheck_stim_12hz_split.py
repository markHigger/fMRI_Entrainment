import psychopy.visual
import numpy as np
from psychopy import core, event
import pickle
import argparse
import sys 
from os import path 

#add triggers
#keep track of triggers in separate file
#visual angle triangle from eye to each side of screen -> dist between fixation and either checkerboard
    #is 4 degrees (2 each side) of visual angle (how far person is from screen in scanner)
#move target to be closer to edge
#need display resolution and 1024/768 (~300 cm) - talk to Raj and/or Cathy about distance
#frequency of critical stimuli (1/5) 
#trigger with critical stimuli
#3 file format for output 

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
        -tcpsec - Freq of non-target side checkerboard fading in Hz
            -either: 0.1, 0.2, 0.5 or 1.0
            -default: 0.5
        -fcpsec - Freq of carrier
        -phase - Degrees of shift for non-target side
            -default: 60
"""
#true if in scanner
inScanner = False

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
parser.add_argument('-fcpsec',dest='fcps',
                    help='Cycles per second (hz) of flicker', 
                    default=12., type=float)

#phase shift of non-target
parser.add_argument('-phase',dest='ph',
                    help='Degrees of shift of non-target',
                    default=60, type=int)

#true if should show instructions
show_inst = False
inst_text = ['The experiment will begin shortly.',
			"Once we begin, please",
			"keep your eyes on the central gray cross."]

psychopy.event.clearEvents()

#get arguments
args = parser.parse_args()
flicker = float(args.fcps)
seconds = float(args.secs)
#multiply frequency times 2 to get correct frequency
tcps = args.tcps * 2
ntcps = args.ntcps * 2
phase_degrees = args.ph
phase_radians = phase_degrees * (np.pi / 180)
###############################################################################
#setup psychopy objects
win = psychopy.visual.Window(
    size=[1024, 768],
    units="pix",
    fullscr=False,
)
    
timg = psychopy.visual.ImageStim(
    win=win,
    image="right.png",
    units="pix",
    pos = (150, 0)
)

ntimg = psychopy.visual.ImageStim(
    win=win,
    image="left.png",
    units="pix",
    pos = (-150,0)
)

check_tar = str(args.side)
if check_tar != 'r':
    timg.image='left.png'
    timg.pos=(-150,0)
    ntimg.image='right.png'
    ntimg.pos=(150,0)


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
    pos=(50,0)
	)
if check_tar != 'r':
    target_obj.pos=(-50,0)

event.Mouse(visible=False)

##
#Setup clock for timing
clock = core.Clock()
if show_inst is True:
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
block_len = (1/tcps) * (1/ntcps) * 10
#length of total video in s
seconds += (seconds % block_len)
#length of video in blocks
block_num = int(seconds / block_len)

#used to calculate aount of cycles per block
tnum_pi = float(tcps) * block_len
ntnum_pi = float(ntcps) * block_len

#Calculate times where fade is calculated
SampleBase_target = np.linspace(0,tnum_pi * np.pi, (flicker*block_len))
SampleBase_ntarget = np.linspace(0,ntnum_pi * np.pi, (flicker*block_len)) 

#caclulate checkerboard fade
# *Fade ranges from 0 to 1 in sin wave 
targetFade_block = ((np.cos(SampleBase_target)* -1)+1) * 0.5
targetFade_block  = (targetFade_block  * 0.96) + 0.02
ntargetFade_block = ((np.cos(SampleBase_ntarget + phase_radians)* -1)+1) * 0.5
ntargetFade_block = (ntargetFade_block * 0.96) + 0.02


#find when to draw the target in each block
#the target is drawn 
t = np.zeros(SampleBase_target.shape)
step = int((flicker*block_len) / (tnum_pi / 2))
t[0:-1:step] = 1

#find fade values for the whole video by adding each block together
targetFade = []
ntargetFade = []
draw_target = []
for block in range(block_num):
    targetFade.extend(targetFade_block)
    ntargetFade.extend(ntargetFade_block)
    draw_target.extend(t)

#establishes flicker rate
sl = (1/args.fcps) #.0833, or ~12Hz
timing = [sl * trial for trial in range(len(targetFade))]



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
con = 1

#create empty timing, target timing list
tlist = []
targetlist = []
t_onset = None
t_offset = None

###############################################################################
#run experiment
for frame in range(len(targetFade)):
    
    #set alternating contrast on both checkerboards
    timg.contrast = con
    ntimg.contrast = con
    con *= -1
    
    #set opacity to calculated fade
    timg.setOpacity(targetFade[frame])
    ntimg.setOpacity(ntargetFade[frame])
    
    #draw checkerboards
    timg.draw()
    ntimg.draw()
    
    #Draw target at given times, this should occur every time the fade finishes
    #   an occilation
    if draw_target[frame] == 1:
        target_obj.draw()
    
    #redraw fixation point
    fixate.draw()
    
    #ensure timing matches before writing to screen
    while clock.getTime() < timing[frame]:
        pass
    
    #write to screen and record time written
    win.flip()
    time = clock.getTime()
    tlist.append(time)
    
    if draw_target[frame] == 1:
        t_onset = time
    else:
        if t_onset != None and t_offset == None:
            t_offset = time
        else:
            t_onset = None
            t_offset = None
            
    try:
        targetlist.append([t_onset,(t_onset-t_offset),1])
    except (TypeError):
        pass
    
    #quit program and close window when esc is pressed
    if event.getKeys(keyList=["escape"]):
        win.close() 
        core.quit()
        
win.close()


###############################################################################
#save timings in output file


dur = np.ones(len(targetFade)) * sl # theoretical duration between frames

#convert target fade rate to file-readable format
cps_str = str(args.tcps).replace('.','_')

#get output file name as <subjectid>_<target_rate>
outname = "{}_{}.ons".format(args.subid, cps_str)

while path.exists(outname) is True:
	base = outname.split('.')[0]
	outname = base+'.ons'

f = open(outname,'w')
for k in range(len(timing)):
    f.write('{:1.3f} {:1.3f} {:1.3f}\n'.format(timing[k], dur[k], targetFade[k]))
f.close()

f = open(args.subid+'_'+cps_str+'_events.ons','w')
for k in targetlist:
    f.write('{},{},{}\n'.format(k[0],k[1],k[2]))
f.close()

pickle.dump(tlist,open('test.p','w'))



