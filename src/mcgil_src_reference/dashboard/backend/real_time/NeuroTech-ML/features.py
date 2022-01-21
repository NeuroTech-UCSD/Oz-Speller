#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 09:32:01 2020

@author: marley
"""

import numpy as np
import matplotlib.mlab as mlab

###Temporal features

#Integrated emg
def iemg(signal):
    return np.sum(np.abs(signal))

#Mean absolute value
def mav(signal):
    return np.mean(np.abs(signal)) 

#Modified mean absolute value
def mmav(signal):
    def weight(n, N):
        if n < 0.25*N: return 4*n/N
        elif 0.25*N <= n and n <= 0.75*N: return 1
        else: return 4*(n - N)/N
    
    N = len(signal)
    w = [weight(n, N) for n in range(N)]
    return np.average(signal, weights=w)

#Variance
def var(signal):
    return np.var(signal) 

#Variance of amplitudes of signal
def var_abs(signal):
    return np.var(np.abs(signal))

#Root mean square
def rms(signal):
    return np.sqrt(np.mean(np.square(signal)))

#Root mean squared subwindows
def rms_3(signal):
    N = len(signal)
    one_third, two_thirds = int(N / 3), int(2 * N / 3)
    return [rms(signal[:one_third]), rms(signal[one_third: two_thirds]), rms(signal[two_thirds:])]

#In what follows, thresholds: 10-100mV
    
### Helper functions for computing features below

def consec_prod(signal):
    #calculates x[i+1] * x[i] for i = 1, ..., len(signal) - 1
    return signal[1:] * signal[:-1]

def consec_abs_diff(signal):
    #calculates |x[i+1] - x[i]| for i = 1, ..., len(signal) - 1
    return np.abs(signal[1:] - signal[:-1])

def consec_abs_sum(signal):
    #calculates |x[i+1] + x[i]| for i = 1, ..., len(signal) - 1
    return np.abs(signal[1:] + signal[:-1])

###

#Waveform length
def wl(signal):
    return np.sum(consec_abs_diff(signal))

#Zero crossing
def zc(signal, threshold=20):
    T = [threshold for i in range(len(signal) - 1)]
    #|x[i+1] - x[i]| > |x[i+1] + x[i]| - calculates if signal crosses zero at i
    #|x[i+1] - x[i]| > threshold - removes noise
    return np.sum(np.where(consec_abs_diff(signal) > np.maximum(consec_abs_sum(signal), T)))

#Slope sign change
def ssc(signal, threshold=20):
    T = [threshold for i in range(len(signal) - 2)] #Threshold
    where_concave = np.where(signal[1:-1] > np.maximum(signal[:-2], signal[2:]), 1, 0) #Where slope changes from pos to neg
    where_convex = np.where(signal[1: -1] < np.minimum(signal[:-2], signal[2:]), 1, 0) #Where slope changes from neg to pos
    noise_condition = np.where(np.maximum(consec_abs_diff(signal[:-1]), consec_abs_diff(signal[1:])) >  T, 1, 0) #Where max(|x[i+1] - x[i]|, |x[i] - x[i-1]|) > threshold for i = 2, ..., len(signal) - 2
    
    return np.sum((where_concave + where_convex) * noise_condition)

#Willison amplitude
def wamp(signal, threshold=20):
    return np.sum(np.where(consec_abs_diff(signal) > threshold, 1, 0))

#Spectrogram

### Helper functions for computing features below

#Returns just the trimmed power spectrum - we don't care really about very low frequencies (below 5hz)
def get_psd(signal):
    psd,freqs = mlab.psd(signal,NFFT=256,window=mlab.window_hanning,Fs=250,noverlap=0)
    return psd

#Returns list of bands that you can use
def get_bands(psd):
    # return [psd[5:20] , psd[20:40] , ,psd[40:60], psd[60:80] , psd[80:100], psd[100:120]]
    # return [psd[5:11] , psd[11:15] , psd[21:29] , psd[29:36] , psd[36:43] , psd[43:50]]# , psd[80:100] , psd[100:120]]
    return [psd[5:10],psd[10:15],psd[15:20],psd[20:25],psd[25:30],psd[30:35],psd[35:40],psd[40:45],psd[45:50]]

# some basic freq domain features 
def freq_feats(signal):
    psd = get_psd(signal)
    return [np.mean(i) for i in get_bands(psd)] 

# jonathan suggested this would be better
def freq_feats_relative(signal):
    psd = get_psd(signal)
    total = np.sum(psd)
    return [np.mean(i)/total for i in get_bands(psd)]

# more basic features : the min and the max from each frequency band
def freq_feats_min_max(signal):
    psd = get_psd(signal)
    return [np.max(i) for i in get_bands(psd)]+[np.min(i) for i in get_bands(psd)]


# some more freq domain features
def freq_var(signal):
    psd = get_psd(signal)
    return [np.mean(np.square(i - np.array([np.mean(i)]*len(i)))) for i in get_bands(psd)]

# more freq domain features
def freq_misc(signal):
    psd = get_psd(signal)
    return [ssc(psd),mav(psd),mmav(psd),zc(psd-[.5]*len(psd))]
    
    
## Unhelpful feature: power spectral density
""" # FIX DIMENSIONS LATER
def psd(signal):
    shift = 0.1
    fs_Hz = 250
    NFFT = 256
    overlap = NFFT - int(shift * fs_Hz)
    
    # Pxx - 1D array for power spectrum values
    # freq - 1D array corresponding to Pxx values
    Pxx, freq = mlab.psd(np.squeeze(signal),
                                   NFFT=NFFT,
                                   window=mlab.window_hanning,
                                   Fs=fs_Hz,
                                   noverlap=overlap
                                   )
    # Make it size 130 so we can splice it
    Pxx.append(Pxx[-1])
    # Bin it by taking average power of every 10 hz
    Pxx_bins = np.reshape(Pxx,(10,-1)).mean();
    
    return Pxx_bins
"""