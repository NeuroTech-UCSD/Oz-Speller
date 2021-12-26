"""Utility functions for some aspects of the project such as plotting
or recording data.
Notes: (optional)
- 
- 
"""

## IMPORTS

import numpy as np
import json
from os.path import join as pjoin

##########################################################################
##########################################################################

## CONSTANTS

SCALE_FACTOR_EEG = (4500000)/24/(2**23-1) #uV/count
SCALE_FACTOR_AUX = 0.002 / (2**4)
ANALOGUE_MODE = '/2' # Reads from analog pins A5(D11), A6(D12) and if no 
                     # wifi shield is present, then A7(D13) as well.
CYTON_BOARD_ID = 0
BAUD_RATE = 115200

##########################################################################
##########################################################################

def do_something(epochs, subject, threshold):
    '''
    This function is supposed to do this thing...
    Inputs: (if takes in parameters)
        epochs (int)
        subject (int): idx of the subject
        threshold: Confidence threshold value for the dynamic stimulation 
                                                         ranging from 0-1 
    Returns: (if returns something)
        test_acc (array): (run_num, epochs) trained with all stimulations
        train_acc (array): (run_num, epochs) trained with all stimulations
        stim_acc (array): (num_stim, run_num) obtained by doing cross 
                                                                validation
        d_stim_prob (array): (num_run, 3) 3 -> (max probability of class, 
                                                stimulation_num,accuracy)
    Examples: (optional)
        >>> test_acc, train_acc, stim_acc, d_stim_prob = do_something(1,2,3)
    Notes: (optional)
        - 
    '''
    test_acc = []
    train_acc = []
    stim_acc = []
    d_stim_prob = []
    return test_acc, train_acc, stim_acc, d_stim_prob

def do_something_else():
    """Utility function to do things."""
    print('Things have been done.')

def save_metadata(meta, path):
    '''
    This function saves the meta data as a json file
    Inputs: 
        meta (dictionary)
        path (str): the full path to save the json file
    Notes:
        - assumes the path is valid
    '''
    with open(pjoin(path, "meta.json"), "w") as outfile:
        json.dump(meta, outfile)

def save_data(to_save, filename, path):
    """Saves the data to the path
    Inputs:
        to_save: ...
        filename (str): file name for saving 'to_save'
        path (str): the path to save 'to_save'
    """
    print('Data saved.')