"""This script runs the calibration gui and record eeg data
Notes:
- requires custom_module.py
- run by typing 'python preprocessing.py' in the terminal or console
  or alternatively import this code and optionally overwrite the constants
- the recorded data are saved under data/eeg_recordings/[SESSION_NAME]/
"""

## IMPORTS
import sys
sys.path.append('../src')
import os
from os.path import join as pjoin
import json
import numpy as np
from custom_module import CustomModule
from utils import save_metadata, save_data

##########################################################################
##########################################################################

## SETTINGS

WINDOW_SIZE = [1366, 768] # in number of pixels
FULL_SCREEN = False # if set to True, WINDOW_SIZE would be ignored
FPS = 60 # refresh rate of the display
N_TRIALS = 2 # number of trials for each target; or [a,b,c...]
DURATION = 2.0 # in seconds, duration of each trial
WAITTIME = 3.0 # in seconds, inter-trial wait time
SESSION_NAME = 'testing1'

### SET PATHS
BASE_PATH = "../"
FIGURE_PATH = pjoin(pjoin(BASE_PATH, "figures/calibration/"),SESSION_NAME)
DATA_PATH = pjoin(pjoin(BASE_PATH, "data/eeg_recordings/"),SESSION_NAME)
if not os.path.isdir(FIGURE_PATH):
    os.makedirs(FIGURE_PATH)
if not os.path.isdir(DATA_PATH):
    os.makedirs(DATA_PATH)

##########################################################################
##########################################################################

def calibration():
    """Runs the calibration script"""
    custom_instance = CustomModule(N_TRIALS, DURATION)
    custom_instance.do_this()

    #### SAVE DATA
    meta = custom_instance.meta
    save_metadata(meta, DATA_PATH)
    # save raw eeg data, will overwrite eeg.csv by default
    # see calibration_instance for details about the eeg variable
    np.savetxt(pjoin(DATA_PATH, 'eeg.csv'), custom_instance.eeg, delimiter=',')

##########################################################################
##########################################################################

if __name__ == "__main__": # if this script is run as a script rather
                           # than imported
    calibration()