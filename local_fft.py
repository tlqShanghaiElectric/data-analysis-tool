# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 21:58:43 2018

@author: Jiasi
"""

''' This is a customised function for plotting spectrum '''


from CrePlotVar import CrePlotVar
from load_percent import load_percent
from load_dollar import load_dollar
from selection import selection_dir_var
from plot_fft import plot_fft

def local_fft(master):
    
    tab_orig = master.tab_current
    xlim = tab_orig.canvas.ax.get_xlim()  
    master.callback_new_tab()
    """ plot local fft in a new tab """
    tab_now = master.tab_current

    for i_varobj in tab_orig.plot_varobjs:
 
        """ --- plot frequency domain --- """
        """ calculation range, i.e. window size """
        x = i_varobj.data_x
        y = i_varobj.data_y
        step = i_varobj.step
        nfft = master.NFFTEntry.get()
        ovlp = master.overlapEntry.get()
        ylabel = i_varobj.ylabel
        unit = i_varobj.unit
        plot_fft(x, y, step, nfft, ovlp, xlim, 
                 tab_now, ylabel, unit) 
    
    tab_now.canvas.ax.legend(handles = tab_now.lns, 
                           loc = 'lower left',
                           bbox_to_anchor= (0, 1.00),
                           ncol = 3) 

    tab_now.toolbar.toolbar.update()  
    tab_now.canvas.plotCanvas.draw()

    
#def find_nearest_time_index(xlim, data_x):
#    '''
#    return nearest value's index
#    '''
#
#    id_tmin = (abs(data_x - xlim[0])).argmin()  
#    id_tmax = (abs(data_x - xlim[1])).argmin()  
#
#    
#    return id_tmin, id_tmax
