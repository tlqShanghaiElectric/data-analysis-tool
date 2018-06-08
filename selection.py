# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 10:36:17 2018

@author: 12600632
"""

import tkinter as tk

# -------------------------- Selection -------------------------------------
def selection_dir_var(master):
    '''
    return the selected:
    dirnames
    varnames
    varunits
    ylabels
    '''
        
    # select and get the directory
    sltId_wholeDir = master.dirTree.selection();
    if sltId_wholeDir == ():
        tk.messagebox.showerror('','Please select a directory.')
        return 0
    else:
        dirnames   = []
        for id_dirName in sltId_wholeDir:
            dirnames.append(
            master.dirTree.parent(id_dirName) + '\\' + \
            master.dirTree.item(id_dirName)['text']
            );  
        
    # select vars in the listbox and get the file names
    id_slt_vars  = master.varList.curselection();
    varnames    = [master.varList.get(i) for i in id_slt_vars];

    ''' Re-mapping 
    The index(or indices) of the selected variable(s) in the filtered list 
    is not the "real" index(or indices) of that in the total variable list,  
    so it has to be re-mapped.
    '''
    id_vars     = []
    for i_var in range(0, len(varnames)):
        id_vars.append(master.VarNameList.index(varnames[i_var])) 
            
    id_var_inlist = tuple(id_vars)

    # Variable Unit
#    varunits    = [master.varUnitList[i] for i in id_var_inlist];
   
    # y labels
    ylabels = create_ylabel(dirnames, master.VarNameList, id_var_inlist)
    

    # hold-on checkbox
#    hold_on_var = master.hold_on_var.get()
    
    return dirnames, varnames, ylabels, id_var_inlist
        
        
# Create labels
def create_ylabel(dirnames, varlist, id_var_inlist):
    ylabels = {}
    
    for i_dirName in dirnames:
        ylabs   = []
        for id_var in id_var_inlist:
            ylab = i_dirName +'\\'+ \
                   varlist[id_var]
            ylab = ylab.split('\\')[-3] + ' ' + \
                   ylab.split('\\')[-2] + \
                   ylab.split('\\')[-1]
            ylabs.append(ylab)
            
        ylabels[i_dirName] = ylabs
    return ylabels
            