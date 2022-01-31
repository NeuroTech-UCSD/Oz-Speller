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
from multiprocessing import Process, Queue
from backend import Server
from dsi import TCPParser

##########################################################################
##########################################################################

## SETTINGS
# CONFIG = {
#     'TRIAL_DURATION' : 2000, #(e.g. 2000 ms)
#     'TARGET_FREQUENCIES' : {'a': 15, 'b': 14},
#     'INTER_TRIAL_INTERVAL' : 1000, #(between targets)
#     'STARTUP_DELAY' : 0, #(before the first trial starts)
#     'SAMPLING_FREQUENCY' : 100,
#     'BREAK_DURATION' : 20, # in seconds
#     'NUM_TRIALS' : 7, #(e.g. randomly pick 10 of the 40 characters)
#     'CHANNELS' : ['P4']
# }

SUBJECT_NUMBER = 0 # to be set by frontend
SESSION_NUMBER = 0 # to be set by frontend

with open('config.json', 'r') as json_file:
    CONFIG = json.load(json_file)

for key,val in CONFIG.items():
    exec(key + '=val')


### SET PATHS
BASE_PATH = "../"
FIGURE_PATH = pjoin(BASE_PATH, "figures/eeg_recordings/")
DATA_PATH = pjoin(BASE_PATH, "data/eeg_recordings/")
if not os.path.isdir(FIGURE_PATH):
    os.makedirs(FIGURE_PATH)
if not os.path.isdir(DATA_PATH):
    os.makedirs(DATA_PATH)

##########################################################################
##########################################################################

# def calibration():
#     """Runs the calibration script"""
#     custom_instance = CustomModule(N_TRIALS, DURATION)
#     custom_instance.do_this()

#     #### SAVE DATA
#     meta = custom_instance.meta
#     save_metadata(meta, DATA_PATH)
#     # save raw eeg data, will overwrite eeg.csv by default
#     # see calibration_instance for details about the eeg variable
#     np.savetxt(pjoin(DATA_PATH, 'eeg.csv'), custom_instance.eeg, delimiter=',')

##########################################################################
##########################################################################

if __name__ == "__main__": # if this script is run as a script rather
                           # than imported
    # with open('config.json', 'w') as json_file:
    #     json.dump(CONFIG, json_file, indent = 4, sort_keys=True)
    # for vars in dir():
    #     print(vars)
    queue = Queue()
    server = Server(queue)
    dsi_parser = TCPParser('localhost',8844)