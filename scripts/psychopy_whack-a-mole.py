"""
SSVEP Offline Experiment
Notes:
- Press esc to quit
- MAKE SURE refresh_rate IS SET TO YOUR MONITOR'S REFRESH RATE
"""

from psychopy import visual, core, event
from psychopy.hardware import keyboard
import pandas as pd
import mne
import numpy as np
from scipy import signal
from sklearn.cross_decomposition import CCA
import random
import sys, time
import os
sys.path.append('src') # if run from the root project directory

# █████████████████████████████████████████████████████████████████████████████

## VARIABLES

refresh_rate = 60.02 # refresh rate of the monitor
use_retina = False # whether the monitor is a retina display
stim_duration = 5  # in seconds
isi_duration = 750  # in ms
result_duration = 3 # in seconds
n_per_class=3
after_stim_padding = 0.25 # in seconds, stim remains but the data is discarded
classes=[9, 11, 12.6]
data = []
run_count = 0
first_call = True
psd_peaks = {8:[8,16,24,32],9:[9,15,18,24],10:[10,10,40,20],11:[11,22,27,6],12:[12,12,24,24],
            12.6:[12.6,9.6,25.2,22.2],13:[13,13,8,26],14:[14,28,8,32],15:[15,15,30,45]}
n_samples = 1500
n_harmonics = 4
sampling_freq = 300
n_components = 4
synthetic_reference = np.zeros((3,n_harmonics*2,n_samples)) # * 2 because sin and cos
for i_freq,target_freq in enumerate([9,11,12.6]):
    times = np.linspace(0,5,1500)
    # sample_times = np.linspace([0] * n_harmonics,[n_samples-1] * n_harmonics * np.arange(1,n_harmonics+1) / sampling_freq,n_samples).T
    interested_peaks = np.array(psd_peaks[target_freq])/target_freq
    sample_times = np.linspace([0] * n_harmonics,[n_samples-1] * n_harmonics * interested_peaks / sampling_freq,n_samples).T
    sinwave = np.sin(2. * np.pi * target_freq * sample_times)
    coswave = np.cos(2. * np.pi * target_freq * sample_times)
    for i,(each_harmonic_sin,each_harmonic_cos) in enumerate(zip(sinwave,coswave)):
        synthetic_reference[i_freq,2*i,:] = each_harmonic_sin
        synthetic_reference[i_freq,2*i+1,:] = each_harmonic_cos
# print(synthetic_reference.shape) # Shape: frequency, harmonics*2, timepoints

# █████████████████████████████████████████████████████████████████████████████

## FUNCTIONS

def create_fixation_cross(pos=[0,0],size=100):
    # return visual.ShapeStim(
    #     win = win,
    #     units='pix',
    #     size = size,
    #     fillColor=[1, 1, 1],
    #     lineColor=[1, 1, 1],
    #     lineWidth = 1,
    #     vertices = 'cross',
    #     name = 'off', # Used to determine state
    #     pos = pos
    # )
    return visual.ImageStim( # hand
        win = win,
        units='pix',
        size=size,
        image = 'figures/boota.png',
        pos = pos
    )

def ms_to_frame(ms, fs):
    dt = 1000 / fs
    return np.round(ms / dt).astype(int)

def create_flickering_square(pos=[0,0],size=150):
    return visual.Rect(
        win=win,
        units="pix",
        width=size,
        height=size,
        fillColor='white',
        lineColor='white',
        lineWidth = 1,
        pos = pos
    )

def create_photosensor_dot(size=50):
    return visual.Circle(
        win=win,
        units="pix",
        radius=size,
        fillColor='white',
        lineColor='white',
        lineWidth = 1,
        edges = 32,
        pos = (-(win_w / 2) + size, -((win_h / 2) - size))
    )

def create_trial_sequence(n_per_class, classes = [7.5,8.57,10,12,15]):
    """
    Create a random sequence of trials with n_per_class of each class
    Inputs:
        n_per_class : number of trials for each class
    Outputs:
        seq : (list of len(10 * n_per_class)) the trial sequence
    """
    seq = classes * n_per_class
    random.seed()
    random.shuffle(seq) # shuffles in-place
    return seq

def load_data_temp_function(eeg, beginning_eeg_time, beginning_time, trial_start_time):
    eeg_trial_start_time = beginning_eeg_time + (trial_start_time - beginning_time)
    eeg = eeg.loc[eeg['time']>eeg_trial_start_time].drop(columns=['time',' TRG']).to_numpy()[:1725].T[:,225:]
    eeg = mne.filter.filter_data(eeg, sfreq=300, l_freq=5, h_freq=49, verbose=0, method='fir')
    return eeg

# █████████████████████████████████████████████████████████████████████████████

## DSI-7

import dsi, ctypes, multiprocessing
SampleCallback = ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_double, ctypes.c_void_p )
@SampleCallback
def ExampleSampleCallback_Signals( headsetPtr, packetTime, userData ):
    global run_count
    global data
    global first_call
    h = dsi.Headset( headsetPtr )
    sample_data = [packetTime] # time stamp
    sample_data.extend([ch.ReadBuffered() for ch in h.Channels()]) # channel voltages
    data.append(sample_data)
    run_count += 1
    if first_call:
        with open("temp_meta.csv", 'w') as csv_file:
            csv_file.write(str(time.time()) + '\n')
        first_call = False
    if run_count >= 10:
        run_count = 0
        data_np = np.array(data)
        with open("temp_eeg.csv", 'a') as csv_file:
            np.savetxt(csv_file, data_np, delimiter=', ')
        data = []
