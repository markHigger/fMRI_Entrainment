#!/bin/bash

#activates psypy environment
source activate psypy

#change to appropriate directory
cd /Users/jcloud/fmri_entrainment

#run eyetracking calibration
#python eyetracking_initiation_calibration.py -subid '000'

#run study
python docheck_stim_12hz_split.py -subid tester -tcpsec .1 -ntcpsec .1 -seconds 60 -phase 0
python docheck_stim_12hz_split.py -subid tester -tcpsec .2 -ntcpsec .2 -seconds 60 -phase 0
python docheck_stim_12hz_split.py -subid tester -tcpsec .5 -ntcpsec .5 -seconds 60 -phase 0
python docheck_stim_12hz_split.py -subid tester -tcpsec 1. -ntcpsec 1. -seconds 60 -phase 0