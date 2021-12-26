"""This script preprocess the eeg recordings
Notes:
- requires funcs.py, utils.py
- run by typing 'python preprocessing.py' in the terminal or console
  or alternatively import this code and optionally overwrite the constants
- assumes the raw eeg is in data/eeg_recordings/
- the processed data is saved under data/preprocessed/
"""

## IMPORTS
import numpy as np
import sys
sys.path.append('../src')
import os
from os.path import join as pjoin
from funcs import do_some_preprocessing
from utils import load_data, save_data

##########################################################################
##########################################################################

## SETTINGS

FS = 128  # sampling frequency

# Filtering Specification
L_FREQ = 4.25
H_FREQ = 90
NOTCH_FREQ = 60
FILTER_METHOD = 'iir'
REF_TYPE = 'average'
SESSION_NAME = 'session1'
FILENAME = 'data.csv'

# SET PATHS
BASE_PATH = "../"
DATA_IN_PATH = pjoin(pjoin(BASE_PATH, "data/eeg_recordings/"),SESSION_NAME)
DATA_OUT_PATH = pjoin(pjoin(BASE_PATH, "data/preprocessed/"),SESSION_NAME)
if not os.path.isdir(DATA_OUT_PATH):
    os.makedirs(DATA_OUT_PATH)

##########################################################################
##########################################################################

def preprocessing():
    raw_data = load_data(DATA_IN_PATH)
    preprocessed_data = do_some_preprocessing(raw_data)

    #### SAVE DATA
    save_data(preprocessed_data, FILENAME, DATA_OUT_PATH)

##########################################################################
##########################################################################

if __name__ == "__main__": # if this script is run as a script rather
                           # than imported
    preprocessing()
