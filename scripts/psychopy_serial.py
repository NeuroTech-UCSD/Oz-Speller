"""
SSVEP Offline Experiment
phase-offset version
Notes:
- Press command-option-esc to quit
- MAKE SURE refresh_rate IS SET TO YOUR MONITOR'S REFRESH RATE
"""

from psychopy import visual, core
from psychopy.hardware import keyboard
import numpy as np
from scipy import signal
import random
import sys, time, serial
from itertools import islice
from pylsl import local_clock
sys.path.append('src') # if run from the root project directory

# █████████████████████████████████████████████████████████████████████████████

## VARIABLES
use_dsi7 = True
use_dsi_trigger = True
use_dsi_lsl = False
use_arduino = True # arduino photosensor for flashing timing test
use_cyton = False
use_photosensor = False
record_start_time = True
center_flash = False # whether the visual stimuli are only presented at the center of the screen
keyboard_flash = True
width = 1536
height = 864
flash_mode = 'square' # 'sine', 'square', or 'chirp', 'dual band'
refresh_rate = 60.02 # refresh rate of the monitor
use_retina = False # whether the monitor is a retina display
stim_duration = 3. # in seconds
isi_duration = 1 # in seconds
# after_stim_padding = 0.25 # in seconds, stim remains but the data is discarded
# isi_duration = 0.1 # in seconds
after_stim_padding = 0.0 # in seconds, stim remains but the data is discarded
n_per_class=20
keyboard_classes=[( 8,0),( 8,0.5),( 8,1),( 8,1.5),
         ( 9,0),( 9,0.5),( 9,1),( 9,1.5),
         (10,0),(10,0.5),(10,1),(10,1.5),
         (11,0),(11,0.5),(11,1),(11,1.5),
         (12,0),(12,0.5),(12,1),(12,1.5), 
         (13,0),(13,0.5),(13,1),(13,1.5),
         (14,0),(14,0.5),(14,1),(14,1.5),
         (15,0),(15,0.5),(15,1),(15,1.5),]
# keyboard_classes=[( 8,0),( 8,0.5),( 8,1),
#          (10,0),(10,0.5),(10,1),
#          (15,0),(15,0.5),(15,1),]
# classes=[(8,0),(9,1.75),(10,1.5),(11,1.25),(12,1),(13,0.75),(14,0.5),(15,0.25),
#         (8.2,0.35),(9.2,0.1),(10.2,1.85),(11.2,1.6),(12.2,1.35),(13.2,1.1),(14.2,0.85),(15.2,0.6),
#         (8.4,0.7),(9.4,0.45),(10.4,0.2),(11.4,1.95),(12.4,1.7),(13.4,1.45),(14.4,1.2),(15.4,0.95),
#         (8.6,1.05),(9.6,0.8),(10.6,0.55),(11.6,0.3),(12.6,0.05),(13.6,1.8),(14.6,1.55),(15.6,1.3),
#         (8.8,1.4),(9.8,1.15),(10.8,0.9),(11.8,0.65),(12.8,0.4),(13.8,0.15),(14.8,1.9),(15.8,1.65)]
# classes=[(15,0),(15,0.5),(15,1)]
classes=[(15,0.5)]
data = []
run_count = 0
first_call = True

# █████████████████████████████████████████████████████████████████████████████

## FUNCTIONS

def create_fixation_cross(size=50):
    return visual.ShapeStim(
        win = win,
        units='pix',
        size = size,
        fillColor=[1, 1, 1],
        lineColor=[1, 1, 1],
        lineWidth = 1,
        vertices = 'cross',
        name = 'off', # Used to determine state
        pos = [0, 0]
    )

def ms_to_frame(ms, fs):
    dt = 1000 / fs
    return np.round(ms / dt).astype(int)

def create_flickering_square(size=100, pos=[0,0]):
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

def create_photosensor_dot(size=100):
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

def create_trial_sequence(n_per_class, classes = [(7.5,0),(8.57,0),(10,0),(12,0),(15,0)]):
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