def record():
    args = getattr( sys, 'argv', [ '' ] )
    if sys.platform.lower().startswith( 'win' ): default_port = 'COM4'
    else:                                        default_port = '/dev/cu.DSI7-0009.BluetoothSeri'
    # first command-line argument: serial port address
    if len( args ) > 1: port = args[ 1 ]
    else: port = default_port
    # second command-line argument:  name of the Source to be used as reference, or the word 'impedances'
    if len( args ) > 2: ref = args[ 2 ]
    else: ref = ''
    headset = dsi.Headset()
    headset.Connect(port)
    headset.SetSampleCallback( ExampleSampleCallback_Signals, 0 )
    headset.StartDataAcquisition()
    with open("temp_eeg.csv", 'w') as csv_file:
        csv_file.write('time, '+', '.join([ ch.GetName()  for ch in headset.Channels() ])+'\n')
    while True:
        headset.Idle(2.0)
if __name__ == "__main__": 
    recording = multiprocessing.Process(target=record,daemon=True)
    recording.start()
    time.sleep(7)

# █████████████████████████████████████████████████████████████████████████████

## EXPERIMENT

# if this script is run as a script rather than imported
if __name__ == "__main__": 
    win = visual.Window(
        screen = 0,
        fullscr = True,
        color = [-1,-1,-1], # black
        useRetina = use_retina
    )
    kb = keyboard.Keyboard()
    [win_w,win_h] = win.size
    if use_retina:
        win_w,win_h = win_w/2,win_h/2
    fixation = create_fixation_cross([0,200])
    fixation2 = create_fixation_cross([-200,-100])
    fixation3 = create_fixation_cross([200,-100])
    square = create_flickering_square([0,200])
    square2 = create_flickering_square([-200,-100])
    square3 = create_flickering_square([200,-100])
    # photosensor = create_photosensor_dot()
    sequence = create_trial_sequence(n_per_class=n_per_class,classes=classes)
    data_path = "./"
    meta = np.loadtxt(data_path + 'temp_meta.csv', delimiter=',', dtype=float)
    eeg = pd.read_csv(data_path + 'temp_eeg.csv').astype(float)
    beginning_eeg_time = eeg['time'].iloc[0]
    beginning_time = meta
    
    for flickering_freq in sequence: # for each trial in the trail sequence
        keys = kb.getKeys()
        for thisKey in keys:
            if thisKey=='escape':  # it is equivalent to the string 'q'
                core.quit()
        for frame in range(ms_to_frame(isi_duration, refresh_rate)):
            if frame == 0:
                trial_start_time = time.time()
            #     with open("meta.csv", 'a') as csv_file:
            #         csv_file.write(str(flickering_freq) + ', ' + str(time.time()) + '\n')
            if flickering_freq == classes[0]:
                fixation.draw()
            if flickering_freq == classes[1]:
                fixation2.draw()
            if flickering_freq == classes[2]:
                fixation3.draw()
            win.flip()

        # 'stim_duration' seconds stimulation using flashing frequency approximation:
        phase_offset = 0 # for implementing frequency and phase mixed coding in the future
        phase_offset += 0.00001 # nudge phase slightly from points of sudden jumps for offsets that are pi multiples
        stim_duration_frames = ms_to_frame((stim_duration+after_stim_padding)*1000, refresh_rate) # total number of frames for the stimulation
        frame_indices = np.arange(stim_duration_frames) # the frames as integer indices
        trial = signal.square(2 * np.pi * classes[0] * (frame_indices / refresh_rate) + phase_offset) # frequency approximation formula
        trial2 = signal.square(2 * np.pi * classes[1] * (frame_indices / refresh_rate) + phase_offset) # frequency approximation formula
        trial3 = signal.square(2 * np.pi * classes[2] * (frame_indices / refresh_rate) + phase_offset) # frequency approximation formula
        trial[trial<0] = 0 # turn -1 into 0
        trial = trial.astype(int) # change float to int
        trial2[trial2<0] = 0 # turn -1 into 0
        trial2 = trial2.astype(int) # change float to int
        trial3[trial3<0] = 0 # turn -1 into 0
        trial3 = trial3.astype(int) # change float to int
        for frame,frame2,frame3 in zip(trial,trial2,trial3): # present the stimulation frame by frame
            if frame == 1:
                square.draw()
            if frame2 == 1:
                square2.draw()
            if frame3 == 1:
                square3.draw()
            win.flip()
        eeg = pd.read_csv(data_path + 'temp_eeg.csv').astype(float)
        eeg = load_data_temp_function(eeg, beginning_eeg_time, beginning_time, trial_start_time)
        # print(eeg.shape)
        max_corr = 0
        max_corr_freq = -1
        for k,target_freq in enumerate([9,11,12.6]):
            model_cca = CCA(n_components=n_components)
            model_cca.fit(eeg.T,synthetic_reference[k][:-1].T)
            eeg_variates,synth_ref_variates = model_cca.transform(eeg.T,synthetic_reference[k][:-1].T)
            curr_corr = np.sum([np.corrcoef(eeg_variates[:,c], synth_ref_variates[:,c])[0,1] for c in range(n_components)])
            # if target_freq == 11:
            #     curr_corr -= 0.2
            if curr_corr > max_corr:
                max_corr = curr_corr
                max_corr_freq = target_freq
        
        # print(max_corr_freq)
        for frame in range(ms_to_frame(result_duration*1000, refresh_rate)):
            if max_corr_freq == classes[0]:
                square.draw()
            if max_corr_freq == classes[1]:
                square2.draw()
            if max_corr_freq == classes[2]:
                square3.draw()
            win.flip()
    os.remove("temp_eeg.csv")
    os.remove("temp_meta.csv")
    # time.sleep(6)



