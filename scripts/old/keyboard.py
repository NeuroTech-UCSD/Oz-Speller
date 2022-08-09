from psychopy import visual, core
from psychopy.hardware import keyboard
import numpy as np
from scipy import signal
import sys, time, pickle, os, serial
from pylsl import local_clock
from brainda.paradigms import SSVEP
from brainda.algorithms.utils.model_selection import (
    set_random_seeds, 
    generate_loo_indices, match_loo_indices)
from brainda.algorithms.decomposition import (
    FBTRCA, FBTDCA, FBSCCA, FBECCA, FBDSP,
    generate_filterbank, generate_cca_references)
sys.path.append('src') # if run from the root project directory

# █████████████████████████████████████████████████████████████████████████████

## VARIABLES
# with open("reports/trained_models/s32/fbtdca_2s.pkl", 'rb') as filehandler:
#     model = pickle.load(filehandler)
# with open("reports/trained_models/n9/fbtdca_1s.pkl", 'rb') as filehandler:
#     model = pickle.load(filehandler)
# with open("reports/trained_models/nx9/fbtdca_1400ms.pkl", 'rb') as filehandler:
#     model = pickle.load(filehandler)
with open("reports/trained_models/nx9/fbtdca_600ms_2.pkl", 'rb') as filehandler:
    model = pickle.load(filehandler)
# with open("reports/trained_models/n12/fbtdca_1s.pkl", 'rb') as filehandler:
#     model = pickle.load(filehandler)
use_retina = False # whether the monitor is a retina display
use_dsi_lsl = True
use_dsi_trigger = True
width = 1536
height = 864
refresh_rate = 60.02 # refresh rate of the monitor
# stim_duration = 1.4
stim_duration = 0.9
isi_duration = 0.75 # in seconds
# classes=[( 8,0),( 8,0.5),( 8,1),( 8,1.5),
#          ( 9,0),( 9,0.5),( 9,1),( 9,1.5),
#          (10,0),(10,0.5),(10,1),(10,1.5),
#          (11,0),(11,0.5),(11,1),(11,1.5),
#          (12,0),(12,0.5),(12,1),(12,1.5), 
#          (13,0),(13,0.5),(13,1),(13,1.5),
#          (14,0),(14,0.5),(14,1),(14,1.5),
#          (15,0),(15,0.5),(15,1),(15,1.5),]
classes=[( 8,0),( 8,0.5),( 8,1),
         (10,0),(10,0.5),(10,1),
         (15,0),(15,0.5),(15,1),]
# classes=[( 8,0),( 8,0.5),( 8,1),( 8,1.5),
#          (10,0),(10,0.5),(10,1),(10,1.5),
#          (13,0),(13,0.5),(13,1),(13,1.5),]
n_keyboard_classes = len(classes)
# classes=[( 8,  0),( 9,  0),(10,  0),(11,  0),(12,  0),(13,  0),(14,  0),(15,  0),
#          ( 8,0.5),( 9,0.5),(10,0.5),(11,0.5),(12,0.5),(13,0.5),(14,0.5),(15,0.5),
#          ( 8,  1),( 9,  1),(10,  1),(11,  1),(12,  1),(13,  1),(14,  1),(15,  1),
#          ( 8,1.5),( 9,1.5),(10,1.5),(11,1.5),(12,1.5),(13,1.5),(14,1.5),(15,1.5),]

# █████████████████████████████████████████████████████████████████████████████

## FUNCTIONS

def ms_to_frame(ms, fs):
    dt = 1000 / fs
    return np.round(ms / dt).astype(int)

def create_flickering_square(size=120, pos=[0,0]):
    return visual.Rect(
        win=win,
        units="pix",
        width=size,
        height=size,
        fillColor='white',
        # lineColor='white',
        interpolate = False,
        lineWidth = 0,
        pos = pos
    )

def create_key_char():
    pass

def create_keyboard():
    keyboard = []
    keyboard.extend([create_flickering_square(pos=[-width/2+90+i*150,height/2-90-200]) for i in range (10)])
    keyboard.extend([create_flickering_square(pos=[-width/2+90+70+i*150,height/2-90-150-200]) for i in range (9)])
    keyboard.extend([create_flickering_square(pos=[-width/2+90+140+i*150,height/2-90-300-200]) for i in range (8)])
    keyboard.extend([create_flickering_square(pos=[-width/2+90+210,height/2-90-450-200])])
    keyboard.extend([visual.Rect(win=win,units='pix',width=130*5,height=130,fillColor='white',lineColor='white',lineWidth=1,
                        pos=[-width/2+130*5+70,height/2-90-450-200])])
    keyboard.extend([create_flickering_square(pos=[-width/2+90+70*15+i*150,height/2-90-450-200]) for i in range (3)])
    return keyboard

