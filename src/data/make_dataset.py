import logging
import click
import numpy as np
import pandas as pd
import yaml
import os
import pickle
import mne

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_data(raw_data_dir, output_dir, l_freq=5, h_freq=49, method='fir'):
    """
    Parse the continuous recording data into trialized data for modeling. Save the
    trialized data as numpy format pickle file in the specified output_dir
    with filename output_dir/${}

    Args:
        raw_data_dir: should contain meta.csv, eeg.csv, and info.yaml in this directory
        l_freq: low_pass filter freq
        h_freq: high_pass filter freq
        method: bandpassing method
    """

    # Load data
    data_path = raw_data_dir
    filename = 'eeg.csv'
    metaname = 'meta.csv'
    infoname = 'info.yaml'
    with open(os.path.join(data_path, infoname)) as file:
        json_dict = yaml.load(file, Loader=yaml.FullLoader)
        sampling_frequency = json_dict['sampling_frequency']
        isi_duration = json_dict['isi_duration']  # s
        stimulus_duration = json_dict['stimulus_duration']  # s
        channels = json_dict['channels']
    eeg = pd.read_csv(data_path + filename).astype(float)
    meta = np.loadtxt(data_path + metaname, delimiter=',', dtype=float)
    trials = meta[1:,
             0]  # we want to align all our data to the first timepoint, so we ignore the first timepoint, the 1st column is the corresponding freq of our targets
    times = meta[:, 2]  # 2nd column is the phase offset, 3rd column is the time with timepoint as units
    times = (times - times[0])[1:]  # again we ignore the first timepoint
    num_targets = len(np.unique(trials))
    freq_tab = {freq: index for index, freq in enumerate(np.unique(trials))}

    # Extract important constants
    timepoints_stimulus_duration = int(stimulus_duration * sampling_frequency)
    timepoints_isi = int(sampling_frequency * isi_duration)
    timepoints_per_trial = int((isi_duration + stimulus_duration) * sampling_frequency)
    logger.info(f"Num targets: {num_targets}")
    logger.info(f"Targets: {list(freq_tab.keys())}")

    # accounting for visual_delay
    max_allowed_visual_delay_timepoints = len(eeg.loc[eeg['time'] > times[-1]]) - timepoints_per_trial
    visual_delay = 0.14  # units: s, according to https://www.pnas.org/doi/10.1073/pnas.1508080112
    timepoints_visual_delay = int(visual_delay * sampling_frequency)
    assert timepoints_visual_delay <= max_allowed_visual_delay_timepoints, f"Maximum visual delay allowed is {max_allowed_visual_delay_timepoints / sampling_frequency} s" \
    f", either allow for longer recording at the end of the recording session or discard the last trial"

    # trializing the data
    eeg = np.array([eeg.loc[eeg['time']>t].drop(columns=['time',' TRG']).to_numpy()[timepoints_visual_delay:(timepoints_per_trial + timepoints_visual_delay)].T for t in times])
    # not interested in isi session, which is at the beginning of each trial
    eeg = eeg[:,:,timepoints_isi:]

    # filtering the data
    eeg = mne.filter.filter_data(eeg, sfreq=sampling_frequency, l_freq=l_freq, h_freq=h_freq, verbose=0, method=method)

    # put targets into different buckets
    eeg_by_freq = []
    for i in range(num_targets):
        eeg_by_freq.append([])
    for i, freq in enumerate(trials):
        eeg_by_freq[freq_tab[freq]].append(eeg[i])
    eeg_by_freq = np.array(eeg_by_freq).transpose(1, 0, 2, 3)  # resulting  shape: (trials, num_targets, channels, timepoints)

    with open(os.path.join(output_dir, "eeg.pickle"), 'wb') as handle:
        pickle.dump(eeg_by_freq, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(os.path.join(output_dir, "eeg.pickle"), 'wb') as handle:
        pickle.dump(eeg_by_freq, handle, protocol=pickle.HIGHEST_PROTOCOL)



@click.command()
@click.argument('raw_data_dir')
@click.argument('output_path')
def main(raw_data_dir, output_path):
    """
    Parse the continuous recording data into trialized data for modeling

    Args:
        raw_data_dir: should contain meta.csv, eeg.csv, and info.yaml in this directory
    """
    parse_data(raw_data_dir, output_path)


if __name__ == '__main__':
    main()
