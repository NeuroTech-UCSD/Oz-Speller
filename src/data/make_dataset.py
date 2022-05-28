import logging
import click
import numpy as np
import pandas as pd
import yaml
import os
import pickle
import mne

project_dir = './'
 

def load_data_temp_function(eeg, meta, classes, *, timepoints_isi, timepoints_per_trial):
    """
    Return
    """
    trials = meta[1:,:2]
    times = meta[:,2]
    times = (times - times[0])[1:]
    eeg['time'] = eeg['time'] - eeg['time'].iloc[0]
    eeg = np.array([eeg.loc[eeg['time']>t].drop(columns=['time',' TRG']).to_numpy()[:timepoints_per_trial].T for t in times])[:,:,timepoints_isi:]
    eeg = mne.filter.filter_data(eeg, sfreq=300, l_freq=5, h_freq=49, verbose=0, method='fir')
    eeg_temp = []
    for i in range(len(classes)):
        eeg_temp.append([])
    for i,freq in enumerate(trials):
        for j,target in enumerate(classes):
            if (freq==target).all():
                eeg_temp[j].append(eeg[i])
    eeg = np.array(eeg_temp).transpose(1,0,2,3)
    return eeg


def prepare_data(data_path):
    data_path = os.path.join(project_dir, data_path)
    with open(data_path, 'rb') as handle:
        data = pickle.load(handle)
    trial_all = data['trial_all']
    eeg_all = data['eeg_all']
    num_trial_per_target, num_targets, num_channels, timepoints_stimulus_duration = eeg_all.shape
        
    # Create dataset
    target_idx_tab = {}
    target_idx_tab = {(freq, phase): i for i, (freq, phase) in enumerate(trial_all)}
    assert len(target_idx_tab.keys()) == num_targets
    target_idx_tab
    trials = np.arange(0, num_trial_per_target)  # only using the subset of trials 
    X = eeg_all[trials]
    y = np.empty([len(trial_all), 1])
    for i, (freq, phase) in enumerate(trial_all):
        y[i] = target_idx_tab[(freq, phase)]
    y = np.repeat(y, len(trials), axis=1).T  # shape: (trials, targets)
    return X, y

@click.command()
def main():
    """
    Parse the continuous recording data into trialized data for modeling

    Args:
        raw_data_dir: should contain meta.csv, eeg.csv, and info.yaml in this directory
    """
    print(os.getcwd())
    
    logger = logging.getLogger(__file__)
    logging.basicConfig(level=logging.INFO)
    output_path = os.path.join(project_dir, 'data/interim/simon_36.pkl')
    
    # Constants
    sub_dirs = ['8hz_20trials/','9hz_20trials/','10hz_20trials/',
            '11hz_10trials_run1/','11hz_10trials_run2/',
            '12hz_10trials_run1/','12hz_10trials_run2/',
            '12.6hz_10trials_run1/','12.6hz_10trials_run2/',
            '13hz_10trials_run1/','13hz_10trials_run2/',
            '14hz_10trials_run1/','14hz_10trials_run2/',
            '15hz_10trials_run1/','15hz_10trials_run2/']

    num_targets = 36
    sampling_frequency = 300
    isi_duration = 0.750  # s
    stimulus_duration = 5.000 # s
    num_trial_per_target = 20
    channels = ['Pz', 'F4', 'C4', 'P4', 'P3', 'C3', 'F3']
    num_channels = len(channels)
    timepoints_stimulus_duration = int(stimulus_duration * sampling_frequency)  # 1500
    timepoints_isi = int(sampling_frequency * isi_duration)
    timepoints_per_trial = int((isi_duration + stimulus_duration) * sampling_frequency)
    
    
    # Process Data
    eeg_all = np.zeros((num_trial_per_target, num_targets, num_channels, timepoints_stimulus_duration))
    trial_all = []  # (num_targets, 1 + 1), freq and phase
    recording_count = 0
    for i_dir,sub_dir in enumerate(sub_dirs):
        if sub_dir[-2] == '2':
            continue
        data_path = os.path.join(project_dir, "data/eeg_recordings/pilot_data/simon/s32/" + sub_dir)
        eeg = pd.read_csv(data_path + 'eeg.csv').astype(float)
        meta = np.loadtxt(data_path + 'meta.csv', delimiter=',', dtype=float)
        trials = meta[1:,:2]
        classes = np.unique(trials, axis=0)  # (4, 2), 4 targets, each target has a freq and a phase
        eeg = load_data_temp_function(eeg, meta, classes, timepoints_isi=timepoints_isi, timepoints_per_trial=timepoints_per_trial)
        if sub_dir not in ['8hz_20trials/','9hz_20trials/','10hz_20trials/']:
            if sub_dir[-2] == '1' and i_dir+1 < len(sub_dirs):
                sub_dir2 = sub_dirs[i_dir+1]
                data_path2 = os.path.join(project_dir, "data/eeg_recordings/pilot_data/simon/s32/" + sub_dir2)
                eeg2 = pd.read_csv(data_path2 + 'eeg.csv').astype(float)
                meta2 = np.loadtxt(data_path2 + 'meta.csv', delimiter=',', dtype=float)
                trials2 = meta2[1:,:2]
                eeg2 = load_data_temp_function(eeg2,meta2,classes, timepoints_isi=timepoints_isi, timepoints_per_trial=timepoints_per_trial)
                eeg = np.vstack((eeg,eeg2))
        trial_all.append(classes.tolist())
        eeg_all[:, recording_count:recording_count + 4] = eeg
        recording_count += 4
    trial_all = np.array(trial_all).reshape([-1, 2]) 
    
    output = {'eeg_all': eeg_all, 'trial_all': trial_all}
    with open(output_path, 'wb') as handle:
        pickle.dump(output, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    
if __name__ == '__main__':
    main()
