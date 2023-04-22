"""
SSVEP Offline + Realtime Experiment

Notes:
- Press esc to quit
- MAKE SURE refresh_rate IS SET TO YOUR MONITOR'S REFRESH RATE
- set use_dsi_lsl and make_predictions to True for regular use
- set use_dsi_lsl and make_predictions to False and dummy_mode to True for dummy mode
"""

from psychopy import visual, core
from psychopy.hardware import keyboard
import numpy as np
from scipy import signal
import yaml
import json
import random
import sys, time, serial, pickle
from pylsl import local_clock

sys.path.append('src')  # if run from the root project directory

# █████████████████████████████████████████████████████████████████████████████


## VARIABLES
use_dsi7 = False
use_dsi_trigger = True
use_dsi_lsl = True
use_arduino = False  # arduino photosensor for flashing timing test
use_cyton = False
use_photosensor = False
record_start_time = True
center_flash = False  # whether the visual stimuli are only presented at the center of the screen
test_mode = True  # whether the script indicates target squares and saves recorded data
home_screen = False
make_predictions = True  # whether the script makes predictions using a pretrained model
dummy_mode = True

model = None
if make_predictions:
    # with open("reports/trained_models/wsx32/fbtdca_1s.pkl", 'rb') as filehandler:
    # with open("reports/trained_models/32-class_speller/DSI-7/Simon/fbtdca_1s6t.pkl", 'rb') as filehandler:
    with open("reports/trained_models/32-class_speller/DSI-24/Aidan/fbtdca_1s.pkl", 'rb') as filehandler:
        model = pickle.load(filehandler)
shuffled_positions = False
shuffled_initial_positions = False
random_positions = False
random_movements = False
random_linear_movements = False
width = 1536
height = 864
flash_mode = 'square'  # 'sine', 'square', or 'chirp', 'dual band'
refresh_rate = 60.02  # refresh rate of the monitor
use_retina = False  # whether the monitor is a retina display
stim_duration = 1.2  # in seconds
isi_duration = 1  # in seconds, used both pre and post stimulations
after_stim_padding = 0.0  # in seconds, stim remains but the data is discarded
n_per_class = 2
keyboard_classes = [(8, 0), (8, 0.5), (8, 1), (8, 1.5),
                    (9, 0), (9, 0.5), (9, 1), (9, 1.5),
                    (10, 0), (10, 0.5), (10, 1), (10, 1.5),
                    (11, 0), (11, 0.5), (11, 1), (11, 1.5),
                    (12, 0), (12, 0.5), (12, 1), (12, 1.5),
                    (13, 0), (13, 0.5), (13, 1), (13, 1.5),
                    (14, 0), (14, 0.5), (14, 1), (14, 1.5),
                    (15, 0), (15, 0.5), (15, 1), (15, 1.5), ]
dummy_keyboard_string = '1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,'

# keyboard_classes=[( 8,0),( 8,0.5),( 8,1),
#          (10,0),(10,0.5),(10,1),
#          (15,0),(15,0.5),(15,1),]

n_keyboard_classes = len(keyboard_classes)
# classes=[(8,0),(9,1.75),(10,1.5),(11,1.25),(12,1),(13,0.75),(14,0.5),(15,0.25),
#         (8.2,0.35),(9.2,0.1),(10.2,1.85),(11.2,1.6),(12.2,1.35),(13.2,1.1),(14.2,0.85),(15.2,0.6),
#         (8.4,0.7),(9.4,0.45),(10.4,0.2),(11.4,1.95),(12.4,1.7),(13.4,1.45),(14.4,1.2),(15.4,0.95),
#         (8.6,1.05),(9.6,0.8),(10.6,0.55),(11.6,0.3),(12.6,0.05),(13.6,1.8),(14.6,1.55),(15.6,1.3),
#         (8.8,1.4),(9.8,1.15),(10.8,0.9),(11.8,0.65),(12.8,0.4),(13.8,0.15),(14.8,1.9),(15.8,1.65)]
classes = keyboard_classes
data = []
run_count = 0
first_call = True


# █████████████████████████████████████████████████████████████████████████████

## FUNCTIONS

def get_content(dir="states/front_to_back.yaml", use_yaml=True):
    if use_yaml:
        with open(dir, "r") as file:
            try:
                content = yaml.safe_load(file)
                return content
            except yaml.YAMLError as exc:
                print(exc)
    else:
        with open(dir, "r") as file:
            content = json.load(file)
            return content

def parse_chat_history(json_obj : dict):
    chat_history_text = ''
    content_list = json_obj['content']
    line_count = 0
    max_lines = 15
    msg_start_ind = -1
    for i_msg, msg in reversed(list(enumerate(content_list))):
        n_lines = int(msg['n_lines'])
        line_count += n_lines
        if line_count <= max_lines:
            msg_start_ind = i_msg
        else:
            break
    content_list = content_list[msg_start_ind:]
    for i_msg, msg in enumerate(content_list):
        if i_msg != 0:
            chat_history_text += '\n'
        chat_history_text += msg['sender']
        chat_history_text += '    '
        chat_history_text += msg['timestamp']
        chat_history_text += '\n'
        chat_history_text += msg['text']
        chat_history_text += '\n'
    return chat_history_text

def update_text(new_text: str):
    content = get_content()
    with open("states/front_to_back.yaml", "w") as file:
        try:
            content['text'] += new_text
            yaml.dump(content, file)
        except yaml.YAMLError as exc:
            print(exc)


def create_fixation_cross(size=50):
    return visual.ShapeStim(
        win=win,
        units='pix',
        size=size,
        fillColor=[1, 1, 1],
        lineColor=[1, 1, 1],
        lineWidth=1,
        vertices='cross',
        name='off',  # Used to determine state
        pos=[0, 0]
    )


def ms_to_frame(ms, fs):
    dt = 1000 / fs
    return np.round(ms / dt).astype(int)


def create_flickering_square(size=120, pos=[0, 0], color='white'):
    return visual.Rect(
        win=win,
        units="pix",
        width=size,
        height=size,
        fillColor=color,
        # lineColor='white',
        interpolate=False,
        lineWidth=0,
        pos=pos
    )


def create_photosensor_dot(size=100):
    return visual.Circle(
        win=win,
        units="pix",
        radius=size,
        fillColor='white',
        lineColor='white',
        lineWidth=1,
        edges=32,
        pos=(-(win_w / 2) + size, -((win_h / 2) - size))
    )


def create_trial_sequence(n_per_class, classes=[(7.5, 0), (8.57, 0), (10, 0), (12, 0), (15, 0)]):
    """
    Create a random sequence of trials with n_per_class of each class
    Inputs:
        n_per_class : number of trials for each class
    Outputs:
        seq : (list of len(10 * n_per_class)) the trial sequence
    """
    seq = classes * n_per_class
    random.seed()
    random.shuffle(seq)  # shuffles in-place
    return seq


def create_keyboard():
    keyboard = []
    keyboard.extend(
        [create_flickering_square(pos=[-width / 2 + 90 + i * 150, height / 2 - 90 - 200]) for i in range(10)])
    keyboard.extend(
        [create_flickering_square(pos=[-width / 2 + 90 + 70 + i * 150, height / 2 - 90 - 150 - 200]) for i in range(9)])
    keyboard.extend(
        [create_flickering_square(pos=[-width / 2 + 90 + 140 + i * 150, height / 2 - 90 - 300 - 200]) for i in
         range(8)])
    keyboard.extend([create_flickering_square(pos=[-width / 2 + 90 + 210, height / 2 - 90 - 450 - 200])])
    keyboard.extend([visual.Rect(win=win, units='pix', width=100 * 5, height=100, fillColor='white', lineWidth=0,
                                 pos=[-width / 2 + 130 * 5 + 70, height / 2 - 90 - 450 - 200])])
    keyboard.extend(
        [create_flickering_square(pos=[-width / 2 + 90 + 70 * 15 + i * 150, height / 2 - 90 - 450 - 200]) for i in
         range(3)])
    return keyboard