def create_9_keys():
    keys = []
    keys.extend([create_flickering_square(pos=[-width/2+300,height/2-90-i*270-80]) for i in range (3)])
    keys.extend([create_flickering_square(pos=[-width/2+450+300,height/2-90-i*270-80]) for i in range (3)])
    keys.extend([create_flickering_square(pos=[-width/2+900+300,height/2-90-i*270-80]) for i in range (3)])
    # keys.extend([create_flickering_square(pos=[-width/2+450+i*250,height/2-90-250-200]) for i in range (3)])
    return keys

def create_12_keys():
    keys = []
    keys.extend([create_flickering_square(pos=[-width/2+300,height/2-90-i*200-80]) for i in range (4)])
    keys.extend([create_flickering_square(pos=[-width/2+450+300,height/2-90-i*200-80]) for i in range (4)])
    keys.extend([create_flickering_square(pos=[-width/2+900+300,height/2-90-i*200-80]) for i in range (4)])
    # keys.extend([create_flickering_square(pos=[-width/2+450+i*250,height/2-90-250-200]) for i in range (3)])
    return keys

def create_key_chars():
    pass

# █████████████████████████████████████████████████████████████████████████████

if use_dsi_lsl:
    from subprocess import Popen, PIPE
    import signal as sig
    import os
    from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream, resolve_streams, local_clock
    from threading import Thread, Event
    from multiprocessing import Process

    def get_lsl_data(save_variable):
        """ 'get data from lsl'  and save them onto 'save_variable'
        Continuously collect specified channels data from the Lab Streaming Layer(LSL),
        not necessarily just the EEG.
        (LSL is commonly used in EEG labs for different devices to push and pull
        data from a shared network layer to ensure good synchronization and timing
        across all devices)

        Parameters
        ----------
        save_variable : empty list --> [timepoints by channels]
                                        where channels = 
                                        [timestamp, types[0]*num_channels_of_type[0] ...]
            the variable to save the data onto
        types: len(types) list of str
            specifies the source types of the streams you want to get data from
        

        Returns
        -------
        inlets : some length list of pylsl.StreamInlet objects
        pull_thread : the thread instance that pulls data from the LSL constantly

        Note
        ----
        To properly end the pull_thread, call all inlet.close_stream() right before
        you call board.stop_stream() If this isn't done, the program could freeze or 
        show error messages. Do not lose the inlets list

        Examples
        --------
        >>> save_variable = []
        >>> inlets, _ = get_eeg_lsl(save_variable) # to start pulling data from lsl
        ...
        >>> for inlet in inlets:\
        >>>     inlet.close_stream()
        >>> print(save_variable)
        """
        streams = []
        inlets = []
        streams = resolve_streams()
        for stream in streams:
            inlets.append(StreamInlet(stream))
        if inlets == None or len(inlets) == 0:
                    raise Exception("Error: no stream found.")

        def save_sample(inlets, save_variable):
            # global record_start_time
            while True:
                row_data = [0]
                inlet_idx = 0
                while inlet_idx < len(inlets): # iterate through the inlets
                    sample, timestamp = inlets[inlet_idx].pull_sample()
                    # if record_start_time:
                    #     with open("meta.csv", 'w') as csv_file:
                    #         csv_file.write('0,0,'+str(local_clock()) + '\n')
                    #     record_start_time = False
                    if (sample, timestamp) != (None, None):
                        if inlet_idx is (len(inlets) - 1):
                            row_data[0] = timestamp
                        row_data.extend(sample)
                        inlet_idx += 1 # move on to next inlet
                    else:
                        time.sleep(0.0001) # wait for 0.1 ms if the data is not there yet
                                        # just to save some processing power
                save_variable.append(row_data)
                # if len(save_variable)>799:
                #     save_variable = save_variable[-800:]
                # save_variable = save_variable[-800:]
                # if save_variable[-1][-1] == 1:
                #     print(save_variable[-1])

        pull_thread = Thread(target = save_sample, args=(inlets, save_variable))
        pull_thread.daemon = True
        # pull_thread = Process(target = save_sample, args=(inlets, save_variable,), daemon=True)
        pull_thread.start()
        return inlets, pull_thread
    
    p = Popen([os.path.join(os.getcwd(), 'src', 'dsi2lsl-win', 'dsi2lsl.exe'), '--port=COM10','--lsl-stream-name=mystream'],shell=True,stdin=PIPE) #COM4
    # p = Popen([os.path.join(os.getcwd(), 'src', 'dsi2lsl-win', 'dsi2lsl.exe'), '--port=COM8','--lsl-stream-name=mystream'],shell=True,stdin=PIPE) #COM4

    # with open("eeg.csv", 'w') as csv_file:
    #     csv_file.write('')
    # with open("meta.csv", 'w') as csv_file:
    #     csv_file.write('')
    time.sleep(15)
    if use_dsi_trigger:
        dsi_serial = serial.Serial('COM2',115200)
    eeg = []    # receive_data() saves [timepoints by channels] here
                # where channels are length 12 [timestamp, 8 EEG Channels, 3 AUX channels]
    # print(resolve_streams())
    inlets, _ = get_lsl_data(eeg)

