#!/bin/bash

#activates psypy environment
source activate psypy

#change to appropriate directory
cd /Users/jcloud/fmri_entrainment

#run study
python docheck_stim_12hz_split.py -subid tester -tcpsec .1 -ntcpsec .1 -phase 0 
python docheck_stim_12hz_split.py -subid tester -tcpsec .2 -ntcpsec .2 -phase 0 
python docheck_stim_12hz_split.py -subid tester -tcpsec .5 -ntcpsec .5 -phase 0 
python docheck_stim_12hz_split.py -subid tester -tcpsec 1. -ntcpsec 1. -phase 0 