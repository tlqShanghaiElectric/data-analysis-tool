# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 12:54:47 2018

@author: 12600632
"""

import os
import numpy as np
import tkinter as tk

# -------------------------- Load .$ file ----------------------------------
def load_dollar(varobj, pct_info, mainpage):

    fileDir = varobj.in_file
    
    if os.path.exists(fileDir):
        
        print(fileDir + ' Load')
        if len(pct_info) == 8:
            filename, id_var_in_file, vars_in_file, \
            num_vars, len_vars, datatype, varunit, timestep = \
            pct_info[0], pct_info[1], pct_info[2], pct_info[3], pct_info[4], \
            pct_info[5], pct_info[6], pct_info[7]
        if len(pct_info) == 7:
            filename, vars_in_file, \
            num_vars, len_vars, datatype, varunit, timestep = \
            pct_info[0], pct_info[1], pct_info[2], pct_info[3], pct_info[4], \
            pct_info[5], pct_info[6]
        
        # Change .% file to .$ file
        fileDir = fileDir.replace('%', '$')

        #Load data ------------------------------------------ 
        #print(fileName)
        fodID = open(fileDir, 'rb');
        if datatype == '4':
            readMethod = np.float32
        else:
            readMethod = np.float64
            
        data = np.fromfile(fodID, readMethod)
        y = data[list(range(id_var_in_file,\
                            num_vars*len_vars,\
                            num_vars))]
        x = np.arange(0, 
                      timestep* len_vars, 
                      timestep)

        fodID.close()
        
        """ 
        save time step 
        """
        varobj.step = timestep
        
        """
        save unit
        """
        varobj.unit = varunit[id_var_in_file]
        
        # if convert unit?
        if varobj.unit in ['A','A/T', 'A/TT']:
            unit_get = mainpage.unitCombobox.get()
            if unit_get in ['deg', 'deg/s', 'deg/s2']:
                y = y * 180/np.pi
            if unit_get in ['rpm']:
                y = y /2/np.pi*60
                
        varobj.data_y = y
        varobj.data_x = x
        
        
    else:
        print(fileDir + ' does not exist.')
        tk.messagebox.showerror('Load .$ error', fileDir + ' does not exist!')
    
    