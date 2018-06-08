# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 18:18:00 2018

@author: 12600632
"""

"""
 Classify y axis 

 To be honest, I do not know how to make the following code conciser.
 All is to make logic decisions whether to create a primary or secondary 
 y axis/axes without overlapping, i.e. to ARRANGE Y AXIS(AXES)
 The logic is based on two facts: 
 1. has this sensor been plotted ever?
 2. is the first sensor of the current tab?

"""
        
def classify_yaxis(varobj):
    
    tab = varobj.mytab
    history = tab.plotted_vars
    
    
    if varobj.var in list(history.keys()):  # this var has been plotted
        ax = history[varobj.var]
    else:                                   # never been plotted
        if list(history.keys()) == []:
            ax = tab.canvas.ax
            history[varobj.var] = ax
        else:
            ax = tab.canvas.ax.twinx()
            ax.spines['right'].set_position(('outward', 75*(tab.secYPos - 1)))
            history[varobj.var] = ax
            tab.secYPos += 1
            
    return ax
