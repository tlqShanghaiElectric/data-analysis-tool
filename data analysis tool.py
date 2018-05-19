# -*- coding: utf-8 -*-

"""
Created on Mon Mar 19 10:55:39 2018

@author: Jiasi
"""


# ================================= Import ==================================
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, dnd
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
                                               NavigationToolbar2TkAgg)
from matplotlib.figure import Figure
import matplotlib.ticker as tick 
import re
import os
from scipy import signal

# ============================ Home Page of App =============================
class HomePage:

    def __init__(self, master):
        
        plt.close('all')
        self.master = master
        self.master.title("SEDAP")

        self.num_filesInCase = []    # a list, number of files in one case   
        self.percentFileList = []    # save .% file names of all the loaded variables
        self.varUnitList     = []    # a list, save variable unit

        self.list_tabs      = []    # Set of added tabs, a list of frames
        self.num_tabs       = 0     # number of added tabs
#       self.tab_current    = ''    # currently selected tab
        
        self.ParentDirList  = []    # a List, parent directory, 
        self.list_num_vars  = []    # a list, number of variables in each read file
        self.list_len_vars  = []    # a list, length of variables in each read file
                                    # ...(Parent directory)/Groups/Cases/Files
        self.GroupNameList  = []    # save loaded group names
        self.CaseNameList   = []    # save loaded case names
        self.VarNameList    = []    # save loaded sensor names
        
        self.varDict        = {}    # dictionary for looking up .$ file corresponding to variables to plot
        
        


        # ------------------------ Menu bar------------------------------
        self.menuBar     = tk.Menu(self.master)
        self.master.config(menu = self.menuBar)
        
        # Menu bar buttons----------------------------------------------
        # File cascade
        self.fileMenu    = tk.Menu(self.menuBar, tearoff=0)  
        self.menuBar.add_cascade(label = 'File', menu = self.fileMenu)
        self.fileMenu.add_command(label='Add File', command = self.CALLBACK_OPEN_FILE);  
        self.fileMenu.add_command(label='Add Folder', command = self.CALLBACK_OPEN_DIR)  
        #self.fileMenu.add_command(label='Save', command = self.CALLBACK_SAVE)  
        self.fileMenu.add_separator()  
        self.fileMenu.add_command(label='Exit', command = self.CALLBACK_EXIT)  
        
        # About 
        self.aboutMenu   = tk.Menu(self.menuBar, tearoff = 0)
        self.menuBar.add_cascade(label = 'About', menu = self.aboutMenu)
        self.aboutMenu.add_command(label = 'About', command = self.CALLBACK_ABOUT)
        
        
        # --------------------- Main menu frames --------------------------------------
        self.frame1 = tk.Frame(self.master); self.frame1.grid(row = 1, column = 0, 
                         sticky = 'wesn')
        self.frame2 = tk.Frame(self.master); self.frame2.grid(row = 1, column = 1, 
                         rowspan = 2)   # figure frame
        self.frame3 = tk.Frame(self.master); 
        self.frame3.grid(row = 0, column = 0, columnspan = 8, sticky = 'w')   # treeview
        
        
        # --------------------- Frame 1 ------------------------------------
        # Directory --------------------------------------------------------
        self.dirTree = ttk.Treeview(self.frame3, height = 4)
        self.dirScrolly = ttk.Scrollbar(self.frame3, orient='vertical', 
                                        command=self.dirTree.yview)
        self.dirScrollx = ttk.Scrollbar(self.frame3, orient='horizontal', 
                                        command=self.dirTree.xview)
        self.dirTree.configure(yscroll=self.dirScrolly.set, 
                               xscroll=self.dirScrollx.set)
        self.dirTree.heading('#0', text='Directory', anchor='w')
        self.dirTree.grid(row=0, column=0, sticky = 'w')
        self.dirScrolly.grid(row=0, column=1, sticky='ns')
        self.dirScrollx.grid(row=3, column=0, sticky='ew')
        self.dirTree.column('#0', width = 500, minwidth = 500)

   
        # Right-click popup menu ----------------------------------------
        self.popup_dirTree  = tk.Menu(self.dirTree, tearoff = 0)                
        # Hide/show lines ----------------------------------------------------
        self.popup_dirTree.add_command(label="Hide/show",
                                       command=self.CALLBACK_HIDE_SHOW_LINE)
        # Delete directory --------------------------------------------------
#        self.popup_dirTree.add_command(label="Delete",
#                                       command=self.CALLBACK_delete_tree)
        
        self.dirTree.bind("<Button-3>", self.CALLBACK_DIRTREE_POPUP)        
        
        
        # Hold-on Checkbutton ----------------------------------------------------
        self.hold_on_var     = tk.IntVar(value = 1)
        self.holdCheckBut    = tk.Checkbutton(self.frame1, 
                                              text = 'Hold', 
                                              variable = self.hold_on_var)
        self.holdCheckBut.grid(row = 8, column = 0, sticky = 'e')   
        
        
        # Variable --------------------------------------------------------------------
        self.varLabel        = tk.Label(self.frame1, text = 'Variables')
        self.varLabel.grid    (row = 8, column = 0, sticky = 'W')
        
        self.varList         = tk.Listbox(self.frame1, width = 25, height = 15,
                                     selectmode = tk.EXTENDED,
                                     exportselection=0);
        self.varList.grid      (row = 9, column = 0, sticky = 'NSEW')
        
        self.varScrolly       = tk.Scrollbar(self.frame1);
        self.varScrolly.grid    (row = 9, column = 0, 
                                 sticky = 'NSE')
        self.varList.config(yscrollcommand=self.varScrolly.set)
        self.varScrolly.config(command=self.varList.yview)
        
        self.varScrollx       = tk.Scrollbar(self.frame1, orient=tk.HORIZONTAL);
        self.varScrollx.grid    (row = 10, column = 0, sticky = 'WES')
        self.varList.config(xscrollcommand=self.varScrollx.set)
        self.varScrollx.config(command=self.varList.xview)
        
