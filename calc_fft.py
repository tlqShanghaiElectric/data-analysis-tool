# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 19:44:15 2018

@author: 12600632
"""

"""
This function is to calculate FFT.

Since wierd error occurs when cx_freeze is used to produce .exe with scipy, I 
write this function to avoid using scipy.

Last edit: Cai Jiasi, 2018/6/6
"""
import tkinter as tk
import numpy as np

def calc_fft(x, y, step, NFFT, ovlp, xlim):
    
    if xlim != (0.0, 1.0):
        id_tmin = (abs(x - xlim[0])).argmin()  
        id_tmax = (abs(x - xlim[1])).argmin()  
        y = y[id_tmin:id_tmax]
        x = x[id_tmin:id_tmax]

        
    #   default 1024
    if NFFT == '' or int(NFFT) == 0:
        NFFT = len(y)
   
    if int(NFFT) > len(y):
        tk.messagebox.showerror('Error','NFFT is larger than data length!')
        
    else:
        NFFT = int(NFFT)
        win_len = NFFT
        win_overlap = float(ovlp)
        win_hann = np.hanning(win_len);
        y -= np.mean(y)         #   remove DC term
        trd = (y[-1]-y[0])/(x[-1]-x[0])*x + y[0]
        y -= trd                #   detrend
        Pxx_den = np.zeros(int(NFFT/2))
        
        i_win = 0
        i     = 0
        while i_win < (len(y) - win_len):
            y_seg = y[i_win:i_win + win_len]
            y_win = win_hann*y_seg
            Pxx_den += np.power(abs(np.fft.fft(y_win)),2)[1:int(NFFT/2)+1]
            i_win += int(win_len*win_overlap)
            i += 1
        Pxx_den /= i
        
        fs = 1/step
        f  = fs*np.arange(0,(NFFT/2))/NFFT;        
        
        #   scale power density
        Sw2 = sum(win_hann**2)
        Pxx_den = 2*Pxx_den/fs/Sw2
        
        #   compensation 
        Pxx_den *= 1.6

        return f, Pxx_den