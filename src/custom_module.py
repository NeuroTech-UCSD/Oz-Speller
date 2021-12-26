"""Module for some aspect of the project
Notes:
- requires funcs.py
"""

## IMPORTS
import numpy as np
import sys
sys.path.append('../src')
from funcs import do_something

##########################################################################
##########################################################################

class CustomModule:
    """Custom module for ...
    Fields:
        X (array): (run_num, trial_num, stimulation_num, channel_num)
                    the input data for the module
                    modified by: (optional, if you find it hard to track)
                        self.do_this()
                        self.__sub_routine()
        y (array): (run_num, trial_num, stimulation_num, channel_num)
                    the classification labels
                    modified by: (optional)
                        self.__sub_routine()
    Notes: (optional)
        - assumes that the input X is sampled at 128Hz
    """

    def __init__(self, X, y):
        """
        Inputs:
            X (array): (run_num, trial_num, stimulation_num, channel_num,
                                                            non_target_num)
                        the input data for the module
            y (array): (run_num, trial_num, stimulation_num, channel_num,
                                                            non_target_num)
                        the classification labels
        """
        # reshape to required dimension
        X = X.reshape([-1, X.shape[-2], X.shape[-1]])
        y = y.reshape([-1])
        self.X = X
        self.y = y

    def do_this(self):
        """This method does this thing"""
        self.__sub_routine()
        self.X = [1]
        print('Things have been done.')

    ### PRIVATE HELPER METHODS
    
    def __sub_routine(self):
        """This method does this thing"""
        self.X = [1]
        self.y = [2]
        print('Things have been done.')