#        # Drag and drop -------------------------------------------------
#        dnd_obj = DnD(master)
#        dnd_obj.bindtarget(self.dirTree, 'text/uri-list', '<Drag>', 
#                           self.drag, 
#                           ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
#        dnd_obj.bindtarget(self.dirTree, 'text/uri-list', '<DragEnter>', 
#                           self.drag_enter, 
#                           ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
#        dnd_obj.bindtarget(self.dirTree, 'text/uri-list', '<Drop>', 
#                           self.drop, 
#                           ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y','%D'))

        
        # Right-click popup menu ----------------------------------------
        self.popup_varList  = tk.Menu(self.varList, tearoff = 0)        
        # Customized x axis
        self.popup_varList.add_command(label="Set as x-axis",
                                       command=self.CALLBACK_SET_AS_X)
        self.popup_varList.add_command(label="Unset as x-axis",
                                       command=self.CALLBACK_UNSET_AS_X)
        
        # Hide/show lines ----------------------------------------------------
        self.popup_varList.add_command(label="Hide/show",
                                       command=self.CALLBACK_HIDE_SHOW_LINE)
        # line setting -------------------------------------------------------
        lineMenu        = tk.Menu(self.varList, tearoff = 0)
        lineColorMenu   = tk.Menu(self.varList, tearoff = 0)
        lineStyleMenu   = tk.Menu(self.varList, tearoff = 0)
        self.popup_varList.add_cascade(label="Line setting",
                                       menu = lineMenu)
        lineMenu.add_cascade(label="Line color",
                             menu = lineColorMenu)
        lineColorMenu.add_command(label="black",
                                  command=lambda: self.CALLBACK_LINE_COLOR('black'))
        lineColorMenu.add_command(label="red",
                                  command=lambda: self.CALLBACK_LINE_COLOR('red'))
        lineColorMenu.add_command(label="blue",
                                  command=lambda: self.CALLBACK_LINE_COLOR('blue'))

        lineMenu.add_cascade(label="Line style",
                             menu = lineStyleMenu)
        lineStyleMenu.add_command(label="--",
                                  command=lambda: self.CALLBACK_LINE_STYLE('--'))
        lineStyleMenu.add_command(label="-.",
                                  command=lambda: self.CALLBACK_LINE_STYLE('-.'))

        # bind ---------------------------------------------------------------
        self.varList.bind("<Button-3>", self.CALLBACK_VARLIST_POPUP)        
        
        
     
        
        # Create a Filter Entry ------------------------------------------------------
        self.enterVar        = tk.StringVar()
        self.filterLabel     = tk.Label(self.frame1, text = 'Filter')
        self.filterLabel.grid  (row = 6, column = 0, sticky = 'w')
        self.filterEntry     = tk.Entry(self.frame1, textvariable = self.enterVar)
        self.filterEntry.grid  (row = 7, column = 0, sticky = 'we')
        self.enterVar.trace("w", self.CALLBACK_FILTER)
        
        
        # Create a button to plot time-domain signals ---------------------------------
        self.varList.bind("<Double-Button-1>", lambda _: self.CALLBACK_PLOT(0))    
        self.PlotTBut      = tk.Button(self.frame1, text = 'Plot Time', 
                                  command = lambda: self.CALLBACK_PLOT(0), bg = 'green')
        self.PlotTBut.grid   (row = 13, column = 0, sticky = 'e')
        
        # Create a button to plot frequency-domain signals ----------------------------
        self.PlotFBut     = tk.Button(self.frame1, text = 'Plot Freq', 
                                 command = lambda: self.CALLBACK_PLOT(1), bg = 'cyan')
        self.PlotFBut.grid  (row = 13, column = 0, sticky = 'w')
        
        # Create a button to RESET FILES --------------------------------------
        self.RESETBut     = tk.Button(self.frame1, 
                                      text = 'RESET', 
                                      command = self.CALLBACK_RESET)
        self.RESETBut.grid  (row = 14, column = 0, sticky = 'w')

        # Create a button to CLEAR PLOT --------------------------------------
        self.CLEAR_PLOTBut     = tk.Button(self.frame1, 
                                           text = 'Clear Plot', 
                                           command = self.CALLBACK_CLEAR_PLOT)
        self.CLEAR_PLOTBut.grid  (row = 14, column = 0, sticky = 'e')

        
        # Create a button to create new tabs
        self.tab_create_but = tk.Button(self.frame1, 
                                        text = 'new tabs', 
                                        command = self.CALLBACK_NEW_TAB)
        self.tab_create_but.grid(row = 6, column = 0, sticky = 'ne')
        
        
        # Unit Conversion ----------------------------------------------------
        # Combobox
        self.unitCombobox    = ttk.Combobox(self.frame1)
        self.unitCombobox.grid(row = 12, column = 0, 
                               sticky = 'we')        
        self.unitCombobox['value'] = ('rad/s', 'deg/s', 'rpm')
        self.unitCombobox.set('rad/s')
        self.unitCombobox.bind("<<ComboboxSelected>>", self.CALLBACK_UNIT_CONVERSION)
       
        
        
        # ----------------------------- Frame 2 ------------------------------
        # Tabs ---------------------------------------------------------------
        self.tabMenu = ttk.Notebook(self.frame2)  # tab menu
        self.tabMenu.grid(row = 0, column = 0, sticky = 'w')
        
        # create the first tab
        self.list_tabs.append(NEW_TAB(self))
        self.tab_current = self.list_tabs[self.tabMenu.index('current')]
        self.data_custom_x  = CUSTOM_X(self)
        # When the current tab is changed
        self.tabMenu.bind("<<NotebookTabChanged>>", self.CALLBACK_SELECT_TAB)
        self.tabMenu.bind("<Double-Button-1>", self.CALLBACK_DEL_TAB)
        
        
        # Right-click popup menu ----------------------------------------
        self.popup_canvas  = tk.Menu(self.tab_current.tab, tearoff = 0)                
        # Hide/show lines ----------------------------------------------------
        self.popup_canvas.add_command(label="Axis setting",
                                       command=self.CALLBACK_AXIS_SETTING_POPUP)
        
        self.tab_current.canvas.plotCanvas.get_tk_widget().bind("<Button-3>", 
                                                        self.CALLBACK_CANVAS_POPUP)      
        
        
    # ======================= Define Button Callbacks =====================    
    # ----------------------- Drag and drop -------------------------------
    def drag(self, action, actions, type, win, X, Y, x, y, data):
        return action
        
    def drag_enter(self, action, actions, type, win, X, Y, x, y, data):
        self.varList.focus_force()
        return action
    
    def drop(self, action, actions, type, win, X, Y, x, y, data):
        files = data.split()
        for f in files:
            if os.path.isfile(f):
                OPEN_FILE(self, (f,))
            else:
                if os.path.isdir(f):
                    OPEN_DIR(self, f)
                else:
                    tk.messagebox.showerror('Please select a correct file/folder!')
   
    
    
    # -------------------- Delete a directory in treeview --------------------
    # To be continued ...
    def CALLBACK_delete_tree(self):
        self.dirTree.delete(self.dirTree.selection())
        
        dirNames    = self.dirTree.get_children()
        caseNames   = self.dirTree.get_children(dirNames)
        dirNames    = [self.dirTree.item(i_dir)['text'] for i_dir in dirNames]
        caseNames   = [self.dirTree.item(i_case)['text'] for i_case in caseNames]
        self.varList.delete(0, tk.END)
#        for i_dir in dirNames:
#            for i_case in caseNames:
#                folderName = i_dir + '/' + i_case
#                OPEN_DIR(self, folderName)
        
        
    # ----------------------- Axis setting pop-up window --------------------
    def CALLBACK_AXIS_SETTING_POPUP(self):
        self.axis_popup = AXIS_SETTING_POPUP(self)    
    
    # ----------------------- Line color ------------------------------------
    def CALLBACK_LINE_COLOR(self, color):
        LINE(self).line_color(color)    

    # ----------------------- Line style ----------------------------------
    def CALLBACK_LINE_STYLE(self, style):
        LINE(self).line_style(style)
        
    # ----------------------- Hide/show line --------------------------------
    def CALLBACK_HIDE_SHOW_LINE(self):
        LINE(self).hide_show_line()
        
    # ----------------------- Unit conversion ------------------------------
    def CALLBACK_UNIT_CONVERSION(self, *arg):
        print(self.unitCombobox.get())
    
    
    # ----------------------- Customized X Axis ----------------------------
    def CALLBACK_SET_AS_X(self):
        self.data_custom_x.SET_AS_X()


    def CALLBACK_UNSET_AS_X(self):
        self.data_custom_x.UNSET_AS_X()


    # ------------ Directory treeview Right-click-pop-up Event ----------------
    def CALLBACK_CANVAS_POPUP(self, event):
        try:
            self.popup_canvas.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_canvas.grab_release()
            
    # ------------ Directory treeview Right-click-pop-up Event ----------------
    def CALLBACK_DIRTREE_POPUP(self, event):
        try:
            self.popup_dirTree.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_dirTree.grab_release()

    # ----------------- Var list Right-click-pop-up Event ---------------------
    def CALLBACK_VARLIST_POPUP(self, event):
        try:
            self.popup_varList.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_varList.grab_release()
            
    # ----------------------- Delete a Tab ---------------------------------
    def CALLBACK_DEL_TAB(self, *arg):
        if len(self.tabMenu.tabs()) > 1:
            self.num_tabs -= 1
            self.list_tabs.pop(self.tabMenu.index('current'))
            self.tabMenu.forget(self.tabMenu.index('current'))


    # ---------------------------- Select the Current Tab --------------------
    # This function could be abandonded in the future
    def CALLBACK_SELECT_TAB(self, *arg):
        
        self.tab_current = self.list_tabs[self.tabMenu.index('current')]
        
            
    
    # ------------------------------ Open a folder ----------------------------
    def CALLBACK_OPEN_DIR(self):
        folderName = filedialog.askdirectory(title = 'Select a directory')
        OPEN_DIR(self, folderName)

        
    # ------------------------------ Open a file -----------------------------
    def CALLBACK_OPEN_FILE(self):
        fileNames = filedialog.askopenfilenames(title= "Select a file",
                                                filetypes = [('.%' , '.%*'),
                                                             ('all', '.*')]);
        OPEN_FILE(self, fileNames)

            
    # ------------------------------- Save a file-----------------------
    def CALLBACK_SAVE():
        #saveFileName = filedialog.asksaveasfilename(title= "Save a file")
        pass

    # ------------------------------- Exit -----------------------
    def CALLBACK_EXIT(self):
        self.master.destroy()   
    
    # ------------------------ Save axis settings -------------------
    def CALLBACK_SAVE_AXIS(self, *arg):
        SAVE_AXIS(self)

        
    # ------------------------ Refresh axis settings ----------------            
    def CALLBACK_REFRESH_AXIS(self):
        id_axis     = self.axis_popup.axisCombobox.current()