# █████████████████████████████████████████████████████████████████████████████

## EXPERIMENT
# if this script is run as a script rather than imported
if __name__ == "__main__": 
    kb = keyboard.Keyboard()
    win = visual.Window(
        size = [1920,1080],
        checkTiming = True,
        allowGUI = False,
        # screen = 0,
        fullscr = True,
        # color = [-1,-1,-1], # black
        useRetina = use_retina
    )
    [win_w,win_h] = win.size
    if use_retina:
        win_w,win_h = win_w/2,win_h/2

    # flickering_keyboard = create_keyboard()
    flickering_keyboard = create_9_keys()
    stim_duration_frames = ms_to_frame((stim_duration)*1000, refresh_rate) # total number of frames for the stimulation
    frame_indices = np.arange(stim_duration_frames) # the frames as integer indices
    flickering_frames = np.zeros((len(frame_indices),n_keyboard_classes))
    for i_class,(flickering_freq,phase_offset) in enumerate(classes):
        phase_offset += .00001 # nudge phase slightly from points of sudden jumps for offsets that are pi multiples
        flickering_frames[:,i_class] = signal.square(2 * np.pi * flickering_freq * (frame_indices / refresh_rate) + phase_offset * np.pi) # frequency approximation formula

    while True:
        keys = kb.getKeys()
        for thisKey in keys:
            if thisKey=='escape':
                if use_dsi_lsl:
                    for inlet in inlets:
                        inlet.close_stream()
                    os.kill(p.pid, sig.CTRL_C_EVENT)
                core.quit()
        for i_frame,frame in enumerate(flickering_frames):
            next_flip = win.getFutureFlipTime()
            for i_key,(key, key_frame) in enumerate(zip(flickering_keyboard,frame)):
                # if i_key == 0:
                #     key.color = (key_frame,key_frame,key_frame)
                # else:
                #     key.color = (-1,-1,-1)
                key.color = (key_frame,key_frame,key_frame)
                key.draw()
            if core.getTime() > next_flip:
                # n_skip = int((core.getTime()-next_flip)/0.016696429999137764)+1
                # print(str(i_trial)+', '+str(i_frame)+', '+str(n_skip))
                # next(islice(iter_frame, n_skip,n_skip), None)
                if use_dsi_trigger and use_dsi_lsl:
                    msg = b'\x01\xe1\x01\x00\x02'
                    dsi_serial.write(msg)
                for failure_frame in range(15):
                    for i_key,key in enumerate(flickering_keyboard):
                        key.color = (1,-1,-1)
                        key.draw()
                    win.flip()
            win.flip()
            if i_frame == 0 and use_dsi_trigger and use_dsi_lsl:
                msg = b'\x01\xe1\x01\x00\x01'
                dsi_serial.write(msg)

        if use_dsi_lsl:
            # trial_eeg = np.array(eeg)[-400:]
            # trial_eeg = np.array(eeg)[-510:]
            # trial_eeg = np.array(eeg)[-240:]
            trial_eeg = np.array(eeg)[-300:]
            # print(trial_eeg.shape)
            # print(trial_eeg[-1])
            # print(np.where(trial_eeg[:,-1]==2)[0])
            # print(np.where(trial_eeg[:,-1]==1)[0][-1])
            # print(trial_eeg[np.where(trial_eeg[:,-1]==1)[0][-1]])
            # print(trial_eeg[np.where(trial_eeg[:,-1]==1)[0]]) 
            # print(trial_eeg[np.where(trial_eeg[:,-1]==1)[0][0],:])
            # print(trial_eeg[np.where(trial_eeg[:,-1]==1)[0][0]+40:,1:-1].T.shape)
            if(len(np.where(trial_eeg[:,-1]==2)[0])==0):
                # prediction = model.predict(trial_eeg[np.where(trial_eeg[:,-1]==1)[0][0]+40:,1:-1].T)
                # DSI-24
                dsi24chans = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,19,22,23]
                # prediction = model.predict(trial_eeg[np.where(trial_eeg[:,-1]==1)[0][0]+40:,dsi24chans].T)
                prediction = model.predict(trial_eeg[np.where(trial_eeg[:,-1]==1)[0][0]+40:np.where(trial_eeg[:,-1]==1)[0][0]+40+185,dsi24chans].T)
                # prediction = model.predict(trial_eeg[np.where(trial_eeg[:,-1]==1)[0][0]+40:np.where(trial_eeg[:,-1]==1)[0][0]+40+245,dsi24chans].T)
            else:
                prediction = [-1]
            # print(prediction)
        for frame in range(ms_to_frame(isi_duration*1000, refresh_rate)):
            for i_key,key in enumerate(flickering_keyboard):
                if use_dsi_lsl and i_key == prediction[0]:
                    key.color = (-1,1,-1)
                    key.draw()
                else:
                    key.color = (1,1,1)
                    key.draw()
            win.flip()
        