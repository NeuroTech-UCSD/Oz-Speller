"""
Oz Speller GUI script without the headset integration

This script does not connect to any EEG headset but is instead controlled by
the keyboard in order to test the function of the GUI. To control it with
the keyboard, the '1', '8', 'z', ',' would be mapped onto the top-left, 
top right, bottom left, bottom right squares on the GUI.

Notes:
- Press esc to quit
- MAKE SURE refresh_rate IS SET TO YOUR MONITOR'S REFRESH RATE
"""

from psychopy import visual, core
from psychopy.hardware import keyboard
import numpy as np
from scipy import signal
import yaml
import json
import random
import sys, time
from pylsl import local_clock

sys.path.append('src')  # if run from the root project directory

# █████████████████████████████████████████████████████████████████████████████


## VARIABLES
use_arduino = False  # arduino photosensor for flashing timing test
use_photosensor = False
record_start_time = True
center_flash = False  # whether the visual stimuli are only presented at the center of the screen
test_mode = False  # whether the script indicates target squares and saves recorded data
dummy_mode = True

width = 1536
height = 864
flash_mode = 'square'  # 'sine', 'square', or 'chirp', 'dual band'
refresh_rate = 60.02  # refresh rate of the monitor
use_retina = False  # whether the monitor is a retina display
stim_duration = 1.2  # in seconds
isi_duration = 1  # in seconds, used both pre and post stimulations
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

n_keyboard_classes = len(keyboard_classes)

classes = keyboard_classes


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

def ms_to_frame(ms, fs):
    dt = 1000 / fs
    return np.round(ms / dt).astype(int)

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

## Arduino Photosensor for Timing
if use_arduino:
    from sys import executable
    import os
    from subprocess import Popen

    # Popen([executable,  os.path.join(os.getcwd(), 'run_arduino_photosensor.py')])
    Popen([executable, os.path.join(os.getcwd(), 'scripts', 'run_arduino_photosensor.py')])
    time.sleep(2)

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

    flickering_keyboard = create_32_keys()
    flickering_keyboard_caps = create_key_caps(text_strip, el_mask, phases)
    flickering_keyboard_caps2 = create_key_caps(text_strip2, el_mask2, phases)
    flickering_keyboard_caps3 = create_key_caps(text_strip3, el_mask3, phases)
    stim_duration_frames = ms_to_frame((stim_duration) * 1000,
                                       refresh_rate)  # total number of frames for the stimulation
    frame_indices = np.arange(stim_duration_frames)  # the frames as integer indices
    flickering_frames = np.zeros((len(frame_indices), n_keyboard_classes))

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
        for i_trial, (flickering_freq, phase_offset) in enumerate(sequence):  # for each trial in the trail sequence
            class_num = keyboard_classes.index((flickering_freq, phase_offset))
            trial_text = visual.TextStim(win, 'trial:' + str(i_trial + 1) + '/' + str(len(sequence)),
                                         color=(-1, -1, -1), colorSpace='rgb', units='pix', pos=[-200, height / 2 - 50])
            trial_text.size = 50
            acc_text = visual.TextStim(win, 'accuracy:%3.2f' % (n_correct / (i_trial + 1) * 100) + '% (' + str(
                n_correct) + '/' + str(i_trial + 1) + ')', color=(-1, -1, -1), colorSpace='rgb', units='pix',
                                       pos=[200, height / 2 - 50])
            acc_text.size = 50
            phase_offset_str = str(phase_offset)
            keys = kb.getKeys()
            for thisKey in keys:
                if thisKey == 'escape':
                    core.quit()
            key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
            key_colors[class_num] = [1, 1, 1]
            flickering_keyboard.colors = key_colors
            flickering_keyboard_caps.colors = key_colors

            for frame in range(ms_to_frame(isi_duration * (1 / 2) * 1000, refresh_rate)):
                trial_text.draw()
                acc_text.draw()
                flickering_keyboard_caps.draw()
                win.flip()
            for frame in range(ms_to_frame(isi_duration * (1 / 2) * 1000, refresh_rate)):
                trial_text.draw()
                acc_text.draw()
                flickering_keyboard.draw()
                win.flip()
            flash_successful = False
            frame_start_time = -1
            while (not flash_successful):
                for i_frame, frame in enumerate(flickering_frames):
                    frame = np.append(frame, 1)
                    next_flip = win.getFutureFlipTime()
                    trial_text.draw()
                    acc_text.draw()
                    flickering_keyboard.colors = np.array([frame] * 3).T
                    flickering_keyboard.draw()
                    if core.getTime() > next_flip:
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
                        frame_start_time = local_clock()
                    if i_frame == stim_duration_frames - 1:
                        flash_successful = True
                        with open("meta.csv", 'a') as csv_file:
                            csv_file.write(
                                str(flickering_freq) + ', ' + str(phase_offset) + ', ' + str(frame_start_time) + '\n')
            key_colors = np.array([[1, 1, 1]] * (n_keyboard_classes + 1))
            flickering_keyboard_caps.colors = key_colors
            prediction = [-1]
            for frame in range(ms_to_frame(isi_duration * (1 / 2) * 1000, refresh_rate)):
                trial_text.draw()
                acc_text.draw()
                # flickering_keyboard.draw()
                flickering_keyboard_caps.draw()
                win.flip()
        eeg_np = np.array(eeg_temp).transpose(1, 0, 2, 3)
        print(eeg_np.shape)
        with open('eeg.npy', 'wb') as f:
            np.save(f, eeg_np)
        time.sleep(5)
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
                        core.quit()
                iter_frame = iter(enumerate(flickering_frames))
                key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                key_colors[:-1] = [1, 1, 1]
                flickering_keyboard.colors = key_colors
                for frame in range(ms_to_frame(isi_duration / 4 * 1000, refresh_rate)):
                    flickering_keyboard.draw()
                    top_text.draw()
                    win.flip()
                for i_frame, frame in iter_frame:
                    next_flip = win.getFutureFlipTime()
                    frame = np.append(frame, 1)
                    flickering_keyboard.colors = np.array([frame] * 3).T
                    flickering_keyboard.draw()
                    top_text.draw()
                    if core.getTime() > next_flip:
                        key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                        key_colors[:-1] = [1, -1, -1]
                        flickering_keyboard.colors = key_colors
                        for failure_frame in range(15):
                            flickering_keyboard.draw()
                            win.flip()
                        break
                    win.flip()
                key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
                key_colors[:-1] = [1, 1, 1]
                flickering_keyboard.colors = key_colors

                if dummy_mode and not first_trial:
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
                        core.quit()
                key_colors = np.array([[-1, -1, -1]] * (n_keyboard_classes + 1))
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

                if dummy_mode:
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

    core.quit()