#        self.select = SELECTION(self) 
        if not self.tab_current.Plot_obj_List == []:
            if self.axis_popup.axisCombobox.get() != 'All':
                self.tab_current.Plot_obj_List[id_axis].AXIS_SET()
            else:
                i_data_begin = 0
                i_data_end   = len(self.tab_current.Plot_obj_List)
                for i_data in range(i_data_begin, i_data_end):
                    self.tab_current.Plot_obj_List[i_data].AXIS_SET()
            
    # ------------------------ Refresh axis settings ----------------            
    def CALLBACK_ABOUT(self):
        tk.messagebox.showinfo('About', 'Author: CAI Jiasi\n' + 
                                        'Last update: 2018/4/23\n' + 
                                        'EMail: caijs@shanghai-electric.com')

    # ------------------------ PLOT Time-domain ---------------------     
    # This callback function need well organization !!!      
    def CALLBACK_PLOT(self, plotFFT):
        
        if self.hold_on_var.get() == 0 and self.tab_current.custom_x == 0:
            self.CALLBACK_CLEAR_PLOT()
            
        
        # Selection ----------------------------------------------
        select_obj = SELECTION(self)
        if self.check_dir(select_obj) == 0:
            return 0
            

        self.tab_current.YLabels += select_obj.yLabel
        # Load .$ files ------------------------------------------
        data_obj = LOAD_DOLLAR(self, select_obj)

      
        # Y axis flag, 1 if this kind of sensor has been plotted, 0 for not
        flag = [0 for i in range(0, len(select_obj.varNames))]
        for select_var in select_obj.varNames:
            if select_var in self.tab_current.num_sensors:
                flag[select_obj.varNames.index(select_var)] = 1

        # plot time-domain ----------
        if plotFFT == 0:
            for i_axis in range(0, len(flag)):
                # Create plot object; one sensor, one y-axis, one object -----
                i_data = i_axis
                plot_data_obj = PLOT_DATA(self, self.tab_current, data_obj, select_obj)    

                while i_data < len(data_obj.data_y): 
                    # plot
                    if self.tab_current.custom_x == 0:
                        plot_data_obj.PLOT_T(i_data, i_axis, flag)
                        
                    else:
                        # if there is a customized x axis
                        plot_data_obj.PLOT_T(i_data, i_axis, flag, self.data_custom_x)
                    
                    i_data += len(select_obj.varNames)
                    self.tab_current.lns.append(plot_data_obj.f_handle)
                    
                    if flag[i_axis] == 0:
                        flag[i_axis] = 1
                # add plot objects into list
                self.tab_current.Plot_obj_List.append(plot_data_obj)                        
            self.tab_current.canvas.ax.legend(handles = self.tab_current.lns, 
                                                   loc = 'lower left',
                                                   bbox_to_anchor= (0, 1.00),
                                                   ncol = 3)
            
            # Update Combobox -----------
            self.tab_current.UPDATE_PLOTTEDVARS(select_obj)
#            # Update combobox values ----
#            self.axisCombobox['value'] = \
#            tuple(self.tab_current.num_sensors) 
            
            # Remember to update the canvas and toolbar!    
            # ThE ORDER OF THE FOLLOWING TWO LINES MATTERS !!!
            self.tab_current.toolbar.toolbar.update()  
            self.tab_current.canvas.plotCanvas.draw()


        # plot frequency-domain  -----  
        else:
            for i_axis in range(0, len(flag)):
                # Create plot object; one sensor, one y-axis, one object -----
                i_data = i_axis
                plot_data_obj = PLOT_DATA(self, self.tab_current, data_obj, select_obj)    

                while i_data < len(data_obj.data_y): 
                    # plot
                    plot_data_obj.PLOT_FFT(i_data, i_axis, flag)
                    i_data += len(select_obj.varNames)
                    self.tab_current.lns.append(plot_data_obj.f_handle)
                    
                    if flag[i_axis] == 0:
                        flag[i_axis] = 1
                # add plot objects into list
                self.tab_current.Plot_obj_List.append(plot_data_obj)                        
            self.tab_current.canvas.ax.legend(handles = self.tab_current.lns, 
                                                   loc = 'best')
            # Remember to update the canvas and toolbar!    
            # ThE ORDER OF THE FOLLOWING TWO LINES MATTERS !!!
            self.tab_current.toolbar.toolbar.update()  
            self.tab_current.canvas.plotCanvas.draw()
            
        # Calculate statistics ------
        CALC_STAT(self.tab_current, data_obj)
        

    # ------------------------ Check directory ----------------------            
    def check_dir(self, select):
        for j_dirName in  select.dirNames:
            for j_var in range(0, len(select.sltId_vars)):
                try:
                    filePrefix = [x for x in os.listdir(j_dirName)
                                  if '.$pm' in x][0].rsplit('.', 1)[-2]
                except IndexError:
                    tk.messagebox.showerror('','Select a directory!')
                    return 0
                    
                except OSError:
                    tk.messagebox.showerror('','Select a case!')
                    return 0
                    
        
                
                


        
    # ------------------------ Reset rRead Files ----------------------            
    def CALLBACK_RESET(self):
        reset_obj = RESET(self)
        reset_obj.RESET_READ_FILES()
    # ---------------------------- Clear Plot ---------------------------            
    def CALLBACK_CLEAR_PLOT(self):
        reset_obj = RESET(self)
        reset_obj.RESET_PLOT()
        
    # -------------------------- Create a new tab -------------------            
    def CALLBACK_NEW_TAB(self):
        self.list_tabs.append(NEW_TAB(self))
    
    def CALLBACK_FILTER(self, *arg):
        # this *arg must be added though Idk why
        FILTER(self, self.enterVar, self.varList)
        
    
# =========================  Classes of Functions ===========================
# ------------------------- Axis setting pop-up window ----------------------
class AXIS_SETTING_POPUP:
    def __init__(self, main):
        self.master = main
        self.axis_set_popup = tk.Toplevel()
        self.axis_set_popup.title('Axis setting')
        
        self.axis_set()

        
    def axis_set(self):
        # Axis settings -------------------------------------------------------------     
        # Combobox
        self.axisRefreshBut  = tk.Button(self.axis_set_popup, text = 'Refresh', 
                                         command = self.master.CALLBACK_REFRESH_AXIS)
        self.axisRefreshBut.grid(row = 1, column = 5, 
                                 rowspan = 2, sticky = 'wens')
        self.axisCombobox    = ttk.Combobox(self.axis_set_popup)
        self.axisCombobox.grid(row = 0, column = 0, 
                               columnspan = 4, sticky = 'we')  
        # Axis ranges frame --------------------------------------------------
        self.yMax       = tk.StringVar()
        self.yMin       = tk.StringVar()
        self.xMax       = tk.StringVar()
        self.xMin       = tk.StringVar()
        # y-axis max
        self.yMaxLabel     = tk.Label(self.axis_set_popup, text = 'y-axis max', width = 10)
        self.yMaxLabel.grid  (row = 1, column = 2, sticky = 'nw')
        self.yMaxEntry     = tk.Entry(self.axis_set_popup, width = 10, textvariable = self.yMax)
        self.yMaxEntry.grid  (row = 1, column = 1, sticky = 'nw')
        # y-axis min
        self.yMinLabel     = tk.Label(self.axis_set_popup, text = 'y-axis min', width = 10)
        self.yMinLabel.grid  (row = 2, column = 2, sticky = 'nw')
        self.yMinEntry     = tk.Entry(self.axis_set_popup, width = 10, textvariable = self.yMin)
        self.yMinEntry.grid  (row = 2, column = 1, sticky = 'nw')
        # x-axis max
        self.xMaxLabel     = tk.Label(self.axis_set_popup, text = 'x-axis max', width = 10)
        self.xMaxLabel.grid  (row = 1, column = 4, sticky = 'nw')
        self.xMaxEntry     = tk.Entry(self.axis_set_popup, width = 10, textvariable = self.xMax)
        self.xMaxEntry.grid  (row = 1, column = 3, sticky = 'nw')
        # x-axis min
        self.xMinLabel     = tk.Label(self.axis_set_popup, text = 'x-axis min', width = 10)
        self.xMinLabel.grid  (row = 2, column = 4, sticky = 'nw')
        self.xMinEntry     = tk.Entry(self.axis_set_popup, width = 10, textvariable = self.xMin)
        self.xMinEntry.grid  (row = 2, column = 3, sticky = 'nw')
        self.yMax.trace('w', self.master.CALLBACK_SAVE_AXIS)
        self.yMin.trace('w', self.master.CALLBACK_SAVE_AXIS)
        self.xMax.trace('w', self.master.CALLBACK_SAVE_AXIS)
        self.xMin.trace('w', self.master.CALLBACK_SAVE_AXIS)
        
        # Combobox values
        self.axisCombobox['value'] = self.master.tab_current.num_sensors 
        
