"""This script runs the entire project pipeline
Notes:
- requires calibration.py, preprocessing.py, analysis.py ...
- run by typing 'python main.py' in the terminal or console
- ...
"""

## IMPORTS
import numpy as np
from calibration import calibration
from preprocessing import preprocessing

##########################################################################
##########################################################################

## SETTINGS

SESSION_NAME = 'session2' # overwrite

##########################################################################
##########################################################################

def main():
    main_menu(calibration, preprocessing)

def main_menu(calibration_ballback, preprocessing_callback):
    # if user clicks on calibration
    calibration_ballback()
    # once calibration finishes
    preprocessing_callback()
    # etc

##########################################################################
##########################################################################

if __name__ == "__main__": # if this script is run as a script rather
                           # than imported
    main()