def create_9_keys(size=120, colors=[-1, -1, -1] * 9):
    positions = []
    positions.extend([[-width / 2 + 300, height / 2 - 90 - i * 270 - 80] for i in range(3)])
    positions.extend([[-width / 2 + 450 + 300, height / 2 - 90 - i * 270 - 80] for i in range(3)])
    positions.extend([[-width / 2 + 900 + 300, height / 2 - 90 - i * 270 - 80] for i in range(3)])
    keys = visual.ElementArrayStim(win, nElements=9, elementTex=None, elementMask=None, units='pix', sizes=[size, size],
                                   xys=positions, colors=colors)
    return keys


def create_12_keys(size=120, colors=[-1, -1, -1] * 12):
    positions = []
    positions.extend([[-width / 2 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 450 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 900 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    keys = visual.ElementArrayStim(win, nElements=12, elementTex=None, elementMask=None, units='pix',
                                   sizes=[size, size], xys=positions, colors=colors)
    return keys


def create_16_keys(size=120, colors=[-1, -1, -1] * 16):
    positions = []
    positions.extend([[-width / 2 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 200 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 400 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 600 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    keys = visual.ElementArrayStim(win, nElements=16, elementTex=None, elementMask=None, units='pix',
                                   sizes=[size, size], xys=positions, colors=colors)
    return keys


def create_20_keys(size=120, colors=[-1, -1, -1] * 20):
    positions = []
    positions.extend([[-width / 2 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 200 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 400 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 600 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 800 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    keys = visual.ElementArrayStim(win, nElements=20, elementTex=None, elementMask=None, units='pix',
                                   sizes=[size, size], xys=positions, colors=colors)
    return keys


def create_24_keys(size=120, colors=[-1, -1, -1] * 24):
    positions = []
    positions.extend([[-width / 2 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 200 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 400 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 600 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 800 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 1000 + 300, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    keys = visual.ElementArrayStim(win, nElements=24, elementTex=None, elementMask=None, units='pix',
                                   sizes=[size, size], xys=positions, colors=colors)
    return keys


def create_28_keys(size=120, colors=[-1, -1, -1] * 28):
    positions = []
    positions.extend([[-width / 2 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 200 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 400 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 600 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 800 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 1000 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 1200 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    keys = visual.ElementArrayStim(win, nElements=28, elementTex=None, elementMask=None, units='pix',
                                   sizes=[size, size], xys=positions, colors=colors)
    return keys


def create_32_keys(size=120, colors=[-1, -1, -1] * 33):
    positions = []
    positions.extend([[-width / 2 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 1 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 2 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 3 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 4 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 5 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 6 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 7 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[width / 2 - 40, height / 2 - 40]])
    keys = visual.ElementArrayStim(win, nElements=33, elementTex=None, elementMask=None, units='pix',
                                   sizes=[size, size], xys=positions, colors=colors)
    return keys


def create_key_caps(text_strip, el_mask, phases, colors=[-1, -1, -1] * 26):
    positions = []
    positions.extend([[-width / 2 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 1 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 2 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 3 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 4 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 5 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 6 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[-width / 2 + 190 * 7 + 100, height / 2 - 90 - i * 200 - 80] for i in range(4)])
    positions.extend([[width / 2 - 40, height / 2 - 40]])
    els = visual.ElementArrayStim(
        win=win,
        units="pix",
        nElements=33,
        sizes=text_strip.shape,
        xys=positions,
        phases=phases,
        colors=colors,
        elementTex=text_strip,
        elementMask=el_mask)
    return els


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
                while inlet_idx < len(inlets):  # iterate through the inlets
                    sample, timestamp = inlets[inlet_idx].pull_sample()
                    if record_start_time:
                        with open("meta.csv", 'w') as csv_file:
                            csv_file.write('0,0,' + str(local_clock()) + '\n')
                        record_start_time = False
                    if (sample, timestamp) != (None, None):
                        if inlet_idx is (len(inlets) - 1):
                            row_data[0] = timestamp
                        row_data.extend(sample)
                        inlet_idx += 1  # move on to next inlet
                    else:
                        time.sleep(0.0001)  # wait for 0.1 ms if the data is not there yet
                        # just to save some processing power
                save_variable.append(row_data)

        pull_thread = Thread(target=save_sample, args=(inlets, save_variable))
        pull_thread.daemon = True
        # pull_thread = Process(target = save_sample, args=(inlets, save_variable,), daemon=True)
        pull_thread.start()
        return inlets, pull_thread


    # p = Popen([os.path.join(os.getcwd(), 'src', 'dsi2lsl-win', 'dsi2lsl.exe'), '--port=COM8',
    # '--lsl-stream-name=mystream'],shell=True,stdin=PIPE) #COM4 or 8 for dsi-7 or COM12 for dsi-24
    p = Popen(
        [os.path.join(os.getcwd(), 'src', 'dsi2lsl-win', 'dsi2lsl.exe'), '--port=COM7', '--lsl-stream-name=mystream'],
        shell=True, stdin=PIPE)  # COM4 or 8 for dsi-7 or COM12 for dsi-24
    with open("eeg.csv", 'w') as csv_file:
        # csv_file.write('time, Pz, F4, C4, P4, P3, C3, F3, TRG\n') # For DSI-7
        csv_file.write(
            'time, P3, C3, F3, Fz, F4, C4, P4, Cz, Pz, Fp1, Fp2, T3, T5, O1, O2, X3, X2, F7, F8, X1, A2, T6, T4, '
            'TRG\n')  # For DSI-24
    with open("meta.csv", 'w') as csv_file:
        csv_file.write('')
    time.sleep(15)
    if use_dsi_trigger:
        # dsi_serial = serial.Serial('COM2',115200) # 2 for serial trigger or 13 for trigger hub
        dsi_serial = serial.Serial('COM8', 9600)  # 2 for serial trigger or 13 for trigger hub
    eeg = []  # receive_data() saves [timepoints by channels] here
    print(resolve_streams())
    inlets, _ = get_lsl_data(eeg)

# █████████████████████████████████████████████████████████████████████████████

## DSI-7
if use_dsi7:
    import dsi, ctypes, multiprocessing, threading, serial

    SampleCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_double, ctypes.c_void_p)


    @SampleCallback
    def ExampleSampleCallback_Signals(headsetPtr, packetTime, userData):
        global run_count
        global data
        global first_call
        h = dsi.Headset(headsetPtr)
        sample_data = [packetTime]  # time stamp
        sample_data.extend([ch.ReadBuffered() for ch in h.Channels()])  # channel voltages
        data.append(sample_data)
        run_count += 1
        if first_call:
            if sample_data[1] > 1e15:  # if Pz saturation error happens
                quit()
            with open("meta.csv", 'w') as csv_file:
                # csv_file.write(str(time.time()) + '\n')
                csv_file.write('0,0,' + str(local_clock()) + '\n')
            first_call = False
        if run_count >= 300:  # save data every second
            run_count = 0
            data_np = np.array(data)
            with open("eeg.csv", 'a') as csv_file:
                np.savetxt(csv_file, data_np, delimiter=',')
            data = []


    def record():
        args = getattr(sys, 'argv', [''])
        if sys.platform.lower().startswith('win'):
            default_port = 'COM8'  # COM4, COM8, COM9
        else:
            default_port = '/dev/cu.DSI7-0009.BluetoothSeri'
        # first command-line argument: serial port address
        if len(args) > 1:
            port = args[1]
        else:
            port = default_port
        # second command-line argument:  name of the Source to be used as reference, or the word 'impedances'
        if len(args) > 2:
            ref = args[2]
        else:
            ref = ''
        headset = dsi.Headset()
        headset.Connect(port)
        headset.SetSampleCallback(ExampleSampleCallback_Signals, 0)
        headset.StartDataAcquisition()
        with open("eeg.csv", 'w') as csv_file:
            csv_file.write('time, ' + ', '.join([ch.GetName() for ch in headset.Channels()]) + '\n')
        while True:
            headset.Idle(2.0)


    if __name__ == "__main__":
        # recording = multiprocessing.Process(target=record,daemon=True)
        recording = threading.Thread(target=record, daemon=True)
        recording.start()
        if use_dsi_trigger:
            dsi_serial = serial.Serial('COM2', 115200)
        time.sleep(10)

# █████████████████████████████████████████████████████████████████████████████

## Arduino Photosensor for Timing
if use_arduino:
    from sys import executable
    import os
    from subprocess import Popen

    # Popen([executable,  os.path.join(os.getcwd(), 'run_arduino_photosensor.py')])
    Popen([executable, os.path.join(os.getcwd(), 'scripts', 'run_arduino_photosensor.py')])
    time.sleep(2)

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
    ANALOGUE_MODE = '/2'  # Reads from analog pins A5(D11), A6(D12) and if no


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
                    datachunk.append(eeg_data[:, i].tolist())
                stamp = local_clock()
                outlet_eeg.push_chunk(datachunk, stamp)
                sent_eeg += required_eeg_samples

                required_aux_samples = int(250 * elapsed_time) - sent_aux
                aux_data = data_from_board[board.get_analog_channels(CYTON_BOARD_ID)]
                datachunk = []
                for i in range(len(aux_data[0])):
                    datachunk.append(aux_data[:, i].tolist())
                stamp = local_clock()
                outlet_aux.push_chunk(datachunk, stamp)
                sent_aux += required_aux_samples

                time.sleep(0.02)  # 20 ms

        push_thread = Thread(target=push_sample)
        push_thread.start()
        return board, stop_event


    def get_lsl_data(save_variable, types=['EEG', 'AUX']):
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
                while inlet_idx < len(inlets):  # iterate through the inlets
                    sample, timestamp = inlets[inlet_idx].pull_sample()
                    if record_start_time:
                        with open("meta.csv", 'w') as csv_file:
                            csv_file.write('0,0,' + str(local_clock()) + '\n')
                        record_start_time = False
                    if (sample, timestamp) != (None, None):
                        if inlet_idx is (len(inlets) - 1):
                            row_data[0] = timestamp
                        row_data.extend(sample)
                        inlet_idx += 1  # move on to next inlet
                    else:
                        time.sleep(0.0001)  # wait for 0.1 ms if the data is not there yet
                        # just to save some processing power
                save_variable.append(row_data)

        pull_thread = Thread(target=save_sample, args=(inlets, save_variable))
        pull_thread.daemon = True
        pull_thread.start()
        return inlets, pull_thread


    with open("eeg.csv", 'w') as csv_file:
        csv_file.write('time, N1P, N2P, N3P, N4P, N5P, N6P, N7P, N8P, D11, D12, D13\n')
    with open("meta.csv", 'w') as csv_file:
        csv_file.write('')
    eeg = []  # receive_data() saves [timepoints by channels] here
    # where channels are length 12 [timestamp, 8 EEG Channels, 3 AUX channels]
    board, stop_cyton = start_cyton_lsl()
    inlets, _ = get_lsl_data(eeg)

# █████████████████████████████████████████████████████████████████████████████

## Keyboard
if True:
    import string
    import numpy as np
    import psychopy.visual
    import psychopy.event
    from psychopy import core

    # letters = string.ascii_letters[:26]
    # letters += '⌂'
    # letters += '⎵'
    # letters += ','
    # letters += '.'
    # letters += '↨'
    # letters += '⌫'
    # letters += ' '
    # letters = 'AIQYBJRZCKS⌂DLT⎵EMU,FNV.GOW↨HPX⌫ '
    # letters = 'AIQYBJRZCKS⌂DLT⎵EMU,FNV.GOW⤒HPX⌫ '
    # letters = 'AIQYBJRZCKS⌂D⌫T⎵EMU,FNV.GOW⤒HPXL '
    letters = 'AIQYBJRZCKS⌂D⌫T⎵EMULFNV.GOW⤒HPX, '
    # letters2 = '19/+2(~-3)$⌂4:%=5;&<6"*>7!#↨8?⮐⌫ '
    # letters2 = '19/+2(~-3)$⌂4:%=5;&<6"*>7!#⤓8?⮐⌫ '
    # letters2 = '19/+2(~-3)$\'4⌫%=5;&<6"*>7!#⤓8?⮐: '
    letters2 = '19/+2(~-3)$;4⌫%=5\'&<6"*>7!#⤓8?⮐: '
    letters3 = '12341234123412341234⏳⌚⏰ ⎚⏩ ⌨✉⏪ ⌫ '
    # letters3 = '12341234123412341234⑮⌚⏰ ⎚⏩ ⌨✉⏪ ⌫ '
    win = psychopy.visual.Window(
        size=(800, 800),
        units="pix",
        fullscr=False)
    n_text = 33
    text_cap_size = 119  # 34
    text_strip_height = n_text * text_cap_size
    text_strip = np.full((text_strip_height, text_cap_size), np.nan)
    text_strip2 = np.full((text_strip_height, text_cap_size), np.nan)
    text_strip3 = np.full((text_strip_height, text_cap_size), np.nan)
    text = psychopy.visual.TextStim(win=win, height=60, font="Courier")
    text2 = psychopy.visual.TextStim(win=win, height=60, font="Courier")
    text3 = psychopy.visual.TextStim(win=win, height=60, font="Courier")
    cap_rect_norm = [-(text_cap_size / 2.0) / (win.size[0] / 2.0),  # left
                     +(text_cap_size / 2.0) / (win.size[1] / 2.0),  # top
                     +(text_cap_size / 2.0) / (win.size[0] / 2.0),  # right
                     -(text_cap_size / 2.0) / (win.size[1] / 2.0)]  # bottom

    # capture the rendering of each letter
    for (i_letter, letter) in enumerate(letters):
        text.text = letter.upper()
        buff = psychopy.visual.BufferImageStim(
            win=win,
            stim=[text],
            rect=cap_rect_norm)
        i_rows = slice(i_letter * text_cap_size,
                       i_letter * text_cap_size + text_cap_size)
        text_strip[i_rows, :] = (np.flipud(np.array(buff.image)[..., 0]) / 255.0 * 2.0 - 1.0)

    # capture the rendering of each letter
    for (i_letter, letter) in enumerate(letters2):
        text2.text = letter.upper()
        buff = psychopy.visual.BufferImageStim(
            win=win,
            stim=[text2],
            rect=cap_rect_norm)
        i_rows = slice(i_letter * text_cap_size,
                       i_letter * text_cap_size + text_cap_size)
        text_strip2[i_rows, :] = (np.flipud(np.array(buff.image)[..., 0]) / 255.0 * 2.0 - 1.0)

    # capture the rendering of each letter
    for (i_letter, letter) in enumerate(letters3):
        text3.text = letter.upper()
        buff = psychopy.visual.BufferImageStim(
            win=win,
            stim=[text3],
            rect=cap_rect_norm)
        i_rows = slice(i_letter * text_cap_size,
                       i_letter * text_cap_size + text_cap_size)
        text_strip3[i_rows, :] = (np.flipud(np.array(buff.image)[..., 0]) / 255.0 * 2.0 - 1.0)

    # need to pad 'text_strip' to pow2 to use as a texture
    new_size = max([int(np.power(2, np.ceil(np.log(dim_size) / np.log(2))))
                    for dim_size in text_strip.shape])
    pad_amounts = []
    for i_dim in range(2):
        first_offset = int((new_size - text_strip.shape[i_dim]) / 2.0)
        second_offset = new_size - text_strip.shape[i_dim] - first_offset
        pad_amounts.append([first_offset, second_offset])
    text_strip = np.pad(
        array=text_strip,
        pad_width=pad_amounts,
        mode="constant",
        constant_values=0.0)
    text_strip = (text_strip - 1) * -1  # invert the texture mapping

    text_strip2 = np.pad(
        array=text_strip2,
        pad_width=pad_amounts,
        mode="constant",
        constant_values=0.0)
    text_strip2 = (text_strip2 - 1) * -1  # invert the texture mapping

    text_strip3 = np.pad(
        array=text_strip3,
        pad_width=pad_amounts,
        mode="constant",
        constant_values=0.0)
    text_strip3 = (text_strip3 - 1) * -1  # invert the texture mapping

    # make a central mask to show just one letter
    el_mask = np.ones(text_strip.shape) * -1.0
    # start by putting the visible section in the corner
    el_mask[:text_cap_size, :text_cap_size] = 1.0

    # then roll to the middle
    el_mask = np.roll(el_mask,
                      (int(new_size / 2 - text_cap_size / 2),) * 2,
                      axis=(0, 1))

    # make a central mask to show just one letter
    el_mask2 = np.ones(text_strip2.shape) * -1.0
    # start by putting the visible section in the corner
    el_mask2[:text_cap_size, :text_cap_size] = 1.0

    # then roll to the middle
    el_mask2 = np.roll(el_mask2,
                       (int(new_size / 2 - text_cap_size / 2),) * 2,
                       axis=(0, 1))

    # make a central mask to show just one letter
    el_mask3 = np.ones(text_strip3.shape) * -1.0
    # start by putting the visible section in the corner
    el_mask3[:text_cap_size, :text_cap_size] = 1.0

    # then roll to the middle
    el_mask3 = np.roll(el_mask3,
                       (int(new_size / 2 - text_cap_size / 2),) * 2,
                       axis=(0, 1))

    # work out the phase offsets for the different letters
    base_phase = ((text_cap_size * (n_text / 2.0)) - (text_cap_size / 2.0)) / new_size

    phase_inc = (text_cap_size) / float(new_size)

    phases = np.array([
        (0.0, base_phase - i_letter * phase_inc)
        for i_letter in range(n_text)])
    win.close()

# █████████████████████████████████████████████████████████████████████████████

## EXPERIMENT

# if this script is run as a script rather than imported
if __name__ == "__main__":
    kb = keyboard.Keyboard()
    win = visual.Window(
        size=[1920, 1080],
        checkTiming=True,
        allowGUI=False,
        fullscr=True,
        useRetina=use_retina
    )
    [win_w, win_h] = win.size
    if use_retina:
        win_w, win_h = win_w / 2, win_h / 2
    if center_flash:  # if we want the visual stimuli to be only presented at the center of the screen
        fixation = create_fixation_cross()
        square = create_flickering_square()
        photosensor = create_photosensor_dot()
        sequence = create_trial_sequence(n_per_class=n_per_class, classes=classes)
        # square.color = (0, 1, 0)
        for i_trial, (flickering_freq, phase_offset) in enumerate(sequence):  # for each trial in the trail sequence
            keys = kb.getKeys()
            for thisKey in keys:
                if thisKey == 'escape':
                    if use_dsi_lsl:
                        for inlet in inlets:
                            inlet.close_stream()
                        os.kill(p.pid, sig.CTRL_C_EVENT)
                        with open("eeg.csv", 'a') as csv_file:
                            np.savetxt(csv_file, eeg, delimiter=',')
                    if use_cyton:
                        for inlet in inlets:
                            inlet.close_stream()
                        stop_cyton.set()
                        board.stop_stream()
                        with open("eeg.csv", 'a') as csv_file:
                            np.savetxt(csv_file, eeg, delimiter=',')
                    core.quit()
            trial_text = visual.TextStim(win, str(i_trial + 1) + '/' + str(len(sequence)), color=(-1, -1, -1),
                                         colorSpace='rgb')
            # 750ms fixation cross:
            for frame in range(ms_to_frame(isi_duration * 1000, refresh_rate)):
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
            phase_offset += 0.00001  # nudge phase slightly from points of sudden jumps for offsets that are pi
            # multiples
            stim_duration_frames = ms_to_frame((stim_duration + after_stim_padding) * 1000,
                                               refresh_rate)  # total number of frames for the stimulation
            frame_indices = np.arange(stim_duration_frames)  # the frames as integer indices
            if flash_mode == 'square':  # if we want to use binarized square wave visual stimuli
                trial = signal.square(2 * np.pi * flickering_freq * (
                            frame_indices / refresh_rate) + phase_offset * np.pi)  # frequency approximation formula
                for i_frame, frame in enumerate(trial):  # present the stimulation frame by frame
                    if i_frame == 0:
                        with open("meta.csv", 'a') as csv_file:
                            # csv_file.write(str(flickering_freq)+', '+phase_offset_str + ', ' + str(time.time()) +
                            # '\n')
                            csv_file.write(
                                str(flickering_freq) + ', ' + phase_offset_str + ', ' + str(local_clock()) + '\n')
                        if use_dsi_trigger and (use_dsi_lsl or use_dsi7):  # send trigger signal to the trigger channel
                            msg = b'\x01\xe1\x01\x00\x01'
                            dsi_serial.write(msg)
                    square.color = (frame, frame, frame)
                    square.draw()
                    # photosensor.color = (frame, frame, frame)
                    photosensor.color = (1, 1, 1)
                    if use_photosensor:
                        photosensor.draw()
                    win.flip()
            elif flash_mode == 'sine':  # if we want to use smoothed sine wave visual stimuli
                trial = np.sin(2 * np.pi * flickering_freq * (
                            frame_indices / refresh_rate) + phase_offset * np.pi)  # frequency approximation formula
                for frame in trial:  # present the stimulation frame by frame
                    square.color = (frame, frame, frame)
                    square.draw()
                    photosensor.color = (frame, frame, frame)
                    if use_photosensor:
                        photosensor.draw()
                    win.flip()
            elif flash_mode == 'chirp':
                frame_times = np.linspace(0, stim_duration, int(stim_duration * refresh_rate))
                trial = signal.chirp(frame_times, f0=10, f1=14, t1=5, method='linear')
                for frame in trial:  # present the stimulation frame by frame
                    square.color = (frame, frame, frame)
                    square.draw()
                    win.flip()
            elif flash_mode == 'dual band':
                flickering_freq2 = phase_offset
                phase_offset = 0.00001
                trial = signal.square(2 * np.pi * flickering_freq * (
                            frame_indices / refresh_rate) + phase_offset * np.pi)  # frequency approximation formula
                trial += signal.square(2 * np.pi * flickering_freq2 * (
                            frame_indices / refresh_rate) + phase_offset * np.pi)  # frequency approximation formula
                trial /= 2
                for frame in trial:  # present the stimulation frame by frame
                    square.color = (frame, frame, frame)
                    square.draw()
                    win.flip()

    flickering_keyboard = create_32_keys()
    flickering_keyboard_caps = create_key_caps(text_strip, el_mask, phases)
    flickering_keyboard_caps2 = create_key_caps(text_strip2, el_mask2, phases)
    flickering_keyboard_caps3 = create_key_caps(text_strip3, el_mask3, phases)
    orig_keyboard_position = np.copy(flickering_keyboard.xys)
    stim_duration_frames = ms_to_frame((stim_duration) * 1000,
                                       refresh_rate)  # total number of frames for the stimulation
    frame_indices = np.arange(stim_duration_frames)  # the frames as integer indices
    flickering_frames = np.zeros((len(frame_indices), n_keyboard_classes))
    linear_movement_vector = (np.random.random(size=[n_keyboard_classes, 2]) * 2 - 1) * 0.2
    if shuffled_initial_positions:
        np.random.seed(1)
        r_pos = np.copy(orig_keyboard_position)
        # print(np.where(r_pos[:, None] == orig_keyboard_position[None, :])[1])
        # print([ np.where(np.logical_and((orig_keyboard_position==x)[:,1], (orig_keyboard_position==x)[:,0])==True)[
        # 0][0] for x in r_pos])
        np.random.shuffle(r_pos[:-1])  # Multi-dimensional arrays are only shuffled along the first axis
        # print(orig_keyboard_position)
        # print([ np.where(np.logical_and((orig_keyboard_position==x)[:,1], (orig_keyboard_position==x)[:,0])==True)[
        # 0][0] for x in r_pos])
        # print(r_pos)
        flickering_keyboard.xys = r_pos
    for i_class, (flickering_freq, phase_offset) in enumerate(keyboard_classes):
        phase_offset += .00001  # nudge phase slightly from points of sudden jumps for offsets that are pi multiples
        flickering_frames[:, i_class] = signal.square(2 * np.pi * flickering_freq * (
                    frame_indices / refresh_rate) + phase_offset * np.pi)  # frequency approximation formula
    if test_mode:  # if we want the visual stimuli to be presented in the keyboard layout
        sequence = create_trial_sequence(n_per_class=n_per_class, classes=classes)
        n_correct = 0  # number of correct predictions made
        n_frameskip = 0
        eeg_temp = []
        for i in range(len(classes)):
            eeg_temp.append([])
        # trial_text = visual.TextStim(win, 'trial:'+str(1)+'/'+str(len(sequence)), color=(-1, -1, -1),
        # colorSpace='rgb', units='pix', pos=[-200,height/2-50])
        # trial_text.size = 50
        # acc_text = visual.TextStim(win, 'accuracy:'+str(n_correct/(1)*100)+'% ('+str(n_correct)+'/'+str(1)+')',
        # color=(-1, -1, -1), colorSpace='rgb', units='pix', pos=[200,height/2-50])
        # acc_text.size = 50
        for i_trial, (flickering_freq, phase_offset) in enumerate(sequence):  # for each trial in the trail sequence
            class_num = keyboard_classes.index((flickering_freq, phase_offset))
            trial_text = visual.TextStim(win, 'trial:' + str(i_trial + 1) + '/' + str(len(sequence)),
                                         color=(-1, -1, -1), colorSpace='rgb', units='pix', pos=[-200, height / 2 - 50])
            trial_text.size = 50
            # trial_text.autoDraw = True
            acc_text = visual.TextStim(win, 'accuracy:%3.2f' % (n_correct / (i_trial + 1) * 100) + '% (' + str(
                n_correct) + '/' + str(i_trial + 1) + ')', color=(-1, -1, -1), colorSpace='rgb', units='pix',
                                       pos=[200, height / 2 - 50])
            acc_text.size = 50
            # acc_text.autoDraw = True
            phase_offset_str = str(phase_offset)
            keys = kb.getKeys()
            for thisKey in keys:
                if thisKey == 'escape':
                    if use_dsi_lsl:
                        for inlet in inlets:
                            inlet.close_stream()
                        print(eeg)
                        os.kill(p.pid, sig.CTRL_C_EVENT)
                        with open("eeg.csv", 'a') as csv_file:
                            np.savetxt(csv_file, eeg, delimiter=',')
                    if use_cyton:
                        for inlet in inlets:
                            inlet.close_stream()
                        stop_cyton.set()
                        board.stop_stream()
                        with open("eeg.csv", 'a') as csv_file:
                            np.savetxt(csv_file, eeg, delimiter=',')
                    core.quit()
            key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
            key_colors[class_num] = [1, 1, 1]
            flickering_keyboard.colors = key_colors
            flickering_keyboard_caps.colors = key_colors
            if shuffled_positions:
                r_pos = np.copy(orig_keyboard_position)
                np.random.shuffle(r_pos[:-1])  # Multi-dimensional arrays are only shuffled along the first axis
                flickering_keyboard.xys = r_pos
            if random_positions:
                # r_pos = np.random.random(size = [n_keyboard_classes,2]) * 2 - 1
                # r_pos[:,0] *= width/2.5
                # r_pos[:,1] *= height/2.5
                # flickering_keyboard.xys = r_pos
                r_pos = np.copy(orig_keyboard_position)
                np.random.shuffle(r_pos)  # Multi-dimensional arrays are only shuffled along the first axis
                random_pos_offset = (np.random.random(size=[n_keyboard_classes + 1, 2]) * 2 - 1)
                random_pos_offset[:, 0] *= width / 25
                random_pos_offset[:, 1] *= height / 25
                r_pos += random_pos_offset
                flickering_keyboard.xys = r_pos

            for frame in range(ms_to_frame(isi_duration * (1 / 2) * 1000, refresh_rate)):
                trial_text.draw()
                acc_text.draw()
                # if random_movements:
                #     movement_vector = (np.random.random(size = [n_keyboard_classes,2]) * 2 - 1) * 1
                #     flickering_keyboard.xys += movement_vector
                # if random_linear_movements:
                #     flickering_keyboard.xys += linear_movement_vector
                # flickering_keyboard.draw()
                flickering_keyboard_caps.draw()
                win.flip()
            for frame in range(ms_to_frame(isi_duration * (1 / 2) * 1000, refresh_rate)):
                trial_text.draw()
                acc_text.draw()
                # if random_movements:
                #     movement_vector = (np.random.random(size = [n_keyboard_classes,2]) * 2 - 1) * 1
                #     flickering_keyboard.xys += movement_vector
                # if random_linear_movements:
                #     flickering_keyboard.xys += linear_movement_vector
                # flickering_keyboard.draw()
                flickering_keyboard.draw()
                win.flip()
            flash_successful = False
            frame_start_time = -1
            while (not flash_successful):
                # iter_frame = iter(enumerate(flickering_frames))
                # for i_frame,frame in iter_frame:
                for i_frame, frame in enumerate(flickering_frames):
                    frame = np.append(frame, 1)
                    next_flip = win.getFutureFlipTime()
                    trial_text.draw()
                    acc_text.draw()
                    if random_movements:
                        movement_vector = (np.random.random(size=[n_keyboard_classes, 2]) * 2 - 1) * 1
                        flickering_keyboard.xys += movement_vector
                    if random_linear_movements:
                        flickering_keyboard.xys += linear_movement_vector
                    flickering_keyboard.colors = np.array([frame] * 3).T
                    flickering_keyboard.draw()
                    if core.getTime() > next_flip:
                        if use_dsi_trigger and (use_dsi_lsl or use_dsi7):
                            # msg = b'\x01\xe1\x01\x00\x02'
                            msg = b'\x02'  # if use trigger hub
                            dsi_serial.write(msg)
                        n_frameskip += 1
                        print(str(n_frameskip) + '/' + str(i_trial + 1))
                        key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                        key_colors[class_num] = [1, -1, -1]
                        flickering_keyboard.colors = key_colors
                        for failure_frame in range(60):
                            flickering_keyboard.draw()
                            win.flip()
                        break
                    win.flip()

                    if i_frame == 0:
                        if use_dsi_trigger and (use_dsi_lsl or use_dsi7):
                            # msg = b'\x01\xe1\x01\x00\x01'
                            msg = b'\x01'  # if use trigger hub
                            dsi_serial.write(msg)
                        frame_start_time = local_clock()
                    if i_frame == stim_duration_frames - 1:
                        flash_successful = True
                        with open("meta.csv", 'a') as csv_file:
                            csv_file.write(
                                str(flickering_freq) + ', ' + str(phase_offset) + ', ' + str(frame_start_time) + '\n')
            key_colors = np.array([[1, 1, 1]] * (n_keyboard_classes + 1))
            # flickering_keyboard.colors = key_colors
            flickering_keyboard_caps.colors = key_colors
            prediction = [-1]
            if use_dsi_lsl and make_predictions:
                # trial_eeg = np.copy(eeg[-700:])
                time_window = -int(stim_duration * 300) - 200
                trial_eeg = np.copy(eeg[time_window:])
                if (len(np.where(trial_eeg[:, -1] == 2.0)[0]) == 0):  # 2.0 or 18.0
                    # print(trial_eeg[np.where(trial_eeg[:,-1]==16.0)[0][0]+40:,1:-1].T.shape)
                    # prediction = model.predict(trial_eeg[np.where(trial_eeg[:,-1]==1.0)[0][0]+40:,1:-1].T) # 1 or 16
                    dsi24chans = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 22, 23]
                    trial_start = np.where(trial_eeg[:, -1] == 16)[0][0] + 43
                    if trial_eeg[trial_start - 44, -1] != 0:
                        print(str(i_trial) + ':beginning not found1')
                    # trial_eeg = trial_eeg[trial_start:trial_start+600,dsi24chans].T
                    trial_eeg = trial_eeg[trial_start:trial_start + int(stim_duration * 300), dsi24chans].T
                    # print(trial_eeg.shape)
                    beginning_found = False
                    # while trial_eeg.shape[1] < 600:
                    while trial_eeg.shape[1] < int(stim_duration * 300):
                        # trial_eeg = np.copy(eeg[-700:])
                        trial_eeg = np.copy(eeg[time_window:])
                        trial_start = np.where(trial_eeg[:, -1] == 16)[0][0] + 43
                        if trial_eeg[trial_start - 44, -1] != 0:
                            # if trial_eeg[-1,trial_start-1] != 0:
                            beginning_found = False
                        else:
                            beginning_found = True
                        # trial_eeg = trial_eeg[trial_start:trial_start+600,dsi24chans].T
                        trial_eeg = trial_eeg[trial_start:trial_start + int(stim_duration * 300), dsi24chans].T
                    # print(trial_eeg.shape)
                    if not beginning_found:
                        print(str(i_trial) + ':beginning not found2')
                    eeg_temp[class_num].append(trial_eeg)
                    # prediction = model.predict(trial_eeg[np.where(trial_eeg[:,-1]==16)[0][0]+42:,dsi24chans].T)
                    prediction = model.predict(trial_eeg)
                    predited_class_num = keyboard_classes.index(classes[prediction[0]])
                    # print(prediction[0])
                    key_colors[predited_class_num] = [-1, 1, -1]
                    if prediction == class_num:
                        n_correct += 1
            for frame in range(ms_to_frame(isi_duration * (1 / 2) * 1000, refresh_rate)):
                trial_text.draw()
                acc_text.draw()
                # flickering_keyboard.draw()
                flickering_keyboard_caps.draw()
                win.flip()
        with open("eeg.csv", 'a') as csv_file:
            np.savetxt(csv_file, eeg, delimiter=',')  # finish save
        # eeg_np = np.array(eeg_temp).transpose(1, 0, 2, 3)

        # with open('eeg.npy', 'wb') as f:
        #     np.save(f, eeg_np)
        time.sleep(5)
    elif home_screen:
        n_frameskip = 0
        i_trial = 0
        while True:
            input_text = visual.TextStim(win,
                                         'adkjfb alsd bfkjsvbjkas dbfijdasb jkdbsfliaeh,askdkfnzkdfna \n alsdkncnas '
                                         'andlkanflk adlfkma asdflskf',
                                         color=(-1, -1, -1), colorSpace='rgb', units='pix', wrapWidth=850,
                                         pos=[-300, 0], alignText='left')
            input_text.size = 40
            i_trial += 1
            keys = kb.getKeys()
            for thisKey in keys:
                if thisKey == 'escape':
                    if use_dsi_lsl:
                        for inlet in inlets:
                            inlet.close_stream()
                        os.kill(p.pid, sig.CTRL_C_EVENT)
                        with open("eeg.csv", 'a') as csv_file:
                            np.savetxt(csv_file, eeg, delimiter=',')
                    if use_cyton:
                        for inlet in inlets:
                            inlet.close_stream()
                        stop_cyton.set()
                        board.stop_stream()
                        with open("eeg.csv", 'a') as csv_file:
                            np.savetxt(csv_file, eeg, delimiter=',')
                    core.quit()
            key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
            # flickering_keyboard.colors = key_colors
            key_colors[:20] = [0, 0, 0]
            flickering_keyboard_caps.colors = key_colors

            for frame in range(ms_to_frame(isi_duration * (1 / 2) * 1000, refresh_rate)):
                flickering_keyboard_caps.draw()
                input_text.draw()
                win.flip()
            key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
            key_colors[:-1] = [1, 1, 1]
            flickering_keyboard.colors = key_colors
            for frame in range(ms_to_frame(isi_duration * (1 / 2) * 1000, refresh_rate)):
                flickering_keyboard.draw()
                win.flip()
            flash_successful = False
            frame_start_time = -1
            while (not flash_successful):
                for i_frame, frame in enumerate(flickering_frames):
                    frame = np.append(frame, 1)
                    next_flip = win.getFutureFlipTime()
                    flickering_keyboard.colors = np.array([frame] * 3).T
                    flickering_keyboard.draw()
                    if core.getTime() > next_flip:
                        if use_dsi_trigger and (use_dsi_lsl or use_dsi7):
                            # msg = b'\x01\xe1\x01\x00\x02'
                            msg = b'\x02'  # if use trigger hub
                            dsi_serial.write(msg)
                        n_frameskip += 1
                        print(str(n_frameskip) + '/' + str(i_trial + 1))
                        key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                        key_colors[:-1] = [1, -1, -1]
                        # key_colors[class_num] = [1,-1,-1]
                        flickering_keyboard.colors = key_colors
                        for failure_frame in range(60):
                            flickering_keyboard.draw()
                            win.flip()
                        break
                    win.flip()

                    if i_frame == 0:
                        if use_dsi_trigger and (use_dsi_lsl or use_dsi7):
                            # msg = b'\x01\xe1\x01\x00\x01'
                            msg = b'\x01'  # if use trigger hub
                            dsi_serial.write(msg)
                        frame_start_time = local_clock()
                    if i_frame == stim_duration_frames - 1:
                        flash_successful = True
                        with open("meta.csv", 'a') as csv_file:
                            csv_file.write(
                                str(flickering_freq) + ', ' + str(phase_offset) + ', ' + str(frame_start_time) + '\n')
            key_colors = np.array([[1, 1, 1]] * (n_keyboard_classes + 1))
            key_colors[:20] = [0, 0, 0]
            flickering_keyboard_caps.colors = key_colors
            prediction = [-1]
            if use_dsi_lsl and make_predictions:
                time_window = -int(stim_duration * 300) - 200
                trial_eeg = np.copy(eeg[time_window:])
                if (len(np.where(trial_eeg[:, -1] == 2.0)[0]) == 0):  # 2.0 or 18.0
                    dsi24chans = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 22, 23]
                    trial_start = np.where(trial_eeg[:, -1] == 16)[0][0] + 43
                    if trial_eeg[trial_start - 44, -1] != 0:
                        print(str(i_trial) + ':beginning not found1')
                    trial_eeg = trial_eeg[trial_start:trial_start + int(stim_duration * 300), dsi24chans].T
                    beginning_found = False
                    while trial_eeg.shape[1] < int(stim_duration * 300):
                        trial_eeg = np.copy(eeg[time_window:])
                        trial_start = np.where(trial_eeg[:, -1] == 16)[0][0] + 43
                        if trial_eeg[trial_start - 44, -1] != 0:
                            beginning_found = False
                        else:
                            beginning_found = True
                        trial_eeg = trial_eeg[trial_start:trial_start + int(stim_duration * 300), dsi24chans].T
                    if not beginning_found:
                        print(str(i_trial) + ':beginning not found2')
                    prediction = model.predict(trial_eeg)
                    predited_class_num = keyboard_classes.index(classes[prediction[0]])
                    # print(prediction[0])
                    key_colors[predited_class_num] = [-1, 1, -1]
            for frame in range(ms_to_frame(isi_duration * (1 / 2) * 1000, refresh_rate)):
                flickering_keyboard_caps.draw()
                win.flip()
    else:
        pred_text = ''
        first_trial = True
        clear_text_double_check = False
        short_timeout = False
        mid_timeout = False
        long_timeout = False
        screen = 'keyboard'
        caps2 = False
        while True:
            if screen == 'keyboard':
                short_pred_text = pred_text
                if '\n' in short_pred_text:
                    short_pred_text = short_pred_text[short_pred_text.rfind('\n') + 1:]
                if len(short_pred_text) > 40:
                    short_pred_text = short_pred_text[-40:]
                top_text = visual.TextStim(win, short_pred_text, color=(-1, -1, -1), colorSpace='rgb', units='pix',
                                           pos=[0, height / 2 - 50], wrapWidth=1500, alignText='left')
                top_text.size = 50
                keys = kb.getKeys()
                for thisKey in keys:
                    if thisKey == 'escape':
                        if use_dsi_lsl:
                            for inlet in inlets:
                                inlet.close_stream()
                            os.kill(p.pid, sig.CTRL_C_EVENT)
                        core.quit()
                iter_frame = iter(enumerate(flickering_frames))
                key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                key_colors[:-1] = [1, 1, 1]
                flickering_keyboard.colors = key_colors
                # for frame in range(ms_to_frame(isi_duration/2*1000, refresh_rate)):
                #     flickering_keyboard_caps.draw()
                #     win.flip()
                for frame in range(ms_to_frame(isi_duration / 4 * 1000, refresh_rate)):
                    flickering_keyboard.draw()
                    top_text.draw()
                    win.flip()
                for i_frame, frame in iter_frame:
                    next_flip = win.getFutureFlipTime()
                    if random_movements:
                        movement_vector = (np.random.random(size=[n_keyboard_classes, 2]) * 2 - 1) * 1
                        flickering_keyboard.xys += movement_vector
                    if random_linear_movements:
                        flickering_keyboard.xys += linear_movement_vector
                    frame = np.append(frame, 1)
                    flickering_keyboard.colors = np.array([frame] * 3).T
                    flickering_keyboard.draw()
                    top_text.draw()
                    if core.getTime() > next_flip:
                        if use_dsi_trigger and (use_dsi_lsl or use_dsi7):
                            # msg = b'\x01\xe1\x01\x00\x02'
                            msg = b'\x02'  # if use trigger hub
                            dsi_serial.write(msg)
                        key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                        key_colors[:-1] = [1, -1, -1]
                        flickering_keyboard.colors = key_colors
                        for failure_frame in range(15):
                            flickering_keyboard.draw()
                            win.flip()
                        break
                    win.flip()
                    if i_frame == 0 and use_dsi_trigger and use_dsi_lsl:
                        # msg = b'\x01\xe1\x01\x00\x01'
                        msg = b'\x01'  # if use trigger hub
                        dsi_serial.write(msg)
                key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                key_colors[:-1] = [1, 1, 1]
                flickering_keyboard.colors = key_colors
                if use_dsi_lsl and make_predictions and not first_trial:
                    time_window = -int(stim_duration * 300) - 200
                    trial_eeg = np.copy(eeg[time_window:])
                    if (len(np.where(trial_eeg[:, -1] == 2.0)[0]) == 0):  # 2.0 or 18.0
                        dsi24chans = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 22, 23]
                        trial_start = np.where(trial_eeg[:, -1] == 16)[0][0] + 43
                        if trial_eeg[trial_start - 44, -1] != 0:
                            print(':beginning not found1')
                        trial_eeg = trial_eeg[trial_start:trial_start + int(stim_duration * 300), dsi24chans].T
                        beginning_found = False
                        while trial_eeg.shape[1] < int(stim_duration * 300):
                            trial_eeg = np.copy(eeg[time_window:])
                            trial_start = np.where(trial_eeg[:, -1] == 16)[0][0] + 43
                            if trial_eeg[trial_start - 44, -1] != 0:
                                beginning_found = False
                            else:
                                beginning_found = True
                            trial_eeg = trial_eeg[trial_start:trial_start + int(stim_duration * 300), dsi24chans].T
                        if not beginning_found:
                            print(':beginning not found2')
                        prediction = model.predict(trial_eeg)
                        predited_class_num = keyboard_classes.index(classes[prediction[0]])
                        key_colors[predited_class_num] = [-1, 1, -1]
                        if caps2 == False:
                            pred_letter = letters[predited_class_num]
                        else:
                            pred_letter = letters2[predited_class_num]
                        # letters = 'AIQYBJRZCKS⌂DLT⎵EMU,FNV.GOW⤒HPX⌫ '
                        # letters2 = '19/+2(~-3)$⌂4⌫%=5;&<6"*>7!#⤓8?⮐: '

                        if pred_letter not in ['⌂', '⎵', '⤒', '⌫', '⤓', '⮐']:
                            pred_text += pred_letter
                        elif pred_letter == '⌫':
                            pred_text = pred_text[:-1]
                        elif pred_letter == '⎵':
                            pred_text += ' '
                        elif pred_letter == '⮐':
                            pred_text += '\n'
                        elif pred_letter == '⤒':
                            caps2 = True
                        elif pred_letter == '⤓':
                            caps2 = False
                        elif pred_letter == '⌂':
                            screen = 'homescreen'

                if not (use_dsi_lsl and make_predictions) and dummy_mode and not first_trial:
                    predited_class_num = 0
                    for thisKey in keys:
                        if thisKey.name in dummy_keyboard_string:
                            predited_class_num = dummy_keyboard_string.index(thisKey.name)
                        elif thisKey.name == 'comma':
                            predited_class_num = dummy_keyboard_string.index(',')
                    key_colors[predited_class_num] = [-1, 1, -1]
                    if caps2 == False:
                        pred_letter = letters[predited_class_num]
                    else:
                        pred_letter = letters2[predited_class_num]
                    if pred_letter not in ['⌂', '⎵', '⤒', '⌫', '⤓', '⮐']:
                        pred_text += pred_letter
                    elif pred_letter == '⌫':
                        pred_text = pred_text[:-1]
                    elif pred_letter == '⎵':
                        pred_text += ' '
                    elif pred_letter == '⮐':
                        pred_text += '\n'
                    elif pred_letter == '⤒':
                        caps2 = True
                    elif pred_letter == '⤓':
                        caps2 = False
                    elif pred_letter == '⌂':
                        screen = 'homescreen'

                if first_trial:
                    first_trial = False
                if caps2:
                    flickering_keyboard_caps2.colors = key_colors
                else:
                    flickering_keyboard_caps.colors = key_colors
                for frame in range(ms_to_frame(isi_duration / 1.5 * 1000, refresh_rate)):
                    if caps2:
                        flickering_keyboard_caps2.draw()
                    else:
                        flickering_keyboard_caps.draw()
                    top_text.draw()
                    win.flip()
            elif screen == 'homescreen':
                input_text = visual.TextStim(win, 'Input: ' + pred_text, color=(-1, -1, -1), colorSpace='rgb', units='pix',
                                             wrapWidth=850, pos=[-300, -270], alignText='left')
                input_text.size = 35
                chat_history_text = parse_chat_history(get_content(dir='states/back_to_front.json',use_yaml=False))
                chat_history = visual.TextStim(win, chat_history_text, color=(-1, -1, -1), colorSpace='rgb', units='pix',
                                             wrapWidth=850, pos=[-300, 300], alignText='left',anchorVert='top')
                chat_history.size = 30
                keys = kb.getKeys()
                for thisKey in keys:
                    if thisKey == 'escape':
                        if use_dsi_lsl:
                            for inlet in inlets:
                                inlet.close_stream()
                            os.kill(p.pid, sig.CTRL_C_EVENT)
                            with open("eeg.csv", 'a') as csv_file:
                                np.savetxt(csv_file, eeg, delimiter=',')
                        if use_cyton:
                            for inlet in inlets:
                                inlet.close_stream()
                            stop_cyton.set()
                            board.stop_stream()
                            with open("eeg.csv", 'a') as csv_file:
                                np.savetxt(csv_file, eeg, delimiter=',')
                        core.quit()
                key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                # flickering_keyboard.colors = key_colors
                key_colors[:20] = [0, 0, 0]
                flickering_keyboard_caps3.colors = key_colors

                for frame in range(ms_to_frame(isi_duration * (1 / 2) * 1000, refresh_rate)):
                    flickering_keyboard_caps3.draw()
                    input_text.draw()
                    chat_history.draw()
                    win.flip()
                key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                key_colors[:-1] = [1, 1, 1]
                flickering_keyboard.colors = key_colors
                for frame in range(ms_to_frame(isi_duration / 4 * 1000, refresh_rate)):
                    flickering_keyboard.draw()
                    win.flip()
                flash_successful = False
                frame_start_time = -1
                while (not flash_successful):
                    for i_frame, frame in enumerate(flickering_frames):
                        frame = np.append(frame, 1)
                        next_flip = win.getFutureFlipTime()
                        flickering_keyboard.colors = np.array([frame] * 3).T
                        flickering_keyboard.draw()
                        if core.getTime() > next_flip:
                            if use_dsi_trigger and (use_dsi_lsl or use_dsi7):
                                # msg = b'\x01\xe1\x01\x00\x02'
                                msg = b'\x02'  # if use trigger hub
                                dsi_serial.write(msg)
                            key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                            key_colors[:-1] = [1, -1, -1]
                            # key_colors[class_num] = [1,-1,-1]
                            flickering_keyboard.colors = key_colors
                            for failure_frame in range(60):
                                flickering_keyboard.draw()
                                win.flip()
                            break
                        win.flip()

                        if i_frame == 0:
                            if use_dsi_trigger and (use_dsi_lsl or use_dsi7):
                                # msg = b'\x01\xe1\x01\x00\x01'
                                msg = b'\x01'  # if use trigger hub
                                dsi_serial.write(msg)
                            frame_start_time = local_clock()
                        if i_frame == stim_duration_frames - 1:
                            flash_successful = True
                            with open("meta.csv", 'a') as csv_file:
                                csv_file.write(str(flickering_freq) + ', ' + str(phase_offset) + ', ' + str(
                                    frame_start_time) + '\n')
                key_colors = np.array([[1, 1, 1]] * (n_keyboard_classes + 1))
                key_colors[:20] = [0, 0, 0]
                flickering_keyboard_caps3.colors = key_colors
                prediction = [-1]
                if use_dsi_lsl and make_predictions:
                    time_window = -int(stim_duration * 300) - 200
                    trial_eeg = np.copy(eeg[time_window:])
                    if (len(np.where(trial_eeg[:, -1] == 2.0)[0]) == 0):  # 2.0 or 18.0
                        dsi24chans = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 22, 23]
                        trial_start = np.where(trial_eeg[:, -1] == 16)[0][0] + 43
                        if trial_eeg[trial_start - 44, -1] != 0:
                            print(str(i_trial) + ':beginning not found1')
                        trial_eeg = trial_eeg[trial_start:trial_start + int(stim_duration * 300), dsi24chans].T
                        beginning_found = False
                        while trial_eeg.shape[1] < int(stim_duration * 300):
                            trial_eeg = np.copy(eeg[time_window:])
                            trial_start = np.where(trial_eeg[:, -1] == 16)[0][0] + 43
                            if trial_eeg[trial_start - 44, -1] != 0:
                                beginning_found = False
                            else:
                                beginning_found = True
                            trial_eeg = trial_eeg[trial_start:trial_start + int(stim_duration * 300), dsi24chans].T
                        if not beginning_found:
                            print(str(i_trial) + ':beginning not found2')
                        prediction = model.predict(trial_eeg)
                        predited_class_num = keyboard_classes.index(classes[prediction[0]])
                        # print(prediction[0])
                        key_colors[predited_class_num] = [-1, 1, -1]
                        pred_letter = letters3[predited_class_num]
                        # letters3 = '12341234123412341234⏳⌚⏰ ⎚⏩ ⌨✉⏪ ⌫ '
                        if pred_letter != '⎚':
                            clear_text_double_check = False
                        if pred_letter == '⌨':
                            screen = 'keyboard'
                            first_trial = True
                        elif pred_letter == '⌫':
                            pred_text = pred_text[:-1]
                        elif pred_letter == '⎚':
                            if clear_text_double_check:
                                pred_text = ''
                                clear_text_double_check = False
                            else:
                                clear_text_double_check = True
                        elif pred_letter == '⏳':
                            short_timeout = True
                        elif pred_letter == '⌚':
                            mid_timeout = True
                        elif pred_letter == '✉':
                            update_text(pred_text + '\u2709')
                            pred_text = ''
                        elif pred_letter == '⏰':
                            long_timeout = True
                        elif pred_letter == '⏩':
                            if isi_duration > 1:
                                isi_duration -= 0.2
                        elif pred_letter == '⏪':
                            if isi_duration < 2:
                                isi_duration += 0.2

                if not (use_dsi_lsl and make_predictions) and dummy_mode:
                    predited_class_num = 0
                    for thisKey in keys:
                        if thisKey.name in dummy_keyboard_string:
                            predited_class_num = dummy_keyboard_string.index(thisKey.name)
                        elif thisKey.name == 'comma':
                            predited_class_num = dummy_keyboard_string.index(',')
                    key_colors[predited_class_num] = [-1, 1, -1]
                    pred_letter = letters3[predited_class_num]
                    if pred_letter != '⎚':
                        clear_text_double_check = False
                    if pred_letter == '⌨':
                        screen = 'keyboard'
                        first_trial = True
                    elif pred_letter == '⌫':
                        pred_text = pred_text[:-1]
                    elif pred_letter == '⎚':
                        if clear_text_double_check:
                            pred_text = ''
                            clear_text_double_check = False
                        else:
                            clear_text_double_check = True
                    elif pred_letter == '✉':
                        update_text(pred_text + '\u2709')
                        pred_text = ''
                    elif pred_letter == '⏳':
                        short_timeout = True
                    elif pred_letter == '⌚':
                        mid_timeout = True
                    elif pred_letter == '⏰':
                        long_timeout = True
                    elif pred_letter == '⏩':
                        if isi_duration > 1:
                            isi_duration -= 0.2
                    elif pred_letter == '⏪':
                        if isi_duration < 2:
                            isi_duration += 0.2

                speed = int(11 - isi_duration / 0.2)
                speed_text = visual.TextStim(win, 'speed: ' + str(speed), color=(-1, -1, -1), colorSpace='rgb',
                                             units='pix', pos=[0, height / 2 - 50], wrapWidth=1500, alignText='left')
                speed_text.size = 50
                for frame in range(ms_to_frame(isi_duration / 1.5 * 1000, refresh_rate)):
                    speed_text.draw()
                    flickering_keyboard_caps3.draw()
                    input_text.draw()
                    chat_history.draw()
                    win.flip()

                if short_timeout or mid_timeout or long_timeout:
                    if short_timeout:
                        timeout_time = 15
                    elif mid_timeout:
                        timeout_time = 30
                    elif long_timeout:
                        timeout_time = 60
                    timer = core.CountdownTimer(timeout_time)
                    timeout_text = visual.TextStim(win, '', color=(-1, -1, -1), colorSpace='rgb', units='pix',
                                                   pos=[0, height / 2 - 50], wrapWidth=1500, alignText='left')
                    timeout_text.size = 50
                    time_left = timer.getTime()
                    while time_left > 0:
                        keys = kb.getKeys()
                        for thisKey in keys:
                            if thisKey == 'escape':
                                if use_dsi_lsl:
                                    for inlet in inlets:
                                        inlet.close_stream()
                                    os.kill(p.pid, sig.CTRL_C_EVENT)
                                    with open("eeg.csv", 'a') as csv_file:
                                        np.savetxt(csv_file, eeg, delimiter=',')
                                if use_cyton:
                                    for inlet in inlets:
                                        inlet.close_stream()
                                    stop_cyton.set()
                                    board.stop_stream()
                                    with open("eeg.csv", 'a') as csv_file:
                                        np.savetxt(csv_file, eeg, delimiter=',')
                                core.quit()
                        time_left = timer.getTime()
                        timeout_text.text = 'Timeout: ' + str(round(time_left, 3))
                        timeout_text.draw()
                        flickering_keyboard_caps3.draw()
                        input_text.draw()
                        chat_history.draw()
                        win.flip()
                    short_timeout = False
                    mid_timeout = False
                    long_timeout = False

    if use_dsi_lsl:
        for inlet in inlets:
            inlet.close_stream()
        os.kill(p.pid, sig.CTRL_C_EVENT)
        with open("eeg.csv", 'a') as csv_file:
            np.savetxt(csv_file, eeg, delimiter=',')
    if use_cyton:
        with open("eeg.csv", 'a') as csv_file:
            np.savetxt(csv_file, eeg, delimiter=',')
    core.quit()