## ----------------------------  Drag and drop ---------------------------------
#class DnD:
#    def __init__(self, tkroot):
#        self._tkroot = tkroot
#        tkroot.tk.eval('package require tkdnd')
#        # make self an attribute of the parent window for easy access in child classes
#        tkroot.dnd = self
#    
#    def bindsource(self, widget, type=None, command=None, arguments=None, priority=None):
#        '''Register widget as drag source; for details on type, command and arguments, see bindtarget().
#        priority can be a value between 1 and 100, where 100 is the highest available priority (default: 50).
#        If command is omitted, return the current binding for type; if both type and command are omitted,
#        return a list of registered types for widget.'''
#        command = self._generate_callback(command, arguments)
#        tkcmd = self._generate_tkcommand('bindsource', widget, type, command, priority)
#        res = self._tkroot.tk.eval(tkcmd)
#        if type == None:
#            res = res.split()
#        return res
#    
#    def bindtarget(self, widget, type=None, sequence=None, command=None, arguments=None, priority=None):
#        '''Register widget as drop target; type may be one of text/plain, text/uri-list, text/plain;charset=UTF-8
#        (see the man page tkDND for details on other (platform specific) types);
#        sequence may be one of '<Drag>', '<DragEnter>', '<DragLeave>', '<Drop>' or '<Ask>' ;
#        command is the callback associated with the specified event, argument is an optional tuple of arguments
#        that will be passed to the callback; possible arguments include: %A %a %b %C %c %D %d %L %m %T %t %W %X %x %Y %y
#        (see the tkDND man page for details); priority may be a value in the range 1 to 100 ; if there are
#        bindings for different types, the one with the priority value will be proceeded first (default: 50).
#        If command is omitted, return the current binding for type, where sequence defaults to '<Drop>'.
#        If both type and command are omitted, return a list of registered types for widget.'''
#        command = self._generate_callback(command, arguments)
#        tkcmd = self._generate_tkcommand('bindtarget', widget, type, sequence, command, priority)
#        res = self._tkroot.tk.eval(tkcmd)
#        if type == None:
#            res = res.split()
#        return res
#    
#    def clearsource(self, widget):
#        '''Unregister widget as drag source.'''
#        self._tkroot.tk.call('dnd', 'clearsource', widget)
#    
#    def cleartarget(self, widget):
#        '''Unregister widget as drop target.'''
#        self._tkroot.tk.call('dnd', 'cleartarget', widget)
#    
#    def drag(self, widget, actions=None, descriptions=None, cursorwindow=None, command=None, arguments=None):
#        '''Initiate a drag operation with source widget.'''
#        command = self._generate_callback(command, arguments)
#        if actions:
#            if actions[1:]:
#                actions = '-actions {%s}' % ' '.join(actions)
#            else:
#                actions = '-actions %s' % actions[0]
#        if descriptions:
#            descriptions = ['{%s}'%i for i in descriptions]
#            descriptions = '{%s}' % ' '.join(descriptions)
#        if cursorwindow:
#            cursorwindow = '-cursorwindow %s' % cursorwindow
#        tkcmd = self._generate_tkcommand('drag', widget, actions, descriptions, cursorwindow, command)
#        self._tkroot.tk.eval(tkcmd)
#                
#    def _generate_callback(self, command, arguments):
#        '''Register command as tk callback with an optional list of arguments.'''
#        cmd = None
#        if command:
#            cmd = self._tkroot._register(command)
#            if arguments:
#                cmd = '{%s %s}' % (cmd, ' '.join(arguments))
#        return cmd
#    
#    def _generate_tkcommand(self, base, widget, *opts):
#        '''Create the command string that will be passed to tk.'''
#        tkcmd = 'dnd %s %s' % (base, widget)
#        for i in opts:
#            if i != None:
#                tkcmd += ' %s' % i
#        return tkcmd

# ----------------------------- Line settings ------------------------------
class LINE:
    def __init__(self, main):
        
        self.master = main
        
    # hide/show line --------------------------------------------------------
    def hide_show_line(self):
        
        id_lines = self.line_select()      
        
        for line in id_lines:
            self.master.tab_current.lns[line].set_visible(not self.master.tab_current.lns[line].get_visible())
        
        self.master.tab_current.canvas.plotCanvas.draw()
        
    # change line color -----------------------------------------------------
    def line_color(self, color):
        
        id_lines = self.line_select()
        
        for line in id_lines:
            self.master.tab_current.lns[line].set_color(color)
            self.master.tab_current.canvas.ax.get_legend().legendHandles[line].set_color(color)
        
        self.master.tab_current.canvas.plotCanvas.draw()

    # line style --------------------------------------------------------
    def line_style(self, style):
        
        id_lines = self.line_select()      
        
        for line in id_lines:
            self.master.tab_current.lns[line].set_linestyle(style)
            self.master.tab_current.canvas.ax.get_legend().legendHandles[line].set_linestyle(style)

        self.master.tab_current.canvas.plotCanvas.draw()

    # select line -----------------------------------------------------------
    def line_select(self):
        select      = SELECTION(self.master)
        theLineDir  = []
        id_lines    = []
        # save selected lines' directories (i.e. labels)
        for i_dir in select.dirNames:
            for i_var in select.varNames:
                theLineDir.append (i_dir  + '/ ' + \
                                   i_var)
        
        # find the corresponding indices
        for line in theLineDir:
            id_lines += [i for i, v in 
                     enumerate(self.master.tab_current.YLabels) if v == line]
            
        return id_lines


# ----------------------------- Customized X axis ---------------------------
class CUSTOM_X:
    def __init__(self, master):
        
        self.master = master
        self.master.tab_current.custom_x = 0
        
    def SET_AS_X(self):
        if self.master.tab_current.custom_x == 1:
            self.master.data_custom_x.UNSET_AS_X()
        
        if self.master.dirTree.selection() != ():
            self.myXAxis_name    = SELECTION(self.master)
            
        try:
            self.myXAxis_name
            self.master.varList.itemconfig(self.master.varList.curselection(), 
                                           background = 'green')
            self.xAxis_data      = LOAD_DOLLAR(self.master, self.myXAxis_name)
            print('Customized x axis: ' + self.myXAxis_name.varNames[0])
            
            self.master.tab_current.custom_x = 1
        except AttributeError:
            tk.messagebox.showerror('','Select a directory!')
            pass
        
    def UNSET_AS_X(self):
        try:
            self.master.varList.itemconfig(self.master.data_custom_x.myXAxis_name.sltId_vars, 
                                           background = 'white')
            self.master.data_custom_x = CUSTOM_X(self.master)
            
        except AttributeError:
            pass
        print('X axis: Time')

