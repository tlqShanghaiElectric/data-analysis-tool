# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 11:07:57 2018

@author: 12600632
"""


import numpy as np
import matplotlib.ticker as tick 
from prettyNum import prettyNum
from classify_yaxis import classify_yaxis
from plot_fft import plot_fft

class CrePlotVar:
    
    def __init__(self):
        self.id_var     = 0     # index of the sensor in the varlist
        self.dir        = 0     # directory
        self.var        = 0     # sensor name
        self.data_x     = 0     # x data of the sensor
        self.data_y     = 0     # y data of the sensor
        self.step       = 0     # time step of the sensor data
        self.unit       = 0     # unit of the sensor data 
        self.ylabel     = 0     # y label of the sensor data
        self.stat       = 0     # statistics of the sensor data
        #self.DEL        = 0     # DEL of the sensor data
        self.in_file    = 0     # .% file
        self.plotflag   = 0     # 1 for plotted, and 0 for not
        self.mytab      = 0     # the tab this variable object belongs to
        self.max_       = 0     # statistics of this variable, maximum
        self.min_       = 0
        self.mean_      = 0
        self.std_       = 0
        self.t_max_     = 0     # time corresponding to the maximum
        self.t_min_     = 0
        
    def _plot_t(self):
        colors     = ['b', 'r', 'g', 'm', 'y', 'k']; ncolor = len(colors)
        linestyles = ['-', '--', '-.', ':'];         nstyle = len(linestyles)
        
        """ decide the y axis position """
        ax = classify_yaxis(self)
        """ plot t """
        n = len(self.mytab.lns)
        f_handle, = ax.plot(self.data_x, self.data_y, 
                            color     = colors[n % ncolor],
                            linestyle = linestyles[max(0, n-ncolor)% nstyle],
                            label     = self.ylabel)
        """ save handles """
        self.mytab.lns.append(f_handle)
        ax.set_xlabel('Time, s')
        """ y axis label and color """
        ax.set_ylabel(self.ylabel, color = f_handle.get_color()[0])
        """ grid on """
        ax.grid(alpha = 0.4, linestyle = '--')
        """ y-axis tick format """
        if abs(np.max(self.data_y)) > 10000:
            ymajor_formatter = tick.FormatStrFormatter('%2.2e')
        else:
            ymajor_formatter = tick.FormatStrFormatter('%4.2f')
        """ pretty ticks """    
        ax.yaxis.set_major_formatter(ymajor_formatter)
        lowbound = ax.get_ybound()[0]
        highbound = ax.get_ybound()[1]
        lowbound, highbound = prettyNum(lowbound, highbound)
        ax.set_yticks(np.linspace(lowbound, highbound, 11))
        
        def onLimitsChange(axes):
            a = axes.get_ylim()
            lowbound, highbound = a[0], a[1]
            axes.set_yticks(np.linspace(lowbound, highbound, 11))
        
        ax.callbacks.connect('ylim_changed', onLimitsChange)        
        
        
        
    def _plot_fft(self, xlim):
        
        
        mainpage = self.mytab.myMaster
        """ point number of fft """
        nfft    = mainpage.NFFTEntry.get()
        """ overlap """
        ovlp    = mainpage.overlapEntry.get()
        
        """ plot fft """
        plot_fft(self.data_x, self.data_y, self.step, nfft, ovlp, xlim, 
                 self.mytab, self.ylabel, self.unit)
        


            
    