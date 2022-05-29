import numpy as np
from numpy.fft import rfft, irfft, rfftfreq
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()
import pandas as pd
import mne 
from matplotlib.pyplot import cm
from scipy.fftpack import fft

import tensorflow as tf
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import json
import os
import yaml
import keras_tuner as kt
import click
import pickle

project_dir = './'

 
@click.command()
@click.argument('data_path')
@click.argument('output_path')
def main(data_path, output_path):
    """
    Parse the continuous recording data into trialized data for modeling

    Args:
        
    """
    def smooth(y, box_pts):
        box = np.ones(box_pts)/box_pts
        y_smooth = np.convolve(y, box, mode='same')
        return y_smooth

    data_path = os.path.join(project_dir, data_path)
    with open(data_path, 'rb') as handle:
        data = pickle.load(handle)
    trial_all = data['trial_all']
    eeg_all = data['eeg_all']
    num_trial_per_target, num_targets, num_channels, timepoints_stimulus_duration = eeg_all.shape
    
    # Please change this line to the correct isi_duration, sampling frequency!!
    isi_duration = 0.75
    sampling_frequency = 300
    
    # Start filtering data
    freqs = np.linspace(0.0, sampling_frequency / 2, int(isi_duration * 1000))
    psd = 2/int(isi_duration * 1000)*np.abs(fft(eeg_all)[:,:,:,:int(isi_duration * 1000)])
    avg_spectral_variance = psd[:,:,0,:].var(axis=0).mean(axis=0)
    avg_spectral_variance_half = psd[:10,:,0,:].var(axis=0).mean(axis=0)
    smooth_avg_spectral_variance = smooth(avg_spectral_variance,9)**(1/3)+0.25
    
    psd_peaks = {8:[8,16,24,32],9:[9,15,18,24],10:[10,10,40,20],11:[11,22,27,6],12:[12,12,24,24],
            12.6:[12.6,9.6,25.2,22.2],13:[13,13,8,26],14:[14,28,8,32],15:[15,15,30,45]}
    peak_freqs = np.unique(np.array(list(psd_peaks.values())))
    freqs = np.linspace(0.0, sampling_frequency / 2, int(isi_duration * 1000))
    peak_freq_inds = [np.abs(freqs - peak_freq).argmin() for peak_freq in peak_freqs]
    smooth_avg_spectral_variance_notched = smooth_avg_spectral_variance.copy()
    smooth_avg_spectral_variance_notched[peak_freq_inds] -=0.5
    
    complex_spectrum = 1/750*fft(eeg_all)[:,:,:,:(timepoints_stimulus_duration)//2]
    complex_spectrum_filtered = complex_spectrum/smooth_avg_spectral_variance_notched
    eeg_filtered = irfft(complex_spectrum_filtered,n=timepoints_stimulus_duration)
   
    output = {'eeg_all': eeg_filtered, 'trial_all': trial_all}
    with open(output_path, 'wb') as handle:
        pickle.dump(output, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    
if __name__ == '__main__':
    main()