# ----------------------------- Reset data  ---------------------------------
class RESET:
    
    def __init__(self, myMaster):
        
        self.master = myMaster
        self.tab    = myMaster.tab_current
        
    def RESET_PLOT(self):    
        # clear tab configurations
        self.tab.num_sensors    = ['All']     # a list, sensors that have been plotted
        self.tab.Plot_obj_List  = []     # a list, save plot objects
        self.tab.CALLBACK_CLEAR_STAT()   # clear statistics list
        plt.close('all')
        del self.tab.canvas              # re-create canvas
        self.tab.canvas  = self.tab.CALLBACK_CREATE_CANVAS()
        del self.tab.toolbar             # re-create toolbar
        self.tab.toolbar = self.tab.CALLBACK_CREATE_TOOLBAR()  
        self.tab.canvas.plotCanvas.get_tk_widget().bind("<Button-3>", 
                                        self.master.CALLBACK_CANVAS_POPUP) 
        self.tab.lns            = []
        self.tab.hostFigOrTwinx = []        # plot handles, save hostFig or hostFig.twinx()
        self.tab.sensor_history = []        # save all sensors in history
        self.tab.firstTwinx     = 0
        self.tab.secYPos        = 1         # secondary y axes postion
        self.tab.YLabels        = []
        self.tab.canvas.ax.legend(handles = self.tab.lns, 
                                       loc = 'lower left',
                                       bbox_to_anchor= (0, 1.00),
                                       ncol = 3)

        

        self.master.CALLBACK_UNSET_AS_X()        
        
        
        
    def RESET_READ_FILES(self):
        self.RESET_PLOT()
        # clear lists of directories and sensors
        for i in self.master.dirTree.get_children():
            self.master.dirTree.delete(i)
        self.master.varList.delete(0,tk.END)
        self.master.num_filesInCase = []    # a list, number of files in one case   
        self.master.percentFileList  = []    # save .% file names of all the loaded variables
        self.varUnitList            = []    # a list, save variable unit
        self.master.list_num_vars   = []    # a list, number of variables in each read file
        self.master.list_len_vars   = []    # a list, length of variables in each read file
        
        self.master.ParentDirList   = []    # a List, parent directory, 
                                    # ...(Parent directory)/Groups/Cases/Files
        self.master.GroupNameList   = []    # save loaded group names
        self.master.CaseNameList    = []    # save loaded case names
        self.master.VarNameList     = []    # save loaded sensor names
      
        
# ----------------------------- Axis Selection ------------------------------     
class SAVE_AXIS:
    
    def __init__(self, myMaster):
        self.master     = myMaster
        self.id_axis    = myMaster.axis_popup.axisCombobox.current()
        self.name_axis  = myMaster.axis_popup.axisCombobox.get()
        self.select     = SELECTION(myMaster)
        self.GET_AXIS_LIM()
        
        
    def GET_AXIS_LIM(self):

        yMax    = self.master.axis_popup.yMaxEntry.get()
        yMin    = self.master.axis_popup.yMinEntry.get()
        xMax    = self.master.axis_popup.xMaxEntry.get()
        xMin    = self.master.axis_popup.xMinEntry.get()
        
        if self.name_axis == 'All':
            i_data_begin    = 0
            i_data_end      = len(self.master.tab_current.Plot_obj_List)
        else:
            i_data_begin    = self.id_axis
            i_data_end      = self.id_axis + 1
        
        if self.master.tab_current.Plot_obj_List != []:
            for i_data in range(i_data_begin, i_data_end):
    
                if xMin != '':
                    try:
                        self.master.tab_current. \
                        Plot_obj_List[i_data].xMin = float(xMin)
                    except ValueError:
                        pass
                        
                if xMax != '':   
                    try:
                        self.master.tab_current. \
                        Plot_obj_List[i_data].xMax = float(xMax)
                    except ValueError:
                        pass
                if yMin != '':    
                    try:
                        self.master.tab_current. \
                        Plot_obj_List[i_data].yMin = float(yMin)
                    except ValueError:
                        pass
                if yMax != '':    
                    try:
                        self.master.tab_current. \
                        Plot_obj_List[i_data].yMax = float(yMax)  
                    except ValueError:
                        pass




# ----------------------------- Plot Data -----------------------------------
class PLOT_DATA():
    

    
    def __init__(self, myMaster, myTab, data, select):
        self.master     = myMaster
        self.myTab      = myTab
        self.data       = data
        self.select     = select
        self.fig1       = 0
        self.yMax       = ''
        self.yMin       = ''
        self.xMax       = ''
        self.xMin       = ''    
        self.myvarNames = self.select.varNames * len(self.select.varNames) \
                                                * len(self.select.dirNames)
        self.colors     = ['b', 'r', 'g', 'm', 'y', 'k']
        self.lines      = ['-', '--', '-.', ':']
        self.lineMarkers= ['o', '^', 's', '*']
        
    def PLOT_T(self, i_data, i_axis, flag_plot, *arg):

        # To be honest, I do not know how to make the following code conciser.
        # All is to make logic decisions whether to create a primary or secondary 
        # y axis/axes without overlapping, i.e. to ARRANGE Y AXIS(AXES)
        # The logic is based on three factors: 
        # 1. is i_data sensor the first sensor of the current selection object?
        # 2. has i_data sensor been plotted ever?
        # 3. is i_data the first sensor of the current tab?
        
        # classify y axis ----------------------------------------------------

        if i_data == 0:
            
            if flag_plot[i_axis] == 1:
                
                if self.myTab.sensor_history == []:
                    #print('YYY')
                    pass
                else:
                    #print('YYN')
                    #print(self.myvarNames[i_data])
                    self.myTab.sensor_history.append(self.myvarNames[i_data])
                    id_fig = [i for i, x in enumerate(self.myTab.sensor_history) \
                              if x == self.myvarNames[i_data]][0]
                    self.fig1 = self.myTab.hostFigOrTwinx[id_fig]
                    self.myTab.hostFigOrTwinx.append(self.fig1)
                    self.i_color = len(self.myTab.sensor_history)
                    
            else:
                
                if self.myTab.sensor_history == []:
                    #print('YNY')
                    #print(self.myvarNames[i_data])
                    self.myTab.sensor_history.append(self.myvarNames[i_data])
                    self.fig1 = self.myTab.canvas.ax
                    self.myTab.hostFigOrTwinx.append(self.fig1)
                    # indices of colors of sensors
                    self.i_color   = len(self.myTab.sensor_history)

                    

                else:
                    #print('YNN')
                    #print(self.myvarNames[i_data])
                    self.myTab.sensor_history.append(self.myvarNames[i_data])
                    self.i_color   = len(self.myTab.sensor_history)
                    self.fig1 = self.myTab.canvas.ax.twinx()
                    self.myTab.hostFigOrTwinx.append(self.fig1)
                    #self.i_pos     = len(self.myTab.num_sensors)
                    self.i_pos  = self.myTab.secYPos
                    if self.myTab.firstTwinx != 0:
                        self.fig1.spines['right'].set_position(('outward', 75*(self.i_pos-1))) 
                    self.myTab.firstTwinx = 1
                    self.myTab.secYPos += 1
 
                    
        else:
            
            if flag_plot[i_axis] == 1:
                
                if self.myTab.sensor_history == []:
                    #print('NYY')
                    pass
                else:
                    #print('NYN')
                    #print(self.myvarNames[i_data])
                    self.myTab.sensor_history.append(self.myvarNames[i_data])
                    id_fig = [i for i, x in enumerate(self.myTab.sensor_history) \
                              if x == self.myvarNames[i_data]][0]
                    self.i_color   = len(self.myTab.sensor_history)
                    self.fig1 = self.myTab.hostFigOrTwinx[id_fig]
                    self.myTab.hostFigOrTwinx.append(self.fig1)
            else:
                
                if self.myTab.sensor_history == []:
                    #print('NNY')
                    pass
                else:
                    #print('NNN')
                    #print(self.myvarNames[i_data])
                    self.myTab.sensor_history.append(self.myvarNames[i_data])
                    self.fig1 = self.myTab.canvas.ax.twinx()  
                    self.myTab.hostFigOrTwinx.append(self.fig1)
                    self.i_color   = len(self.myTab.sensor_history)
                    #self.i_pos     = len(self.myTab.num_sensors) 
                    self.i_pos  = self.myTab.secYPos
                    if self.myTab.firstTwinx != 0:
                        self.fig1.spines['right'].set_position(('outward', 75*(self.i_pos-1))) 
                    self.myTab.firstTwinx = 1
                    self.myTab.secYPos += 1  
        
        # plot ------------------------------------------------------------ 
        if arg:
            xData = arg[0].xAxis_data.data_y[0]
            # when use scatter, self.f_handle = scatter;
            # when use plot, self.f_handle, = plot !!!
            self.f_handle = self.fig1.scatter(xData, 
                                self.data.data_y[i_data], 
                          color = self.colors[(self.i_color-1)%len(self.colors)],
                          linestyle = self.lines[max(0, self.i_color - len(self.colors)) %len(self.lines)],
                          label = self.select.yLabel[i_data].split('/')[-3] + ' ' + \
                                  self.select.yLabel[i_data].split('/')[-2] + \
                                  self.select.yLabel[i_data].split('/')[-1])  
            self.fig1.set_xlabel(arg[0].myXAxis_name.varNames[0])
            # scatter has face color and edge color; 
            self.fig1.set_ylabel(self.select.yLabel[i_data].split('/')[-1],
                                 color = self.f_handle.get_facecolor()[0])            
        else:
            xData = self.data.data_x[i_data]
            self.f_handle, = self.fig1.plot(xData, 
                                self.data.data_y[i_data], 
                          color = self.colors[(self.i_color-1)%len(self.colors)],
                          linestyle = self.lines[max(0, self.i_color - len(self.colors)) %len(self.lines)],
                          label = self.select.yLabel[i_data].split('/')[-3] + ' ' + \
                                  self.select.yLabel[i_data].split('/')[-2] + \
                                  self.select.yLabel[i_data].split('/')[-1])
            self.fig1.set_xlabel('Time, s')
            # axis label
            self.fig1.set_ylabel(self.select.yLabel[i_data].split('/')[-1],
                                 color = self.f_handle.get_color())
        
        # grid on
        self.fig1.grid(alpha = 0.5, linestyle = '--')
        # y-axis tick format
        ymajor_formatter = tick.FormatStrFormatter('%2.2e')
        self.fig1.yaxis.set_major_formatter(ymajor_formatter)
        self.fig1.set_yticks(np.linspace(self.fig1.get_ybound()[0], 
                                 self.fig1.get_ybound()[1],
                                 10))
        


            
    def PLOT_FFT(self, i_data, i_axis, flag_plot, *arg):
        ## Classify y axes
        #self.CLASSIFY_Y(i_data, i_axis, flag_plot, *arg)
        
        self.f_data   = CALC_FFT(self.data)
        
        self.fig1 = self.myTab.canvas.ax
        
        # semilogy to plot power density - frequency    
        self.f_handle, = self.fig1.semilogy(self.f_data.freq[i_data], 
                                            self.f_data.PD[i_data], 
                      label = self.select.yLabel[i_data].split('/')[-2] + \
                              self.select.yLabel[i_data].split('/')[-1])        
        
        # grid on
        self.fig1.grid(alpha = 0.5, linestyle = '--')
        # y-axis tick format
        ymajor_formatter = tick.FormatStrFormatter('%2.2e')
        self.fig1.yaxis.set_major_formatter(ymajor_formatter)
        
        # axis label
        self.fig1.set_ylabel('Spectral Energy Density')
        self.fig1.set_xlabel('Frequency, Hz')
        
        # if secondary axis
        if i_axis != 0:
            self.fig1.spines['right'].set_position(('outward', 75*(i_axis-1))) 
                            
    
    def AXIS_SET(self):
        
        if self.xMin != '':
            self.fig1.set_xlim(xmin = self.xMin)
        if self.xMax != '':
            self.fig1.set_xlim(xmax = self.xMax)
        if self.yMin != '':
            self.fig1.set_ylim(ymin = self.yMin)
        if self.yMax != '':
            self.fig1.set_ylim(ymax = self.yMax)
            
        self.myTab.canvas.plotCanvas.draw()
    


      


