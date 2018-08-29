#!/bin/bash

#activates psypy environment
source activate psypy

#change to appropriate directory
cd /Users/jcloud/fmri_entrainment

#run programs
python docheck_stim_12hz_split.py -subid ‘000’ -tcpsec .1 -ntcpsec .1 -seconds 180
python docheck_stim_12hz_split.py -subid ‘000’ -tcpsec .2 -ntcpsec .2 -seconds 180 -tside ‘l’
python docheck_stim_12hz_split.py -subid ‘000’ -tcpsec .5 -ntcpsec .5 -seconds 180
python docheck_stim_12hz_split.py -subid ‘000’ -tcpsec 1. -ntcpsec 1. -seconds 180 -tside ‘l’