def create_keyboard():
    keyboard = []
    keyboard.extend([create_flickering_square(pos=[-width/2+90+i*150,height/2-90-200]) for i in range (10)])
    keyboard.extend([create_flickering_square(pos=[-width/2+90+70+i*150,height/2-90-150-200]) for i in range (9)])
    keyboard.extend([create_flickering_square(pos=[-width/2+90+140+i*150,height/2-90-300-200]) for i in range (8)])
    keyboard.extend([create_flickering_square(pos=[-width/2+90+210,height/2-90-450-200])])
    # keyboard.extend([visual.Rect(win=win,units='pix',width=100*5,height=100,fillColor='white',lineColor='white',lineWidth=1,
    #                     pos=[-width/2+130*5+70,height/2-90-450-200])])
    keyboard.extend([visual.Rect(win=win,units='pix',width=100*5,height=100,fillColor='white',lineWidth=0,
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
            global record_start_time
            while True:
                row_data = [0]
                inlet_idx = 0
                while inlet_idx < len(inlets): # iterate through the inlets
                    sample, timestamp = inlets[inlet_idx].pull_sample()
                    if record_start_time:
                        with open("meta.csv", 'w') as csv_file:
                            csv_file.write('0,0,'+str(local_clock()) + '\n')
                        record_start_time = False
                    if (sample, timestamp) != (None, None):
                        if inlet_idx is (len(inlets) - 1):
                            row_data[0] = timestamp
                        row_data.extend(sample)
                        inlet_idx += 1 # move on to next inlet
                    else:
                        time.sleep(0.0001) # wait for 0.1 ms if the data is not there yet
                                        # just to save some processing power
                save_variable.append(row_data)

        pull_thread = Thread(target = save_sample, args=(inlets, save_variable))
        pull_thread.daemon = True
        # pull_thread = Process(target = save_sample, args=(inlets, save_variable,), daemon=True)
        pull_thread.start()
        return inlets, pull_thread
    
    p = Popen([os.path.join(os.getcwd(), 'src', 'dsi2lsl-win', 'dsi2lsl.exe'), '--port=COM8','--lsl-stream-name=mystream'],shell=True,stdin=PIPE) #COM4
    with open("eeg.csv", 'w') as csv_file:
        csv_file.write('time, Pz, F4, C4, P4, P3, C3, F3, TRG\n')
    with open("meta.csv", 'w') as csv_file:
        csv_file.write('')
    time.sleep(15)
    if use_dsi_trigger:
        dsi_serial = serial.Serial('COM2',115200)
    eeg = []    # receive_data() saves [timepoints by channels] here
                # where channels are length 12 [timestamp, 8 EEG Channels, 3 AUX channels]
    print(resolve_streams())
    inlets, _ = get_lsl_data(eeg)

# █████████████████████████████████████████████████████████████████████████████

## DSI-7
if use_dsi7:
    import dsi, ctypes, multiprocessing, threading, serial
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
            if sample_data[1] > 1e15: # if Pz saturation error happens
                quit()
            with open("meta.csv", 'w') as csv_file:
                # csv_file.write(str(time.time()) + '\n')
                csv_file.write('0,0,'+str(local_clock()) + '\n')
            first_call = False
        if run_count >= 300: # save data every second
            run_count = 0
            data_np = np.array(data)
            with open("eeg.csv", 'a') as csv_file:
                np.savetxt(csv_file, data_np, delimiter=', ')
            data = []
    def record():
        args = getattr( sys, 'argv', [ '' ] )
        if sys.platform.lower().startswith( 'win' ): default_port = 'COM8' #COM4, COM8, COM9
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
        with open("eeg.csv", 'w') as csv_file:
            csv_file.write('time, '+', '.join([ ch.GetName()  for ch in headset.Channels() ])+'\n')
        while True:
            headset.Idle(2.0)
    if __name__ == "__main__": 
        # recording = multiprocessing.Process(target=record,daemon=True)
        recording = threading.Thread(target=record,daemon=True)
        recording.start()
        if use_dsi_trigger:
            dsi_serial = serial.Serial('COM2',115200)
        time.sleep(10)

# █████████████████████████████████████████████████████████████████████████████

## Arduino Photosensor for Timing
if use_arduino:
    from sys import executable
    import os
    from subprocess import Popen
    # Popen([executable,  os.path.join(os.getcwd(), 'run_arduino_photosensor.py')])
    Popen([executable,  os.path.join(os.getcwd(), 'scripts', 'run_arduino_photosensor.py')])
    time.sleep(2)

    # import serial, threading, multiprocessing
    # # arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)
    # arduino = serial.Serial(port='COM3', baudrate=19200, timeout=.1)
    # # arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)
    # arduino_call_num = 0
    # with open("light_amp.csv", 'w') as csv_file:
    #     csv_file.write('time, light_amp\n')
    # def record_light_amp():
    #     global arduino_call_num
    #     while True:
    #         try:
    #             # data = arduino.readline().decode('ascii')[:-1]
    #             data = int.from_bytes(arduino.read(), "big")
    #             if data > 100:
    #                 data = 0
    #             if arduino_call_num < 100:
    #                 arduino_call_num+=1
    #                 continue
    #             elif arduino_call_num == 100:
    #                 arduino_call_num+=1
    #                 with open("meta.csv", 'w') as csv_file:
    #                     csv_file.write('0,0,'+str(local_clock()) + '\n')
    #             with open("light_amp.csv", 'a') as csv_file:
    #                 # csv_file.write(data)
    #                 csv_file.write(str(local_clock())+', '+str(data)+'\n')
    #         except UnicodeDecodeError and ValueError:
    #             pass
    # if __name__ == "__main__": 
    #     # recording_light_amp = multiprocessing.Process(target=record_light_amp,daemon=True)
    #     recording_light_amp = threading.Thread(target=record_light_amp,daemon=True)
    #     recording_light_amp.start()
    #     # time.sleep(2)

# █████████████████████████████████████████████████████████████████████████████

## OpenBCI Cyton
if use_cyton:
    import glob
    from brainflow.board_shim import BoardShim, BrainFlowInputParams
    from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream, local_clock
    from serial import Serial
    from threading import Thread, Event
    CYTON_BOARD_ID = 0
    BAUD_RATE = 115200
    ANALOGUE_MODE = '/2' # Reads from analog pins A5(D11), A6(D12) and if no 
                     # wifi shield is present, then A7(D13) as well.
    
    def find_openbci_port():
        """Finds the port to which the Cyton Dongle is connected to."""
        # Find serial port names per OS
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/ttyUSB*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/cu.usbserial*')
        else:
            raise EnvironmentError('Error finding ports on your operating system')

        openbci_port = ''
        for port in ports:
            try:
                s = Serial(port=port, baudrate=BAUD_RATE, timeout=None)
                s.write(b'v')
                line = ''
                time.sleep(2)
                if s.inWaiting():
                    line = ''
                    c = ''
                    while '$$$' not in line:
                        c = s.read().decode('utf-8', errors='replace')
                        line += c
                    if 'OpenBCI' in line:
                        openbci_port = port
                s.close()
            except (OSError, serial.SerialException):
                pass
        if openbci_port == '':
            raise OSError('Cannot find OpenBCI port.')
        else:
            return openbci_port
    def start_cyton_lsl():
        """ 'start streaming cyton to lsl'
        Stream EEG and analogue(AUX) data from Cyton onto the Lab Streaming 
        Layer(LSL).
        (LSL is commonly used in EEG labs for different devices to push and pull
        data from a shared network layer to ensure good synchronization and timing
        across all devices)

        Returns
        -------
        board : board instance for the amplifier board, in this case OpenBCI Cyton
        push_thread : the thread instance that pushes data onto the LSL constantly

        Note
        ----
        To properly end the push_thread, call board.stop_stream(). If this isn't done,
        the program could freeze or show error messages. Do not lose the board instance

        Examples
        --------
        >>> board, _ = start_lsl() # to start pushing onto lsl
        ...
        >>> board.stop_streaming() # to stop pushing onto lsl
        """
        # print("Creating LSL stream for EEG. \nName: OpenBCIEEG\nID: OpenBCItestEEG\n")
        info_eeg = StreamInfo('OpenBCIEEG', 'EEG', 8, 250, 'float32', 'OpenBCItestEEG')
        # print("Creating LSL stream for AUX. \nName: OpenBCIAUX\nID: OpenBCItestEEG\n")
        info_aux = StreamInfo('OpenBCIAUX', 'AUX', 3, 250, 'float32', 'OpenBCItestAUX')

        outlet_eeg = StreamOutlet(info_eeg)
        outlet_aux = StreamOutlet(info_aux)

        params = BrainFlowInputParams()
        params.serial_port = find_openbci_port()
        board = BoardShim(CYTON_BOARD_ID, params)
        board.prepare_session()
        res_query = board.config_board('/0')
        print(res_query)
        res_query = board.config_board('//')
        print(res_query)
        res_query = board.config_board(ANALOGUE_MODE)
        print(res_query)
        board.start_stream(45000)
        time.sleep(1)
        stop_event = Event()
        def push_sample():
            start_time = local_clock()
            sent_eeg = 0
            sent_aux = 0
            while not stop_event.is_set():
                elapsed_time = local_clock() - start_time
                data_from_board = board.get_board_data()

                required_eeg_samples = int(250 * elapsed_time) - sent_eeg
                eeg_data = data_from_board[board.get_eeg_channels(CYTON_BOARD_ID)]
                datachunk = []
                for i in range(len(eeg_data[0])):
                    datachunk.append(eeg_data[:,i].tolist())
                stamp = local_clock()
                outlet_eeg.push_chunk(datachunk, stamp)
                sent_eeg += required_eeg_samples
                
                required_aux_samples = int(250 * elapsed_time) - sent_aux
                aux_data = data_from_board[board.get_analog_channels(CYTON_BOARD_ID)]
                datachunk = []
                for i in range(len(aux_data[0])):
                    datachunk.append(aux_data[:,i].tolist())
                stamp = local_clock()
                outlet_aux.push_chunk(datachunk, stamp)
                sent_aux += required_aux_samples

                time.sleep(0.02) # 20 ms

        push_thread = Thread(target=push_sample)
        push_thread.start()
        return board, stop_event
    def get_lsl_data(save_variable, types = ['EEG', 'AUX']):
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
        for stream_type in types:
            streams.extend(resolve_stream('type', stream_type))
        for stream in streams:
            inlets.append(StreamInlet(stream))
        if inlets == None or len(inlets) == 0:
                    raise Exception("Error: no stream found.")

        def save_sample(inlets, save_variable):
            global record_start_time
            while True:
                row_data = [0]
                inlet_idx = 0
                while inlet_idx < len(inlets): # iterate through the inlets
                    sample, timestamp = inlets[inlet_idx].pull_sample()
                    if record_start_time:
                        with open("meta.csv", 'w') as csv_file:
                            csv_file.write('0,0,'+str(local_clock()) + '\n')
                        record_start_time = False
                    if (sample, timestamp) != (None, None):
                        if inlet_idx is (len(inlets) - 1):
                            row_data[0] = timestamp
                        row_data.extend(sample)
                        inlet_idx += 1 # move on to next inlet
                    else:
                        time.sleep(0.0001) # wait for 0.1 ms if the data is not there yet
                                        # just to save some processing power
                save_variable.append(row_data)

        pull_thread = Thread(target = save_sample, args=(inlets, save_variable))
        pull_thread.daemon = True
        pull_thread.start()
        return inlets, pull_thread

    with open("eeg.csv", 'w') as csv_file:
        csv_file.write('time, N1P, N2P, N3P, N4P, N5P, N6P, N7P, N8P, D11, D12, D13\n')
    with open("meta.csv", 'w') as csv_file:
        csv_file.write('')
    eeg = []    # receive_data() saves [timepoints by channels] here
                # where channels are length 12 [timestamp, 8 EEG Channels, 3 AUX channels]
    board, stop_cyton = start_cyton_lsl()
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
        # waitBlanking = False,
        # waitBlanking = True,
        # screen = 1,
        # winType="pyglet",
        fullscr = True,
        # multiSample = True,
        # color = [-1,-1,-1], # black
        useRetina = use_retina
    )
    [win_w,win_h] = win.size
    if use_retina:
        win_w,win_h = win_w/2,win_h/2
    if center_flash: # if we want the visual stimuli to be only presented at the center of the screen
        fixation = create_fixation_cross()
        square = create_flickering_square()
        photosensor = create_photosensor_dot()
        sequence = create_trial_sequence(n_per_class=n_per_class,classes=classes)
        # square.color = (0, 1, 0)
        for i_trial,(flickering_freq, phase_offset) in enumerate(sequence): # for each trial in the trail sequence
            keys = kb.getKeys() 
            for thisKey in keys:
                if thisKey=='escape':
                    if use_dsi_lsl:
                        for inlet in inlets:
                            inlet.close_stream()
                        os.kill(p.pid, sig.CTRL_C_EVENT)
                        with open("eeg.csv", 'a') as csv_file:
                            np.savetxt(csv_file, eeg, delimiter=', ')
                    if use_cyton:
                        for inlet in inlets:
                            inlet.close_stream()
                        stop_cyton.set()
                        board.stop_stream()
                        with open("eeg.csv", 'a') as csv_file:
                            np.savetxt(csv_file, eeg, delimiter=', ')
                    core.quit()
            trial_text = visual.TextStim(win, str(i_trial+1)+'/'+str(len(sequence)), color=(-1, -1, -1), colorSpace='rgb')
            # 750ms fixation cross:
            for frame in range(ms_to_frame(isi_duration*1000, refresh_rate)):
                # if frame == 0:
                #     with open("meta.csv", 'a') as csv_file:
                #         csv_file.write(str(flickering_freq)+', '+str(phase_offset) + ', ' + str(time.time()) + '\n')
                fixation.draw()
                trial_text.draw()
                photosensor.color = (-1, -1, -1)
                if use_photosensor:
                    photosensor.draw()
                win.flip()
            # 'stim_duration' seconds stimulation using flashing frequency approximation:
            phase_offset_str = str(phase_offset)
            phase_offset += 0.00001 # nudge phase slightly from points of sudden jumps for offsets that are pi multiples
            stim_duration_frames = ms_to_frame((stim_duration+after_stim_padding)*1000, refresh_rate) # total number of frames for the stimulation
            frame_indices = np.arange(stim_duration_frames) # the frames as integer indices
            if flash_mode == 'square': # if we want to use binarized square wave visual stimuli
                trial = signal.square(2 * np.pi * flickering_freq * (frame_indices / refresh_rate) + phase_offset * np.pi) # frequency approximation formula
                for i_frame,frame in enumerate(trial): # present the stimulation frame by frame
                    if i_frame == 0:
                        with open("meta.csv", 'a') as csv_file:
                            # csv_file.write(str(flickering_freq)+', '+phase_offset_str + ', ' + str(time.time()) + '\n')
                            csv_file.write(str(flickering_freq)+', '+phase_offset_str + ', ' + str(local_clock()) + '\n')
                        if use_dsi_trigger and (use_dsi_lsl or use_dsi7): # send trigger signal to the trigger channel
                            msg = b'\x01\xe1\x01\x00\x01'
                            dsi_serial.write(msg)
                    square.color = (frame, frame, frame)
                    square.draw()
                    # photosensor.color = (frame, frame, frame)
                    photosensor.color = (1, 1, 1)
                    if use_photosensor:
                        photosensor.draw()
                    win.flip()
            elif flash_mode == 'sine': # if we want to use smoothed sine wave visual stimuli
                trial = np.sin(2 * np.pi * flickering_freq * (frame_indices / refresh_rate) + phase_offset * np.pi) # frequency approximation formula
                for frame in trial: # present the stimulation frame by frame
                    square.color = (frame, frame, frame)
                    square.draw()
                    photosensor.color = (frame, frame, frame)
                    if use_photosensor:
                        photosensor.draw()
                    win.flip()
            elif flash_mode == 'chirp':
                frame_times = np.linspace(0,stim_duration,int(stim_duration*refresh_rate))
                trial = signal.chirp(frame_times, f0=10, f1=14, t1=5, method='linear')
                for frame in trial: # present the stimulation frame by frame
                    square.color = (frame, frame, frame)
                    square.draw()
                    win.flip()
            elif flash_mode == 'dual band':
                flickering_freq2 = phase_offset
                phase_offset = 0.00001
                trial = signal.square(2 * np.pi * flickering_freq * (frame_indices / refresh_rate) + phase_offset * np.pi) # frequency approximation formula
                trial += signal.square(2 * np.pi * flickering_freq2 * (frame_indices / refresh_rate) + phase_offset * np.pi) # frequency approximation formula
                trial /= 2
                for frame in trial: # present the stimulation frame by frame
                    square.color = (frame, frame, frame)
                    square.draw()
                    win.flip()
    if keyboard_flash: # if we want the visual stimuli to be presented in the keyboard layout
        flickering_keyboard = create_keyboard()
        # flickering_keyboard = create_9_keys()
        stim_duration_frames = ms_to_frame((stim_duration)*1000, refresh_rate) # total number of frames for the stimulation
        frame_indices = np.arange(stim_duration_frames) # the frames as integer indices
        flickering_frames = np.zeros((len(frame_indices),32))
        for i_class,(flickering_freq,phase_offset) in enumerate(keyboard_classes):
            phase_offset += .00001 # nudge phase slightly from points of sudden jumps for offsets that are pi multiples
            flickering_frames[:,i_class] = signal.square(2 * np.pi * flickering_freq * (frame_indices / refresh_rate) + phase_offset * np.pi) # frequency approximation formula
        sequence = create_trial_sequence(n_per_class=n_per_class,classes=classes)
        
        for i_trial,(flickering_freq, phase_offset) in enumerate(sequence): # for each trial in the trail sequence
            # class_num = (flickering_freq-8)*4+phase_offset/0.5
            class_num = keyboard_classes.index((flickering_freq, phase_offset))
            # print(class_num)
            phase_offset_str = str(phase_offset)
            keys = kb.getKeys() 
            for thisKey in keys:
                if thisKey=='escape':
                    if use_dsi_lsl:
                        for inlet in inlets:
                            inlet.close_stream()
                        os.kill(p.pid, sig.CTRL_C_EVENT)
                        with open("eeg.csv", 'a') as csv_file:
                            np.savetxt(csv_file, eeg, delimiter=', ')
                    if use_cyton:
                        for inlet in inlets:
                            inlet.close_stream()
                        stop_cyton.set()
                        board.stop_stream()
                        with open("eeg.csv", 'a') as csv_file:
                            np.savetxt(csv_file, eeg, delimiter=', ')
                    core.quit()
            for frame in range(ms_to_frame(isi_duration*1000, refresh_rate)):
                for i_key,key in enumerate(flickering_keyboard):
                    if i_key == class_num:
                        key.color = (1,1,1)
                    else:
                        key.color = (-1,-1,-1)
                    key.draw()
                win.flip()
            # last_flip = win.getFutureFlipTime()
            iter_frame = iter(enumerate(flickering_frames))
            next_flip = win.getFutureFlipTime()
            for i_frame,frame in iter_frame:
                key_counter = 0
                # next_flip = win.getFutureFlipTime()
                # while next_flip == last_flip:
                #     next_flip = win.getFutureFlipTime()
                iter_keyboard = iter(enumerate(zip(flickering_keyboard,frame)))
                for i_key,(key, key_frame) in iter_keyboard:
                    # if i_key == class_num:
                    #     key.color = (key_frame,key_frame,key_frame)
                    #     key.draw()
                    # else:
                    #     # key.color = (-1,-1,-1)
                    #     key.color = (key_frame,key_frame,key_frame)
                    #     if key_counter < 9:
                    #         key.draw()
                    #         key_counter += 1
                    key.color = (key_frame,key_frame,key_frame)
                    key.draw()
                    if core.getTime() > (next_flip + 0.004):
                        break
                # if core.getTime() > (next_flip):
                if core.getTime() > (next_flip + 0.004):
                    n_skip = int((core.getTime()-next_flip )/0.016696429999137764)+1
                    print(str(i_trial)+', '+str(i_frame)+', '+str(n_skip))
                    next(islice(iter_frame, n_skip,n_skip), None)
                win.flip()
                next_flip = win.getFutureFlipTime()
                    # for i in range(n_skip):
                    #     next(iter_frame, None)
                # else:
                #     win.clearBuffer()
                    # last_flip = next_flip
                # print(win.getFutureFlipTime())
                # print(core.getTime())
                # print(win.monitorFramePeriod)
                if i_frame == 0:
                    if use_dsi_trigger and (use_dsi_lsl or use_dsi7):
                        msg = b'\x01\xe1\x01\x00\x01'
                        dsi_serial.write(msg)
                    # else:
                    #     with open("meta.csv", 'a') as csv_file:
                    #         # csv_file.write(str(flickering_freq)+', '+phase_offset_str + ', ' + str(time.time()) + '\n')
                    #         csv_file.write(str(flickering_freq)+', '+str(phase_offset) + ', ' + str(local_clock()) + '\n')
                    with open("meta.csv", 'a') as csv_file:
                        csv_file.write(str(flickering_freq)+', '+str(phase_offset) + ', ' + str(local_clock()) + '\n')
            # print(win.getMsPerFrame())
        # if use_dsi_trigger and (use_dsi_lsl or use_dsi7):
        #     for i_trial,(flickering_freq, phase_offset) in enumerate(sequence):
        #         with open("meta.csv", 'a') as csv_file:
        #             # csv_file.write(str(flickering_freq)+', '+phase_offset_str + ', ' + str(time.time()) + '\n')
        #             csv_file.write(str(flickering_freq)+', '+str(phase_offset) + ', ' + str(local_clock()) + '\n')
    time.sleep(5)
    
    if use_dsi_lsl:
        for inlet in inlets:
            inlet.close_stream()
        os.kill(p.pid, sig.CTRL_C_EVENT)
        with open("eeg.csv", 'a') as csv_file:
            np.savetxt(csv_file, eeg, delimiter=', ')
    if use_cyton:
        with open("eeg.csv", 'a') as csv_file:
            np.savetxt(csv_file, eeg, delimiter=', ')
    core.quit()


