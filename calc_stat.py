# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 15:56:08 2018

@author: 12600632
"""

import tkinter as tk

# ----------------------- Calculate statistic data -----------------
def calc_stat(tab, varobj):
    
    x = varobj.data_x
    y = varobj.data_y
    
    if x != [] and y != []:
        
        mean_   = y.mean()
        max_    = y.max()
        min_    = y.min()
        std_    = y.std()
        
        ind_max = y.tolist().index(max_)
        ind_min = y.tolist().index(min_)
        
        t_max_   = x[ind_max]
        t_min_   = x[ind_min]
        
        varobj.max_     = max_
        varobj.min_     = min_ 
        varobj.mean_    = mean_ 
        varobj.std_     = std_ 
        varobj.t_max_   = t_max_ 
        varobj.t_min_   = t_min_ 
        
        tab.myMaster.statList.statTree.insert('', tk.END, 
                                     text = '{:6.3e}'.format(mean_),
                                     values = ('{:6.3e}'.format(max_),
                                               '{:6.3e}'.format(min_),
                                               '{:6.3e}'.format(std_),
                                               '{0:.2f}'.format(t_max_),
                                               '{0:.2f}'.format(t_min_)))
        
#        tab.stat_val.append([t_max_, max_,
#                             t_min_, min_,
#                             mean_,
#                             std_])