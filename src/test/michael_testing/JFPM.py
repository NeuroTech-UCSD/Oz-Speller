import matplotlib.pyplot as plt
import numpy as np

monitor_fps = 60
ms_per_frame = 1000 / monitor_fps
delta_phase = 0.5 * np.pi
base_frequency = 12
upper_frequency = 18
num_targets = 26  # A - Z
# TODO round up delta_frequency to the nearest tenth, i.e. 0.3231 -> 0.3
delta_frequency = (upper_frequency - base_frequency) / num_targets

# TODO finish filling in the sitimulus table
characters = ['A', 'B']  # A - Z
stimulus_table = {}  # {'A': [8.0, 0.0], 'B': [8.2, 0.35]}


def get_stimulus_sequence(f, phi, i):
    '''

    :param f: frequency of a target
    :param phi: phase of a target
    :param i: frame index (0 - 59 if fps = 60)
    :return: luminance level (0 - 1)
    '''
    return 1 / 2 * (1 + np.sin(2 * np.pi * f * (i / monitor_fps) + phi))


# TODO Generate plot fig4.A
freq_picks = [12.2, 12.4, 12.6]  # can have any size from 1 to num_targets, should
# only use frequency & phase from the stimulus table
fig, axes = plt.subplots(nrows=4, ncols=1)  # phase = 0, pi/2, pi, 3pi/2
axes[0].plot(x, y11)
axes[0].plot(x, y21)
axes[0].plot(x, y31)
axes[0].legend()

axes[1].plot(x, y21)
...
plt.show()