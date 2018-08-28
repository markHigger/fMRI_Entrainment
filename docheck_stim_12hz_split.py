import psychopy.visual
import numpy as np
from psychopy import core, event
import pickle
import argparse
import sys 
from os import path 

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

#true if in scanner
inScanner = False
        
parser = MyParser(prog="docheck_stim")
parser.add_argument('-subid', dest='subid', help="Subject ID. (Required)", required=True)
parser.add_argument('-seconds', dest='secs', help="Approximate number of seconds you want the task to last (will be rounded up to generate full target cycle).", default=60)
parser.add_argument('-tside', dest='side', help = 'What side the target should appear on', default='r',type=str)
#how fast the opacity changes/how often the dot appears
parser.add_argument('-tcpsec', dest='tcps', help='Cycles per second (hz)', choices=[0.1, 0.2, 0.5, 1.0], default=0.5, type=float)
parser.add_argument('-ntcpsec', dest='ntcps', help='Cycles per second (hz)', choices=[0.1, 0.2, 0.5, 1.0], default=0.5, type=float)
#how fast the flicker goes
parser.add_argument('-fcpsec',dest='fcps',help='Cycles per second (hz) of flicker', default=12., type=float)
parser.add_argument("-type", dest="type", help="Type of stimulus display (boxcar or sine)", 
	choices=['sine','boxcar'],default='sine')

#true if should show instructions
show_inst = False
inst_text = ['The experiment will begin shortly.',
			"Once we begin, please",
			"keep your eyes on the central gray cross."]

psychopy.event.clearEvents()

args = parser.parse_args()
seconds = float(args.secs)
tcps = args.tcps * 2
ntcps = args.ntcps * 2
block_len = (1/tcps) * (1/ntcps) * 10
flicker = float(args.fcps)
seconds += (seconds % block_len)
block_num = int(seconds / block_len)
tnum_pi = float(tcps) * block_len
ntnum_pi = float(ntcps) * block_len
step = int((flicker*block_len) / (tnum_pi / 2))
if args.type == 'sine':
	x = np.linspace(0,tnum_pi * np.pi, (flicker*block_len))
	t = np.zeros(x.shape)
	s = ((np.cos(x)* -1)+1) * 0.5
	s = (s * 0.96) + 0.02
	z = np.zeros(x.shape)
	target = []
	draw_target = []
	t[0:-1:step] = 1
	for block in range(block_num):
		target.extend(s)
		draw_target.extend(t)

	x = np.linspace(0,ntnum_pi * np.pi, (flicker*block_len)) 
	s = ((np.cos(x)* -1)+1) * 0.5
	s = (s * 0.96) + 0.02
	z = np.zeros(x.shape)
	nontarget = []
	for block in range(block_num):
		nontarget.extend(s)

#establishes flicker rate
sl = (1/args.fcps) #.0833, or ~12Hz
timing = [sl * trial for trial in range(len(target))]

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
    vertices=((-3,.5),(-.5,.5),(-.5,3),(.5,3),(.5,.5),(3,.5),(3,-.5),(.5,-.5),(.5,-3),(-.5,-3),(-.5,-.5),(-3,-.5)),
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


tlist = []
waiting = True
while waiting:
	if event.getKeys(keyList=["space"]):
		waiting = False

clock.reset()

fixate.size = 4
fixate.draw()
win.flip()

while clock.getTime() < 0.5:
	pass

fixate.size = 3
fixate.draw()
win.flip()

con = 1
for k in range(len(target)):
	#timg.contrast = target[k] * ((k % 2) * -1)
	timg.contrast = con
	timg.setOpacity(target[k])
	timg.draw()
	ntimg.contrast = con
	ntimg.setOpacity(nontarget[k])
	ntimg.draw()
	if draw_target[k] == 1:
		target_obj.draw()
	fixate.draw()
	while clock.getTime() < timing[k]:
		pass
	win.flip()
	tlist.append(clock.getTime())
	timg.contrast *= -1
	if event.getKeys(keyList=["escape"]):
         core.quit()
	con *= -1
dur = np.ones(len(target)) * sl

cps_str = str(args.tcps).replace('.','_')
outname = "{}_{}_{}.ons".format(args.subid, args.type,cps_str)

while path.exists(outname) is True:
	base = outname.split('.')[0]
	outname = base+'+.ons'

f = open(outname,'w')
for k in range(len(timing)):
    f.write('{:1.3f} {:1.3f} {:1.3f}\n'.format(timing[k], dur[k], target[k]))
f.close()

pickle.dump(tlist,open('test.p','w'))



