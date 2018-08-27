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
parser.add_argument('-cycles', dest='cycles', help="Number of on/off cycles; padded with 10s 'off' at beginning and end.", default=10)
parser.add_argument('-cpsec', dest='cps', help='Cycles per second (hz)', choices=[0.1, 0.2, 0.5, 1.0], default=0.5, type=float)
parser.add_argument("-type", dest="type", help="Type of stimulus display (boxcar or sine)", 
	choices=['sine','boxcar'],default='sine')

#true if should show instructions
show_inst = False
inst_text = ['The experiment will begin shortly.',
			"Once we begin, please",
			"keep your eyes on the central gray cross."]

args = parser.parse_args()
cycles = int(args.cycles)
## 10s blocks, 1/2 cycle per pi, so... 
num_pi = float(args.cps) * 10
step = int(120 / (num_pi / 2))
if args.type == 'sine':
	x = np.linspace(0,num_pi * np.pi, 120)
	t = np.zeros(x.shape)
	s = ((np.cos(x)* -1)+1) * 0.5
	s = (s * 0.96) + 0.02
	z = np.zeros(x.shape)
	ss = []
	draw_target = []
	# draw_target.extend(t)
	t[0:-1:step] = 1
	for block in range(cycles):
		for tr in range(3):
			ss.extend(s)
			draw_target.extend(t)

	x = np.linspace(0,num_pi *2 * np.pi, 120)
	s = ((np.cos(x)* -1)+1) * 0.5
	s = (s * 0.96) + 0.02
	z = np.zeros(x.shape)
	sr = []
	for block in range(cycles):
		for tr in range(3):
			sr.extend(s)

elif args.type == 'boxcar':
	x = np.linspace(0,num_pi * np.pi, 120)
	s = np.ones(x.shape)
	z = np.zeros(x.shape)
	ss = []
	ss.extend(z)
	## Do a classic 20/20 boxcar for each cycle
	for block in range(cycles):
		ss.extend(s)
		ss.extend(s)
		ss.extend(z)
		ss.extend(z)

sl = 5 * (1/60.)
timing = [sl * trial for trial in range(len(ss))]

win = psychopy.visual.Window(
    size=[1024, 768],
    units="pix",
    fullscr=True,
)

limg = psychopy.visual.ImageStim(
    win=win,
    image="left.png",
    units="pix",
    pos = (-150, 0)
)

rimg = psychopy.visual.ImageStim(
    win=win,
    image="right.png",
    units="pix",
    pos = (150,0)
)


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

target = psychopy.visual.Circle(
    win=win,
    units="pix",
    radius=10,
    fillColor=[-0.125, -0.125, -0.125],
    lineColor=[-0.5, -0.5, -0.5],
    pos=(50,0)
	)

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
for k in range(len(ss)):
	limg.contrast = ss[k] * ((k % 2) * -1)
	limg.contrast = con
	limg.setOpacity(ss[k])
	limg.draw()
	rimg.contrast = con
	rimg.setOpacity(sr[k])
	rimg.draw()
	if draw_target[k] == 1:
		target.draw()
	fixate.draw()
	while clock.getTime() < timing[k]:
		pass
	win.flip()
	tlist.append(clock.getTime())
	rimg.contrast *= -1
	if event.getKeys(keyList=["escape"]):
		core.quit()
	con *= -1
dur = np.ones(len(ss)) * sl

cps_str = str(args.cps).replace('.','_')
outname = "{}_{}_{}.ons".format(args.subid, args.type,cps_str)

while path.exists(outname) is True:
	base = outname.split('.')[0]
	outname = base+'+.ons'

f = open(outname,'w')
for k in range(len(timing)):
    f.write('{:1.3f} {:1.3f} {:1.3f}\n'.format(timing[k], dur[k], ss[k]))
f.close()

pickle.dump(tlist,open('test.p','w'))