# ----------------------- Calculate FFT ----------------------------
class CALC_FFT:
    def __init__(self, data):
        
        self.freq = []
        self.PD = []
        
        win_hann = signal.get_window('hann', 1024);
        
        for i_data in range(0, len(data.data_y)):
            
            fs = 1/data.step[i_data]            
            
            f, Pxx_den  =   signal.periodogram(data.data_y[i_data], fs, 
                                               win_hann, nfft = 1024, 
                                               detrend = 'constant', 
                                               return_onesided = True,
                                               scaling = 'density')
            self.freq.append(list(f));
            self.PD.append(list(Pxx_den));

        
# ----------------------- Calculate statistic data -----------------
class CALC_STAT:
    
    def __init__(self, tab, data):
        for i_data in range(0, len(data.data_y)):
            if data.data_x[i_data] != [] and data.data_y[i_data] != []:
                stat_mean   = np.mean(data.data_y[i_data])
                stat_min    = np.min(data.data_y[i_data])
                stat_max    = np.max(data.data_y[i_data])
                stat_std    = np.std(data.data_y[i_data])
                
                tab.statList.statTree.insert('', tk.END, 
                                             text = '{:6.3e}'.format(stat_mean),
                                             values = ('{:6.3e}'.format(stat_min),
                                                       '{:6.3e}'.format(stat_max),
                                                       '{:6.3e}'.format(stat_std)))
    
    
# -------------------------- Load .$ file ----------------------------------
class LOAD_DOLLAR:
    def __init__(self, myMaster, select):
        self.data_y = []
        self.data_x = []
        self.step   = []
        
        for j_dirName in  select.dirNames:
            for j_var in range(0, len(select.sltId_vars)):
                filePrefix = [x for x in os.listdir(j_dirName) if '.$pm' in x][0].rsplit('.', 1)[-2]
                fileDir =   j_dirName +  '/' + \
                            filePrefix + '.' + \
                            myMaster.varDict[select.varNames[j_var]].split('.')[-1]
    
                if os.path.exists(fileDir):
                    
                    print(fileDir + ' Load')
                    # (id_dataFile) th .% file
                    dataInfo_obj \
                    = LOAD_PERCENT(fileDir, myMaster, select.sltId_vars[j_var])
                    self.step.append(dataInfo_obj.timeStep)
                    # Change .% file to .$ file
                    fileDir = fileDir.replace('%', '$')

                    #Load data ------------------------------------------ 
                    #print(fileName)
                    fodID = open(fileDir, 'rb');
                    if dataInfo_obj.dataType == '4':
                        readMethod = np.float32
                    else:
                        readMethod = np.float64
                        
                    data = np.fromfile(fodID, readMethod)
                    self.data_y.append(data[list(range( dataInfo_obj.idx_var_in_file,\
                                                  dataInfo_obj.num_vars*dataInfo_obj.len_vars,\
                                                  dataInfo_obj.num_vars))])
                    self.data_x.append(np.arange(0, 
                                                 dataInfo_obj.timeStep* dataInfo_obj.len_vars, 
                                                 dataInfo_obj.timeStep))
                    
                    fodID.close();
                    
                    # if convert unit?
                    if myMaster.varUnitList[select.sltId_vars[j_var]] in ['A','A/T', 'A/TT']:
                        if myMaster.unitCombobox.get() in ['deg', 'deg/s', 'deg/s2']:
                            self.data_y[-1] = self.data_y[-1] * 180/np.pi
                        if myMaster.unitCombobox.get() in ['rpm']:
                            self.data_y[-1] = self.data_y[-1] /2/np.pi*60
                        

                    
                else:
                    print(fileDir + ' does not exist.')
                    tk.messagebox.showerror('Load .$ error', fileDir + ' does not exist!')
                    break
                    self.data_y.append([])
                    self.data_x.append([])
                        
            
            

# -------------------------- Selection -------------------------------------
class SELECTION:
    
    def __init__(self, myMaster):
        
        # select and get the directory
        self.sltId_wholeDir = myMaster.dirTree.selection()
        if not self.sltId_wholeDir:
            tk.messagebox.showerror('','Please select a directory.')
            return 0
        else:
            dirNames = []
            for wholedir in myMaster.dirTree.selection():
                dirNames.append(myMaster.dirTree.parent(wholedir) + '/' + \
                             myMaster.dirTree.item(wholedir)['text'])
            self.dirNames = dirNames
            # self.dirNames   = [myMaster.dirTree.parent(myMaster.dirTree.selection()) + '/' + \
            #                 myMaster.dirTree.item(myMaster.dirTree.selection())['text']];  
#            print(self.dirNames)
            
        # select vars in the listbox and get the file names
        sltId_vars  = myMaster.varList.curselection();
        self.varNames    = [myMaster.varList.get(i) for i in sltId_vars];
#        print(self.varNames)

        # Re-mapping -------------------------------------------------------
        # The index(or indices) of the selected variable(s) in the filtered list 
        # is not the "real" index(or indices) of that in the total variable list,  
        # so it has to be re-mapped.
        id_vars     = []
        for i_var in range(0, len(self.varNames)):
            id_vars.append(myMaster.VarNameList.index(self.varNames[i_var])) 
                
        self.sltId_vars  = tuple(id_vars)
