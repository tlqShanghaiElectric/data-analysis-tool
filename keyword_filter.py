# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 09:37:40 2018

@author: 12600632
"""

"""
Keyword filter for convenient search
"""
import tkinter as tk

def keyword_filter(mainpage):
    var_enter = mainpage.enterVar.get()
    filt_list = mainpage.VarNameList
    varlist   = mainpage.varList
        
    if var_enter != '':
        var_enter = [x for x in var_enter.split(' ') if x != '']
        for i_var_enter in var_enter:
            temp_filt_list = []
            temp_filt_list = [x for x in filt_list 
                              if (i_var_enter.lower() in x.lower() and 
                                  x not in temp_filt_list)]
            filt_list = temp_filt_list

                     
    varlist.delete(0, tk.END)
    for i_word in filt_list:
        varlist.insert(tk.END, i_word)
        
    mainpage.varList.see(0)     
    
    # This is to hold color for the selected x axis signal
    if mainpage.tab_current.custom_x == 1:
        try:
            varlist.itemconfig(varlist.get(0, tk.END).index(
                    mainpage.data_custom_x.myXAxis_name.varNames[0]
                    ),background = 'green')
        except ValueError:
            pass