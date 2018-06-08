# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 13:52:50 2018

@author: 12600632
"""

""" Plot signals in frequency domain
"""
from calc_fft import calc_fft
import matplotlib.ticker as tick 

def plot_fft(x, y, step, nfft, ovlp, xlim, tab, ylabel, unit):
    
    """ calculate fft """
    f, PD   = calc_fft(x, y, step, nfft, ovlp, xlim)
    """ plot fft """
    ax = tab.canvas.ax
    f_handle, = ax.semilogy(f, PD, 
                            label = ylabel)
    """ save handles """
    tab.lns.append(f_handle)
    """ grid on """
    ax.grid(alpha = 0.5, linestyle = '--')
    """ y-axis tick format """
    ymajor_formatter = tick.FormatStrFormatter('%2.2e')
    ax.yaxis.set_major_formatter(ymajor_formatter)
    """ axis label """
    ax.set_ylabel('Spectral Energy Density')
    ax.set_xlabel('Frequency, Hz')