#        print(self.sltId_vars)

        # Variable Unit
        self.varUnit    = [myMaster.varUnitList[i] for i in self.sltId_vars];
       
        # y labels
        self.yLabel = []   
        self.CREATE_YLABEL(myMaster)
        
        
        # hold-on checkbox
        self.hold_on_var = myMaster.hold_on_var.get()
        
        
    # Create labels
    def CREATE_YLABEL(self, myMaster):
        for i_dirName in self.dirNames:
            for i_var in range(0, len(self.sltId_vars)):
                self.yLabel.append(i_dirName +'/ '+\
                              myMaster.VarNameList[self.sltId_vars[i_var]])
            
    


# ----------------------------- Create new lists for statistics -------------
class CREATE_STAT():
    def __init__(self, myMaster):
        # Show statistics ------------------------------------------------------
        self.frame_stat = myMaster
        self.create_stat()
        
    def create_stat(self):
        self.statTree = ttk.Treeview(self.frame_stat, height = 4,
                                     columns = ('1', '2', '3'))
        self.statTree.grid(row = 0, column = 3)
        self.statScrolly = ttk.Scrollbar(self.frame_stat, orient='vertical', 
                                        command=self.statTree.yview)
        self.statScrolly.grid(row = 0, column = 4, sticky = 'ns')
        self.statTree.configure(yscroll=self.statScrolly.set)
        
        self.statTree.heading('#0', text = 'Mean')
        self.statTree.heading(1,    text = 'Max')
        self.statTree.heading(2,    text = 'Min')
        self.statTree.heading(3,    text = 'Std')
        self.statTree.column('#0', width = 100,  anchor='w')
        self.statTree.column(1,    width = 100,  anchor='w')
        self.statTree.column(2,    width = 100,  anchor='w')
        self.statTree.column(3,    width = 100,  anchor='w')
        
        
    
# -------------------- Create a new navigation toolbar ----------------------
class CREATE_TOOLBAR():
    def __init__(self, myMaster, target):
        # it seems that toolbar cannot use .grid() but only .pack(), 
        # so put it in a standalone frame.
        frame_Toolbar = tk.Frame(myMaster)
        frame_Toolbar.grid(row = 1, column = 0, sticky = 'w')
        self.toolbar = NavigationToolbar2TkAgg(target.plotCanvas, frame_Toolbar)   
        
        
# ----------------------------- Create a new canvas -------------------------
class CREATE_CANVAS():
    def __init__(self, myMaster):
        # Create a canvas to show plots -------------------------------------
        page = myMaster.myMaster.master
        width = page.winfo_reqwidth()
        self.hostFig, self.ax = plt.subplots(figsize = (20,8), dpi = 60)
        self.hostFig.subplots_adjust(left = 0.08, right = 0.82)
        self.plotCanvas = FigureCanvasTkAgg(self.hostFig, master = myMaster.tab)
        self.plotCanvas.get_tk_widget().grid(row = 0, column = 0, 
                                columnspan = 2, sticky = 'WEN')  
        self.ax.legend(handles  = myMaster.lns, 
                                   loc = 'lower left',
                                   bbox_to_anchor= (0, 1.00),
                                   ncol = 3)
        

# ----------------------------- Create a New Tab -----------------------------
class NEW_TAB():
    # main = Main
    def __init__(self, main):
        
        self.myMaster       = main
        self.num_sensors    = ['All']   # a list, sensors that have been plotted, no duplicates
        self.Plot_obj_List  = []        # a list, save plot objects
        self.lns            = []        # legends
        self.hostFigOrTwinx = []        # plot handles, save hostFig or hostFig.twinx()
        self.sensor_history = []        # save all sensor names in history
        self.firstTwinx     = 0         # a flag, will be set to 1 if the first secondary y axis is created
        self.secYPos        = 1         # secondary y axes postion
        self.setX           = 0         # a flag, 0 for time x axis,
                                        #         1 for customized x axis
        self.YLabels        = []
        self.custom_x       = 0         # 0 for no customized x axis is selected,
                                        # 1 for one sensor is selected

        # hopefully the maximum number of tabs should not be over 10
        self.myMaster.num_tabs += 1
        self.tab = tk.Frame(self.myMaster.tabMenu)   
        self.myMaster.tabMenu.add(self.tab, text= 'Tab ' + str(len(self.myMaster.tabMenu.tabs())+1))
        
        # Create a new canvas -------------------------------------
        self.canvas = self.CALLBACK_CREATE_CANVAS()
        self.myMaster.tabMenu.select(self.tab) # Select the created tab, just for convenience
        
        # Create a new navigation toolbar -------------------------
        self.toolbar = self.CALLBACK_CREATE_TOOLBAR()
        
        # Create new lists for statistics -------------------------
        self.statList = self.CALLBACK_CREATE_STAT()      
        
        #self.new_next_tab()
    
    def CALLBACK_CREATE_STAT(self):
        return CREATE_STAT(self.myMaster.frame3)
    
    def CALLBACK_CREATE_TOOLBAR(self):
        return CREATE_TOOLBAR(self.tab, self.canvas)
        
    def CALLBACK_CREATE_CANVAS(self):
        return CREATE_CANVAS(self)
                
    def CALLBACK_CLEAR_STAT(self):
        self.statList.statTree.delete(*self.statList.statTree.get_children())

        
    def UPDATE_PLOTTEDVARS(self, select):
        # add new plotted sensors
        for i in range(0, len(select.varNames)):
            if select.varNames not in self.num_sensors:
                self.num_sensors.insert(-1, select.varNames[i])

    def CLEAR_PLOTTEDVARS(self):
#        self.myMaster.axisCombobox['value'] = ()
#        self.myMaster.axisCombobox.set('')
        pass
        
    def new_next_tab(self):
        self.tab = tk.Frame(self.myMaster.tabMenu)   
        self.myMaster.tabMenu.add(self.tab, text = '*')
        
# ------------------------------ Variable Filter -------------------------
class FILTER():
    def __init__(self, master, enterVar, varList):
        var_enter = enterVar.get()
        filt_List = master.VarNameList
        
            
        if var_enter != '':
            var_enter = [x for x in enterVar.get().split(' ') if x != '']
            for i_var_enter in var_enter:
                temp_filt_List = []
                temp_filt_List = [x for x in filt_List 
                                  if (i_var_enter.lower() in x.lower() and 
                                      x not in temp_filt_List)]
                filt_List = temp_filt_List

                         
        varList.delete(0, tk.END)
        for i_word in filt_List:
            varList.insert(tk.END, i_word)
            
        master.varList.see(0)     
        
        # This is to hold color for the selected x axis signal
        if master.tab_current.custom_x == 1:
            try:
                master.varList.itemconfig(varList.get(0, tk.END).index(
                        master.data_custom_x.myXAxis_name.varNames[0]
                        ),background = 'green')
            except ValueError:
                pass
            

# -------------------------------- Open a file ------------------------------
class OPEN_FILE:
    
    def __init__(self, master, fileNames):
        
        for j_file in fileNames:
            
            fileName    = j_file.rsplit('/', 2)[-1]
            
            parentDir   = j_file[0:j_file.rfind(fileName)]
            
            caseName    = j_file.rsplit('/', 2)[-2]
            
            groupName   = j_file.rsplit('/', 2)[-3]
            
            
            master.dirTree.insert('', 'end', groupName, text = groupName)
            master.dirTree.insert(groupName, 'end', text = caseName)
            
            
            if j_file.find('%') != -1:
                info_pctFile = LOAD_PERCENT(parentDir + '/' + \
                                            fileName,
                                            master)
                UPDATE_LIST(master, info_pctFile)
            else:
                tk.messagebox.showerror('Error!','Please select .% file(s)!')
                break
                return 0
            
            
# ---------------------------- Open a directory ------------------------------
class OPEN_DIR:
    
    def __init__(self, master, folderName):
        
        self.master = master
        folderName  = folderName + '/'
        self.rec_folder_read(folderName)
        
    # Recursive function to find the lowest level folder    
    def rec_folder_read(self, folder):
        if os.path.isdir(folder):
            # print('enter ' + folder)
            if not any(['.$pm' in x for x in os.listdir(folder)]):
                for in_folder in os.listdir(folder):
                    temp_folder = folder + in_folder + '/'
                    #print(temp_folder)
                    self.rec_folder_read(temp_folder)
                
            else:
                groupName = folder[0:-1].rsplit('/',1)[-2]
                caseName = folder[0:-1].rsplit('/', 1)[-1]
                if  groupName not in self.master.dirTree.get_children():
                    self.master.dirTree.insert('', 'end', groupName, text = groupName)
                self.master.dirTree.insert(groupName, 'end', text = caseName)                
                READ_FILES_IN_CASE(self.master, folder)
                
        else:
            pass
        
        

# -------------------------- Read each file in one case----------------------
class READ_FILES_IN_CASE:
    def __init__(self, master, ParentDir_caseName):
        
        fileNames   = os.listdir(ParentDir_caseName)    # all files in the directory
        
        # kick out files not with extension .% or .$
        i_file = 0
        while i_file < len(fileNames):
            if ('.%' not in fileNames[i_file]) and \
               ('.$' not in fileNames[i_file]):
                fileNames.pop(i_file)
                i_file -= 1
            i_file += 1

        
        regex_dollarFile  = re.compile(r'(.+\.\%\d+)')  # regular expression of .$ files
        master.num_filesInCase.append(int(len(fileNames)/2))
        
        for i in range(len(fileNames)):         # access each file .% + .$
            x1 = regex_dollarFile.search(fileNames[i]);
            if x1 != None:                      # if .% file
               #print(x1.group(1))
                info_pctFile = LOAD_PERCENT(ParentDir_caseName + x1.group(1), master)   
                UPDATE_LIST(master, info_pctFile)


# ------------------- Inserting elements into a target list --------------
# master, the master of the target list
# elements, a list of elements(sensor strings) to insert
class UPDATE_LIST:
    def __init__(self, master, info_pctFile):
        
        master.list_num_vars.append(info_pctFile.num_vars)
        master.list_len_vars.append(info_pctFile.len_vars)

        #   List variables
        for i_in_file in range(0,info_pctFile.num_vars):

            # if current variable exists, then skip it, otherwise add it.
            if info_pctFile.varNames_in_file[i_in_file] in master.VarNameList:
                master.list_num_vars[-1] -= 1
                
    
            else:
                master.VarNameList.append(info_pctFile.varNames_in_file[i_in_file])
                master.varList.insert(tk.END, info_pctFile.varNames_in_file[i_in_file])   
                master.percentFileList.append(info_pctFile.fileName.split('.')[-1]) 
                master.varUnitList.append(info_pctFile.varUnit[i_in_file]) 
                master.varDict[info_pctFile.varNames_in_file[i_in_file]] = info_pctFile.fileName
        
# ---------------------------------- Open .% file -----------------------
class LOAD_PERCENT:
    def __init__(self, ParentDir_caseFolder_fileName, master, *arg):
        
        self.fileName   = ParentDir_caseFolder_fileName
        myMaster        = master
        j_var           = []    # index of variable
        
        if arg:
            j_var       = arg[0]
        
        fod = open(ParentDir_caseFolder_fileName)
        fText    = fod.read()
        
        #   find data type ! FORMATR*(4/8), 4 for 32 bit, 8 for 64 bit
        regex_dtp   = re.compile(r'\bRECL\b\s+(\d+)')
        dTypeText   = regex_dtp.search(fText)
        self.dataType = dTypeText.group(1)
        
        #   TIME STEP
        regex_step  = re.compile(r'\bSTEP\b\s+(\d+\.\d+[E]?[-+]?\d{1,})')
        stepText    = regex_step.search(fText)
        #   time step need to be rounded, otherwise a time length error will occur
        #   when variable length is long
        self.timeStep = float('{:2.2e}'.format(float(stepText.group(1))))

        #   rad/s - deg/s - rpm Conversion
        regex_varUnit   = re.compile(r'\bVARUNIT\b\s+(.*)')
        varUnitText     = regex_varUnit.search(fText)
        regex_varUnit2  = re.compile(r'(\S+)')
        self.varUnit         = regex_varUnit2.findall(varUnitText.group(1))           


        #   N DIMENSIONS
        regex_NDimens   = re.compile(r'\bNDIMENS\b\s+(\d+)')
        NDimensText     = regex_NDimens.search(fText)
        self.NDimens    = float(NDimensText.group(1))
        
        
        # Regular expression of variables
        # Variables could be named in a variaty of rules, so more than one 
        # regex are needed. As far as I know, the following two cover almost all
        # cases
        
        reg_var1 = r'([\(]?\w+[-\w+]?[\)]?\s*' \
                                    '[\(]?\w*[-\w+]?[\)]?\s*' \
                                    '[\(]?\w*[-\w+]?[\)]?\s*' \
                                    '[\(]?\w*[-\w+]?[\)]?\s*' \
                                    '[\(]?\w*[-\w+]?[\)]?\s*' \
                                    '[\(]?\w*[-\w+]?[\)]?\s*' \
                                    '[\(]?\w*[-\w+]?[\)]?\s*' \
                                    '[\(]?\w*[-\w+]?[\)]?\s*' \
                                    '[\(]?\w*[-\w+]?[\)]?\s*' \
                                    '[\(]?\w*[-\w+]?[\)]?)'
        reg_var2 = r'\w+|\'\w+\s\w+\''
        
        # if there is no axial cross-section, i.e. NDIMENS = 2
        if self.NDimens == 2:
            #   find dimension of variables
            regex_dims  = re.compile(r'\bDIMENS\b\s+(\d+)\s+(\d+)')
            dim_vars    = regex_dims.search(fText)
            self.num_vars = int(dim_vars.group(1))   # number of vars
            self.len_vars = int(dim_vars.group(2))   # length of a var
    
            #   find variable names
            regex_vars  = re.compile(r'VARIAB\s(.+)')
            varText     = regex_vars.search(fText)
            
            regex2  = re.compile(reg_var1)
            self.varNames_in_file = regex2.findall(varText.group(1)) 
            
            # in case the found variables do not match the number of variables
            if len(self.varNames_in_file) != self.num_vars:
                regex2  = re.compile(reg_var2)
                self.varNames_in_file = regex2.findall(varText.group(1)) 
           
        else:
            #   find dimension of variables
            regex_dims  = re.compile(r'\bDIMENS\b\s+(\d+)\s+(\d+)\s+(\d+)')
            dim_vars    = regex_dims.search(fText)
            self.num_vars = int(dim_vars.group(1))   # number of vars
            self.num_axi  = int(dim_vars.group(2))   # number of axial cross-sections
            self.len_vars = int(dim_vars.group(3))   # length of a var
            
            #   find axial values
            regex_axival    = re.compile(r'\bAXIVAL\b\s+(.+)')
            axivalText      = regex_axival.search(fText)

            regex_axival2   = re.compile(r'(\d+\.\d+)')
            self.axival     = regex_axival2.findall(axivalText.group(1))

            #   find variable names
            regex_vars  = re.compile(r'VARIAB\s(.+)')
            varText     = regex_vars.search(fText)
                # this trick could be improved!
            regex2      = re.compile(reg_var2) 
            self.varNames_in_file = regex2.findall(varText.group(1)) 
                # remove single quotes in names 
            for i_file in range(0, self.num_vars):
                self.varNames_in_file[i_file] = self.varNames_in_file[i_file].replace('\'', '')
            
            # in case the found variables do not match the number of variables
            if len(self.varNames_in_file) != self.num_vars:
                regex2  = re.compile(reg_var1)
                self.varNames_in_file = regex2.findall(varText.group(1)) 
            
            # if there is AXIVAR, extend variables and their units
            varNames_in_file_temp = []
            varUnit_in_file_temp = []
            for i_axival in range(0, self.num_axi):
                for i_var in range(0, self.num_vars):
                    varNames_in_file_temp.append(self.varNames_in_file[i_var] + \
                                                 ' (axial = ' + \
                                                 self.axival[i_axival] + \
                                                 ')')
                    varUnit_in_file_temp.append(self.varUnit[i_var])
            self.num_vars = self.num_axi * self.num_vars
            self.varNames_in_file = varNames_in_file_temp
            self.varUnit = varUnit_in_file_temp
            
        if j_var != []: 
            self.idx_var_in_file = self.varNames_in_file.index(myMaster.VarNameList[j_var])    
        fod.close()
        
        
# ================================ End of Classes ============================
        
        
        
# -------------------------------- Main loop ---------------------------
if __name__ == '__main__':
    Main = tk.Tk()
    Main.resizable(width = True, height = True)
    HomePage(Main)
    Main.mainloop()
           
    


