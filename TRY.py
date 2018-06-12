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
import rainflow
from calDel import calDel
from DragAndDrop import DnD
from prettyNum import prettyNum
import pandas as pd
from CrePlotVar import CrePlotVar
from selection import selection_dir_var
from load_dollar import load_dollar
from load_percent import load_percent
from calc_stat import calc_stat
from keyword_filter import keyword_filter

# ============================ Home Page of App =============================
class HomePage:

    def __init__(self, master):
        
        plt.close('all')
        self.master = master
        self.master.title("SEDAP")
        self.list_tabs      = []    # Set of added tabs, a list of frames
        self.VarNameList    = []    # save loaded sensor names
        self.varDict        = {}    # dictionary for looking up .$ file corresponding to variables to plot
        
        


        # ------------------------ Menu bar------------------------------
        self.menuBar     = tk.Menu(self.master)
        self.master.config(menu = self.menuBar)
        
        # Menu bar buttons----------------------------------------------
        # File cascade
        self.fileMenu    = tk.Menu(self.menuBar, tearoff=0)  
        self.menuBar.add_cascade(label = 'File', menu = self.fileMenu)
        ## "Add file" is temporarily banned
        ## to be fixed...
<<<<<<< HEAD
        self.fileMenu.add_command(label='Add File', command = self.callback_open_file);  
        self.fileMenu.add_command(label='Add Folder', command = self.callback_open_dir)  
        self.fileMenu.add_command(label='Save', command = self.callback_save)  
=======
        self.fileMenu.add_command(label='Add File', command = self.CALLBACK_OPEN_FILE)
        self.fileMenu.add_command(label='Add Folder', command = self.CALLBACK_OPEN_DIR)  
        self.fileMenu.add_command(label='Save', command = self.CALLBACK_SAVE)  
>>>>>>> d0ccabc4620743ca03706404509f3fd84632e7e0
        self.fileMenu.add_separator()  
        self.fileMenu.add_command(label='Exit', command = self.CALLBACK_EXIT)  
        
        # About 
        self.aboutMenu   = tk.Menu(self.menuBar, tearoff = 0)
        self.menuBar.add_cascade(label = 'About', menu = self.aboutMenu)
        self.aboutMenu.add_command(label = 'About', command = self.callback_about)
        
        
        # --------------------- Main menu frames --------------------------------------
        self.frame1 = tk.Frame(self.master)
        self.frame1.grid(row = 1, column = 0, sticky = 'wesn')

        self.frame2 = tk.Frame(self.master)
        self.frame2.grid(row = 1, column = 1, rowspan = 2)   # figure frame

        self.frame3 = tk.Frame(self.master)
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
        self.dirTree.column('#0', width = 400, minwidth = 800)

   
        # Right-click popup menu ----------------------------------------
        self.popup_dirTree  = tk.Menu(self.dirTree, tearoff = 0)                
        # Hide/show lines ----------------------------------------------------
        self.popup_dirTree.add_command(label="Hide/show",
                                       command=self.CALLBACK_HIDE_SHOW_LINE)
        # Delete directory --------------------------------------------------
#        self.popup_dirTree.add_command(label="Delete",
#                                       command=self.CALLBACK_delete_tree)
        # Copy directory from clipboard ------------------------------------
        self.popup_dirTree.add_command(label="Copy from clipboard",
                                       command=self.callback_copyFromClipbd)
        
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
                                     exportselection=0)
        self.varList.grid      (row = 9, column = 0, sticky = 'NSEW')
        
        self.varScrolly       = tk.Scrollbar(self.frame1)
        self.varScrolly.grid    (row = 9, column = 0, 
                                 sticky = 'NSE')
        self.varList.config(yscrollcommand=self.varScrolly.set)
        self.varScrolly.config(command=self.varList.yview)
        
        self.varScrollx       = tk.Scrollbar(self.frame1, orient=tk.HORIZONTAL)
        self.varScrollx.grid    (row = 10, column = 0, sticky = 'WES')
        self.varList.config(xscrollcommand=self.varScrollx.set)
        self.varScrollx.config(command=self.varList.xview)
        
        # Drag and drop -------------------------------------------------
        dnd_obj = DnD(master)
        dnd_obj.bindtarget(self.dirTree, 'text/uri-list', '<Drag>', 
                           self.drag, 
                           ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
        dnd_obj.bindtarget(self.dirTree, 'text/uri-list', '<DragEnter>', 
                           self.drag_enter, 
                           ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
        dnd_obj.bindtarget(self.dirTree, 'text/uri-list', '<Drop>', 
                           self.drop, 
                           ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y','%D'))

        
        # Right-click popup menu ----------------------------------------
        self.popup_varList  = tk.Menu(self.varList, tearoff = 0)        

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
        # Hide/show lines ----------------------------------------------------
        self.popup_varList.add_command(label="Hide/show",
                                       command=self.CALLBACK_HIDE_SHOW_LINE)
        # Customized x axis
        self.popup_varList.add_command(label="Set as x-axis",
                                       command=self.CALLBACK_SET_AS_X)
        self.popup_varList.add_command(label="Unset as x-axis",
                                       command=self.CALLBACK_UNSET_AS_X)
        
        # Plot frequency domain
        self.popup_varList.add_command(label="Plot Spectrum", 
                                       background = 'cyan',
                                       command=lambda: self.callback_plot(1))
        

        # bind ---------------------------------------------------------------
        self.varList.bind("<Button-3>", self.callback_varlist_popup)        
        
        
     
        
        # Create a Filter Entry ------------------------------------------------------
        self.enterVar        = tk.StringVar()
        self.filterLabel     = tk.Label(self.frame1, text = 'Filter')
        self.filterLabel.grid  (row = 6, column = 0, sticky = 'w')
        self.filterEntry     = tk.Entry(self.frame1, textvariable = self.enterVar)
        self.filterEntry.grid  (row = 7, column = 0, sticky = 'we')
        self.enterVar.trace("w", self.callback_filter)
        
        
        # Create a button to plot time-domain signals ---------------------------------
        self.varList.bind("<Double-Button-1>", lambda _: self.callback_plot(0))    
        self.PlotTBut      = tk.Button(self.frame1, text = 'Plot Time', 
                                  command = lambda: self.callback_plot(0), bg = 'green')
        self.PlotTBut.grid   (row = 13, column = 0, sticky = 'e')
        
        # Create a button to plot frequency-domain signals ----------------------------
        self.PlotFBut     = tk.Button(self.frame1, text = 'Plot Freq', 
                                 command = lambda: self.callback_plot(1), bg = 'cyan')
        self.PlotFBut.grid  (row = 13, column = 0, sticky = 'w')
        
        # Create a button to RESET FILES --------------------------------------
        self.RESETBut     = tk.Button(self.frame1, 
                                      text = 'RESET', 
                                      command = self.callback_reset)
        self.RESETBut.grid  (row = 14, column = 0, sticky = 'w')

        # Create a button to CLEAR PLOT --------------------------------------
        self.CLEAR_PLOTBut     = tk.Button(self.frame1, 
                                           text = 'Clear Plot', 
                                           command = self.callback_clear_plot)
        self.CLEAR_PLOTBut.grid  (row = 14, column = 0, sticky = 'e')

        
        # Create a button to create new tabs
        self.tab_create_but = tk.Button(self.frame1, 
                                        text = 'new tabs', 
                                        command = self.callback_new_tab)
        self.tab_create_but.grid(row = 6, column = 0, sticky = 'ne')
        
        
        # Unit Conversion ----------------------------------------------------
        # Combobox
        self.unitCombobox    = ttk.Combobox(self.frame1)
        self.unitCombobox.grid(row = 12, column = 0, 
                               sticky = 'we')        
        self.unitCombobox['value'] = ('rad/s', 'deg/s', 'rpm')
        self.unitCombobox.set('deg/s')
        self.unitCombobox.bind("<<ComboboxSelected>>", self.CALLBACK_UNIT_CONVERSION)
       
        # Point number of FFT Entry ------------------------------------------------------
        self.NFFTLabel        = tk.Label(self.frame1, text = 'NFFT')
        self.NFFTLabel.grid     (row = 15, column = 0, sticky = 'w')
        self.NFFTEntry        = tk.Entry(self.frame1, width = 10)
        self.NFFTEntry.insert(0, '1024')
        self.NFFTEntry.grid     (row = 15, column = 0, sticky = 'e')
        self.overlapLabel        = tk.Label(self.frame1, text = 'Overlap')
        self.overlapLabel.grid     (row = 16, column = 0, sticky = 'w')
        self.overlapEntry        = tk.Entry(self.frame1, width = 10)
        self.overlapEntry.insert(0, '0.5')
        self.overlapEntry.grid     (row = 16, column = 0, sticky = 'e')
        
        ''' ------------------------- Frame 2 --------------------------- '''
        # Tabs ---------------------------------------------------------------
        self.tabMenu = ttk.Notebook(self.frame2)  # tab menu
        self.tabMenu.grid(row = 0, column = 0, sticky = 'w')
        
        # create the first tab
        self.list_tabs.append(NewTab(self))
        self.tab_current = self.list_tabs[self.tabMenu.index('current')]
#        self.data_custom_x  = CUSTOM_X(self)
        # When the current tab is changed
        self.tabMenu.bind("<<NotebookTabChanged>>", self.callback_select_tab)
        self.tabMenu.bind("<Double-Button-1>", self.callback_new_tab)
        
        
        
        
        # Right-click popup menu ----------------------------------------
        self.popup_canvas  = tk.Menu(self.tab_current.tab, tearoff = 0)                
        # axis setting  ----------------------------------------------------
        self.popup_canvas.add_command(label="Axis setting",
                                       command=self.callback_axis_set_popup)
        # show max./min.  ----------------------------------------------------
        self.popup_canvas.add_command(label="Show Max./Min.",
                                       command=self.callback_show_max_min)        
        # plot frequency domain ----------------------------------------------
        self.popup_canvas.add_command(label="Plot Spectrum",background = 'cyan',
                                       command=self.callback_local_fft) 
        
        self.tab_current.canvas.plotCanvas.get_tk_widget().bind("<Button-3>", 
                                                        self.CALLBACK_CANVAS_POPUP)

        ''' ----------------------- Frame 3 ---------------------- '''
        # Create statistics table (treeview)
        self.statList = CREATE_STAT(self.frame3)
        # Create DEL table (treeview)
        self.delTable = create_del(self.frame3)
        
        
        
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
                f = f.replace('/','\\')
                open_file(self, (f,))
            else:
                if os.path.isdir(f):
                    f = f.replace('/','\\')
                    open_dir(self, f)
                else:
                    tk.messagebox.showerror('Please select a correct file/folder!')
   
    
    
    # -------------------- Delete a directory in treeview --------------------
    # To be continued ...
#    def CALLBACK_delete_tree(self):
#        self.dirTree.delete(self.dirTree.selection())
#        
#        dirNames    = self.dirTree.get_children()
#        caseNames   = self.dirTree.get_children(dirNames)
#        dirNames    = [self.dirTree.item(i_dir)['text'] for i_dir in dirNames]
#        caseNames   = [self.dirTree.item(i_case)['text'] for i_case in caseNames]
#        self.varList.delete(0, tk.END)
#        for i_dir in dirNames:
#            for i_case in caseNames:
#                folderName = i_dir + '/' + i_case
#                open_dir(self, folderName)
        
    # --------------- local fft  -------------------
    def callback_local_fft(self):
        from local_fft import local_fft
        local_fft(self)
        
    # ----------------------- Axis setting pop-up window --------------------
    def callback_axis_set_popup(self):
        self.axis_popwin = axis_set_popup(self)    

    # ------------------------ Refresh axis settings ----------------            
    def callback_refresh_axis(self):
        combobox    = self.axis_popwin.axisCombobox
        if combobox.get() == 'All':
            """ iterate all axes """
        else:
            slt_axis = combobox.get()
            print(slt_axis)
            
                    
#        id_axis     = self.axis_popup.axisCombobox.current()
#        if not self.tab_current.Plot_obj_List == []:
#            if self.axis_popup.axisCombobox.get() != 'All':
#                self.tab_current.Plot_obj_List[id_axis].AXIS_SET()
#            else:
#                i_data_begin = 0
#                i_data_end   = len(self.tab_current.Plot_obj_List)
#                for i_data in range(i_data_begin, i_data_end):
#                    self.tab_current.Plot_obj_List[i_data].AXIS_SET()
                    
    # ----------------------- Show max/min ---------------------------------
    def callback_show_max_min(self):
        show_max_min(self.tab_current)
        
    # ----------------------- Line color ------------------------------------
    def CALLBACK_LINE_COLOR(self, color):
        LINE(self).line_color(color)    

    # ----------------------- Line style ----------------------------------
    def CALLBACK_LINE_STYLE(self, style):
        LINE(self).line_style(style)
        
    # ----------------------- Hide/show line --------------------------------
    def CALLBACK_HIDE_SHOW_LINE(self):
        LINE(self).hide_show_line()

    # ----------------------- Copy from clipboard --------------------------
    def callback_copyFromClipbd(self):
        cpydirs = self.master.clipboard_get()
        cpydirs = cpydirs.split()
        for i_cpydir in cpydirs:
            open_dir(self, i_cpydir)
     
    # ----------------------- Unit conversion ------------------------------
    def CALLBACK_UNIT_CONVERSION(self, *arg):
        print(self.unitCombobox.get())
    
    
    # ----------------------- Customized X Axis ----------------------------
    def CALLBACK_SET_AS_X(self):
        self.data_custom_x.SET_AS_X()


    def CALLBACK_UNSET_AS_X(self):
#        self.data_custom_x.UNSET_AS_X()
        pass


    # ------------ Canvas Right-click-pop-up Event ----------------
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
    def callback_varlist_popup(self, event):
        try:
            self.popup_varList.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_varList.grab_release()
            
    # ----------------------- Delete a Tab ---------------------------------
    def callback_del_tab(self, *arg):
        if len(self.tabMenu.tabs()) > 1:
            self.list_tabs.pop(self.tabMenu.index('current'))
            self.tabMenu.forget(self.tabMenu.index('current'))


    # ---------------------------- Select the Current Tab --------------------
    # This function could be abandonded in the future
    def callback_select_tab(self, *arg):
        self.tab_current = self.list_tabs[self.tabMenu.index('current')] 
        tab = self.tab_current
        if tab.plot_varobjs is not []:
            update_stat_del(tab)       
    
    # ------------------------------ Open a folder ----------------------------
    def callback_open_dir(self):
        folderName = filedialog.askdirectory(title = 'Select a directory')
        if folderName is '':
            return 
        else:
            folderName = folderName.replace('/', '\\')
            open_dir(self, folderName)

        
    # ------------------------------ Open a file -----------------------------
    def callback_open_file(self):
        fileNames = filedialog.askopenfilenames(title= "Select a file",
                                                filetypes = [('.%' , '.%*'),
                                                             ('all', '.*')])
        if fileNames is '':
            return
        else:
            open_file(self, fileNames)

            
    # ------------------------------- Save a file-----------------------
    def callback_save(self):
        save_data(self.tab_current)

    # ------------------------------- Exit -----------------------
    def CALLBACK_EXIT(self):
        plt.close('all')
        self.master.destroy()   
    
    # ------------------------ Save axis settings -------------------
    def callback_save_axis(self, *arg):
        SAVE_AXIS(self)
            
    # ------------------------ Refresh axis settings ----------------            
    def callback_about(self):
        tk.messagebox.showinfo('About', 'Author: Cai Jiasi, Tang Laiquan\n' + 
                                        'Last update: 2018/6/6\n' + 
                                        'EMail: caijs@shanghai-electric.com\n' +
                                        '       tanglq2@shanghai-electric.com')

    """ Plot function """
    def callback_plot(self, plotFFT):
        
        tab = self.tab_current
        
        if self.hold_on_var.get() == 0 and tab.custom_x == 0:
            self.callback_clear_plot()
      
        """ Selection """
        dirnames, varnames, ylabels, varlist_ids = selection_dir_var(self)
        
        for i_dir in dirnames:
            i = 0
            for i_var in varnames:
                plot_var        = CrePlotVar()
                plot_var.dir    = i_dir
                plot_var.var    = i_var
                plot_var.mytab  = tab
                plot_var.id_var = varlist_ids[i]                
                plot_var.ylabel = ylabels[i_dir][i]
                plot_var.in_file= self.varDict[i_var]
                tab.plot_varobjs.append(plot_var)
                i += 1
                
                """ Load .% files """
                percent_file_info = load_percent(plot_var.in_file, plot_var)
                
                """ Load .$ files """
                load_dollar(plot_var, percent_file_info, self)
                
                """ Calculate statistics """
                calc_stat(tab, plot_var)
                
                """ Calculate DEL """
                n = 64
                m = np.arange(3,13)
                life = 25
                t_in_year = 100
    
                if plot_var.unit in ['F','FL']:
                    
                    T = plot_var.step*(len(plot_var.data_x)-1)
                    DEL = calDel(plot_var.data_y, m, life, t_in_year, T)
                    plot_var.DEL = DEL
#                    tab.DEL.append(DEL)
                    
                    for mi in range(0,len(m)):
                        self.delTable.insert('', tk.END,
                             text = m[mi],
                             values = ('{:6.3e}'.format(plot_var.DEL[mi])))                        
                        
                """ --- plot time domain --- """
                if plotFFT == 0:
                    plot_var._plot_t()
                    """ legend and update """
                    tab.canvas.ax.legend(handles = tab.lns, 
                                           loc = 'lower left',
                                           bbox_to_anchor= (0, 1.00),
                                           ncol = 3) 
                    tab.toolbar.toolbar.update()  
                    tab.canvas.plotCanvas.draw()
                    
                """ --- plot frequency domain --- """
                """ calculation range, i.e. window size """
                xlim    = plot_var.mytab.canvas.ax.get_xlim()
                if plotFFT == 1:
                    plot_var._plot_fft(xlim)
                    tab.canvas.ax.legend(handles = tab.lns, 
                                           loc = 'lower left',
                                           bbox_to_anchor= (0, 1.00),
                                           ncol = 3) 
                    tab.toolbar.toolbar.update()  
                    tab.canvas.plotCanvas.draw()                   
        
    # ------------------------ Reset rRead Files ----------------------            
    def callback_reset(self):
        reset_read_files(self)

    # ---------------------------- Clear Plot ---------------------------            
    def callback_clear_plot(self):
        reset_plot(self.tab_current)
        
    # -------------------------- Create a new tab -------------------            
    def callback_new_tab(self):
        self.list_tabs.append(NewTab(self))
        self.tab_current = self.list_tabs[self.tabMenu.index('current')]
#        self.data_custom_x  = CUSTOM_X(self)
        # When the current tab is changed
        self.tabMenu.bind("<<NotebookTabChanged>>", self.callback_select_tab)
        self.tabMenu.bind("<Double-Button-1>", self.callback_del_tab)
        
        
        # Right-click popup menu ----------------------------------------
        self.popup_canvas  = tk.Menu(self.tab_current.tab, tearoff = 0)                
        # axis setting  ----------------------------------------------------
        self.popup_canvas.add_command(label="Axis setting",
                                       command=self.callback_axis_set_popup)
        # show max./min.  ----------------------------------------------------
        self.popup_canvas.add_command(label="Show Max./Min.",
                                       command=self.callback_show_max_min)        
        # plot frequency domain ----------------------------------------------
        self.popup_canvas.add_command(label="Plot Spectrum",background = 'cyan',
                                       command=self.callback_local_fft) 
        self.tab_current.canvas.plotCanvas.get_tk_widget().bind("<Button-3>", 
                                                        self.CALLBACK_CANVAS_POPUP)   
        
    def callback_filter(self, *arg):
        # this *arg must be added though Idk why
        keyword_filter(self)
        
    
''' =========================  Functions ===================== '''

''' save data '''
def save_data(tab):

    fn = filedialog.asksaveasfilename(title= "Save a file",
                                     defaultextension = ".txt",
                                     filetypes = [('text', '.txt')],
                                     confirmoverwrite = True)
    if fn is '':
        return
    else:
        data2save = {}
        for i_varobj in tab.plot_varobjs:
            header = 'time-' + i_varobj.ylabel
            data2save[header] = np.array(i_varobj.data_x)
            header = i_varobj.ylabel
            data2save[header] = np.array(i_varobj.data_y)
        
        df = pd.DataFrame(data = data2save, columns = list(data2save.keys()))
        df.to_csv(fn, sep = '\t', float_format = '%15.2f', index = False)

    
''' update statistics table and DEL table '''
def update_stat_del(tab):
    
    tab.callback_clear_stat()   # clear statistics list
    tab.clear_del()
    
    for i_varobj in tab.plot_varobjs:
        t_max_  = i_varobj.t_max_
        max_    = i_varobj.max_
        t_min_  = i_varobj.t_min_
        min_    = i_varobj.min_
        mean_   = i_varobj.mean_
        std_    = i_varobj.std_
        
        tab.myMaster.statList.statTree.insert('', tk.END, 
                                      text   = '{:6.3e}'.format(mean_),
                                      values = ('{:6.3e}'.format(max_),
                                                '{:6.3e}'.format(min_),
                                                '{:6.3e}'.format(std_),
                                                '{0:.2f}'.format(t_max_),
                                                '{0:.2f}'.format(t_min_)))
        try:
            m = np.arange(3,13)
            for mi in range(0,len(m)):
                tab.myMaster.delTable.insert('', tk.END,
                                 text = m[mi],
                                 values = ('{:6.3e}'.format(i_varobj.DEL[mi])))
        except AttributeError:
            pass
        
''' create DEL table (treeview) '''
def create_del(frame):
    
    del_table = ttk.Treeview(frame, height = 4,
                             columns = ('1'))
    del_table.grid(row = 0, column = 5)
    del_scrolly = ttk.Scrollbar(frame, orient = 'vertical',
                                command = del_table.yview)
    del_scrolly.grid(row = 0, column = 6, sticky = 'ns')
    del_table.configure(yscroll = del_scrolly.set)
    
    del_table.heading('#0',     text = 'm')
    del_table.heading(1,        text = 'DEL')
    del_table.column('#0', width = 50, anchor = 'w')
    del_table.column(1   , width = 100, anchor = 'w')
    
    return del_table



''' ------------------------ Calculate max/min values ------------------- '''
def cal_max_min(data_x, data_y):

    max_    = data_y.max()
    min_    = data_y.min()
    
    ind_max = data_y.tolist().index(max_)
    ind_min = data_y.tolist().index(min_)
    

    x_max, y_max, x_min, y_min  =   data_x[ind_max], \
                                    data_y[ind_max], \
                                    data_x[ind_min], \
                                    data_y[ind_min]
    
    return x_max, y_max, x_min, y_min
        
''' ------------------------ Show/hide max/min values -------------------- '''
def show_max_min(tab):
    
    # if partly shown and hidden, all lines are shown firstly.
    sum_logic = sum(i_plot.max_.get_visible() for i_plot in tab.Plot_obj_List)
    
    
    if  sum_logic < len(tab.Plot_obj_List) and sum_logic > 0:
        for i_plot in tab.Plot_obj_List:
            i_plot.max_.set_visible(1)
            i_plot.min_.set_visible(1)
            i_plot._max_vline.set_visible(1)
            i_plot._min_vline.set_visible(1)

    else:
        for i_plot in tab.Plot_obj_List:
            i_plot.max_.set_visible(not i_plot.max_.get_visible())
            i_plot.min_.set_visible(not i_plot.min_.get_visible())
            i_plot._max_vline.set_visible(not i_plot._max_vline.get_visible())
            i_plot._min_vline.set_visible(not i_plot._min_vline.get_visible())
        
    tab.canvas.plotCanvas.draw()
        


""" Axis-setting pop-up window"""
def axis_set_popup(mainpage):
    pop_win = tk.Toplevel()
    pop_win.title('Axis setting')

    """ Axis settings """
    """ Combobox """
    axisRefreshBut  = tk.Button(pop_win, text = 'Refresh', 
                                     command = mainpage.callback_refresh_axis)
    axisRefreshBut.grid(row = 1, column = 5, 
                             rowspan = 2, sticky = 'wens')
    axisCombobox    = ttk.Combobox(pop_win)
    axisCombobox.grid(row = 0, column = 0, 
                           columnspan = 4, sticky = 'we')  
    """ Axis ranges frame """
    yMax       = tk.StringVar()
    yMin       = tk.StringVar()
    xMax       = tk.StringVar()
    xMin       = tk.StringVar()
    """ y-axis max """
    yMaxLabel     = tk.Label(pop_win, text = 'y-axis max', width = 10)
    yMaxLabel.grid  (row = 1, column = 2, sticky = 'nw')
    yMaxEntry     = tk.Entry(pop_win, width = 10, textvariable = yMax)
    yMaxEntry.grid  (row = 1, column = 1, sticky = 'nw')
    """ y-axis min """
    yMinLabel     = tk.Label(pop_win, text = 'y-axis min', width = 10)
    yMinLabel.grid  (row = 2, column = 2, sticky = 'nw')
    yMinEntry     = tk.Entry(pop_win, width = 10, textvariable = yMin)
    yMinEntry.grid  (row = 2, column = 1, sticky = 'nw')
    """ x-axis max """
    xMaxLabel     = tk.Label(pop_win, text = 'x-axis max', width = 10)
    xMaxLabel.grid  (row = 1, column = 4, sticky = 'nw')
    xMaxEntry     = tk.Entry(pop_win, width = 10, textvariable = xMax)
    xMaxEntry.grid  (row = 1, column = 3, sticky = 'nw')
    """ x-axis min """
    xMinLabel     = tk.Label(pop_win, text = 'x-axis min', width = 10)
    xMinLabel.grid  (row = 2, column = 4, sticky = 'nw')
    xMinEntry     = tk.Entry(pop_win, width = 10, textvariable = xMin)
    xMinEntry.grid  (row = 2, column = 3, sticky = 'nw')
    yMax.trace('w', mainpage.callback_save_axis)
    yMin.trace('w', mainpage.callback_save_axis)
    xMax.trace('w', mainpage.callback_save_axis)
    xMin.trace('w', mainpage.callback_save_axis)
    
    """ Combobox values """
    sensor_names = []
    for i_varobj in mainpage.tab_current.plot_varobjs:
        sensor_names.append(i_varobj.var)
    sensor_names.append('All')
    axisCombobox['value'] = sensor_names
    
    
    return pop_win

    
    
## ------------------------- Axis setting pop-up window ----------------------
#class axis_set_popup:
#    def __init__(self, main):
#        self.master = main
#        self.axis_set_popup = tk.Toplevel()
#        self.axis_set_popup.title('Axis setting')
#        
#        self.axis_set()
#
#        
#    def axis_set(self):
#        # Axis settings -------------------------------------------------------------     
#        # Combobox
#        self.axisRefreshBut  = tk.Button(self.axis_set_popup, text = 'Refresh', 
#                                         command = self.master.callback_refresh_axis)
#        self.axisRefreshBut.grid(row = 1, column = 5, 
#                                 rowspan = 2, sticky = 'wens')
#        self.axisCombobox    = ttk.Combobox(self.axis_set_popup)
#        self.axisCombobox.grid(row = 0, column = 0, 
#                               columnspan = 4, sticky = 'we')  
#        # Axis ranges frame --------------------------------------------------
#        self.yMax       = tk.StringVar()
#        self.yMin       = tk.StringVar()
#        self.xMax       = tk.StringVar()
#        self.xMin       = tk.StringVar()
#        # y-axis max
#        self.yMaxLabel     = tk.Label(self.axis_set_popup, text = 'y-axis max', width = 10)
#        self.yMaxLabel.grid  (row = 1, column = 2, sticky = 'nw')
#        self.yMaxEntry     = tk.Entry(self.axis_set_popup, width = 10, textvariable = self.yMax)
#        self.yMaxEntry.grid  (row = 1, column = 1, sticky = 'nw')
#        # y-axis min
#        self.yMinLabel     = tk.Label(self.axis_set_popup, text = 'y-axis min', width = 10)
#        self.yMinLabel.grid  (row = 2, column = 2, sticky = 'nw')
#        self.yMinEntry     = tk.Entry(self.axis_set_popup, width = 10, textvariable = self.yMin)
#        self.yMinEntry.grid  (row = 2, column = 1, sticky = 'nw')
#        # x-axis max
#        self.xMaxLabel     = tk.Label(self.axis_set_popup, text = 'x-axis max', width = 10)
#        self.xMaxLabel.grid  (row = 1, column = 4, sticky = 'nw')
#        self.xMaxEntry     = tk.Entry(self.axis_set_popup, width = 10, textvariable = self.xMax)
#        self.xMaxEntry.grid  (row = 1, column = 3, sticky = 'nw')
#        # x-axis min
#        self.xMinLabel     = tk.Label(self.axis_set_popup, text = 'x-axis min', width = 10)
#        self.xMinLabel.grid  (row = 2, column = 4, sticky = 'nw')
#        self.xMinEntry     = tk.Entry(self.axis_set_popup, width = 10, textvariable = self.xMin)
#        self.xMinEntry.grid  (row = 2, column = 3, sticky = 'nw')
#        self.yMax.trace('w', self.master.CALLBACK_SAVE_AXIS)
#        self.yMin.trace('w', self.master.CALLBACK_SAVE_AXIS)
#        self.xMax.trace('w', self.master.CALLBACK_SAVE_AXIS)
#        self.xMin.trace('w', self.master.CALLBACK_SAVE_AXIS)
#        
#        # Combobox values
#        self.axisCombobox['value'] = self.master.tab_current.names_sensor 
        


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
#        select      = SELECTION(self.master)
#        theLineDir  = []
#        id_lines    = []
#        # save selected lines' directories (i.e. labels)
#        for i_dir in select.dirNames:
#            for i_var in select.varNames:
#                dirvar = i_dir  + '\\' + i_var
#                dirvar = dirvar.split('\\')[-3] + ' ' + \
#                         dirvar.split('\\')[-2] + \
#                         dirvar.split('\\')[-1]
#                theLineDir.append (dirvar)
#        
#        # find the corresponding indices
#        for line in theLineDir:
#            id_lines += [i for i, v in 
#                     enumerate(self.master.tab_current.YLabels) if v == line]
#
#        return id_lines
        pass


## ----------------------------- Customized X axis ---------------------------
#class CUSTOM_X:
#    def __init__(self, master):
#        
#        self.master = master
#        self.master.tab_current.custom_x = 0
#        
#    def SET_AS_X(self):
#        if self.master.tab_current.custom_x == 1:
#            self.master.data_custom_x.UNSET_AS_X()
#        
#        if self.master.dirTree.selection() != ():
#            self.myXAxis_name    = SELECTION(self.master)
#            
#        try:
#            self.myXAxis_name
#            self.master.varList.itemconfig(self.master.varList.curselection(), 
#                                           background = 'green')
#            self.xAxis_data      = LOAD_DOLLAR(self.master, self.myXAxis_name)
#            print('Customized x axis: ' + self.myXAxis_name.varNames[0])
#            
#            self.master.tab_current.custom_x = 1
#        except AttributeError:
#            tk.messagebox.showerror('','Select a directory!')
#            pass
#        
#    def UNSET_AS_X(self):
#        try:
#            self.master.varList.itemconfig(self.master.data_custom_x.myXAxis_name.sltId_vars, 
#                                           background = 'white')
#            self.master.data_custom_x = CUSTOM_X(self.master)
#            
#        except AttributeError:
#            pass
#        print('X axis: Time')

""" Clear the plot in the current tab """
def reset_plot(tab):    
    tab.plotted_vars   = {}     # sensors that have been plotted, no duplicates
    tab.plot_varobjs   = []     # save plotted sensor objects
    tab.lns            = []
    tab.secYPos        = 1      # secondary y axes postion
    tab.callback_clear_stat()   # clear statistics list
    tab.clear_del()             # clear DEL list
    del tab.canvas              # re-create canvas
    tab.canvas  = tab.callback_create_canvas()
    del tab.toolbar             # re-create toolbar
    tab.toolbar = tab.callback_create_toolbar()  
    
    tab.canvas.plotCanvas.get_tk_widget().bind("<Button-3>", 
                                    tab.myMaster.CALLBACK_CANVAS_POPUP) 
    tab.canvas.ax.legend(handles = tab.lns, 
                                   loc = 'lower left',
                                   bbox_to_anchor= (0, 1.00),
                                   ncol = 3)
    
""" Clear the loaded data including plot """ 
def reset_read_files(mainpage):
    
    for i_tab in mainpage.tabMenu.tabs():
        tab_id = mainpage.tabMenu.index(i_tab)
        if tab_id == 0:
            reset_plot(mainpage.tab_current)
        else:
            mainpage.tabMenu.forget(tab_id)
    
#    reset_plot(mainpage.tab_current)
    
    for i in mainpage.dirTree.get_children(): # clear lists of directories and sensors
        mainpage.dirTree.delete(i)
    mainpage.varList.delete(0,tk.END)
    mainpage.VarNameList        = []    # save loaded sensor names
      
        
# ----------------------------- Axis Selection ------------------------------     
class SAVE_AXIS:
    
    def __init__(self, myMaster):
        self.master     = myMaster
        self.id_axis    = myMaster.axis_popup.axisCombobox.current()
        self.name_axis  = myMaster.axis_popup.axisCombobox.get()
#        self.select     = SELECTION(myMaster)
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
    

<<<<<<< HEAD
=======

# ----------------------- Calculate FFT ----------------------------
def calc_fft(data, i_data, NFFT, ovlp):
    
    #   default 1024
    if NFFT == '' or int(NFFT) == 0:
        NFFT = len(data.data_y[i_data])
        
    if int(NFFT) > len(data.data_y[i_data]):
        tk.messagebox.showerror('Error','NFFT is larger than data length!')
        
    else:
        NFFT = int(NFFT)
        win_len = NFFT
        win_overlap = float(ovlp)
        win_hann = np.hanning(win_len)
        y = data.data_y[i_data]
        x = data.data_x[i_data]
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
        
        fs = 1/data.step[i_data]
        f  = fs*np.arange(0,(NFFT/2))/NFFT;        
        
        #   scale power density
        Sw2 = sum(win_hann**2)
        Pxx_den = 2*Pxx_den/fs/Sw2
        
        #   compensation 
        Pxx_den *= 1.6

        return f, Pxx_den


# ----------------------- Calculate statistic data -----------------
class CALC_STAT:
    
    def __init__(self, tab, data):
        for i_data in range(0, len(data.data_y)):
            if data.data_x[i_data] != [] and data.data_y[i_data] != []:
                
                _mean   = data.data_y[i_data].mean()
                _max    = data.data_y[i_data].max()
                _min    = data.data_y[i_data].min()
                _std    = data.data_y[i_data].std()
                
                ind_max = data.data_y[i_data].tolist().index(_max)
                ind_min = data.data_y[i_data].tolist().index(_min)
                
                _t_max   = data.data_x[i_data][ind_max]
                _t_min   = data.data_x[i_data][ind_min]
                
                tab.myMaster.statList.statTree.insert('', tk.END, 
                                             text = '{:6.3e}'.format(_mean),
                                             values = ('{:6.3e}'.format(_max),
                                                       '{:6.3e}'.format(_min),
                                                       '{:6.3e}'.format(_std),
                                                       '{0:.2f}'.format(_t_max),
                                                       '{0:.2f}'.format(_t_min)))
                
                tab.stat_val.append([_t_max, _max,
                                     _t_min, _min,
                                     _mean,
                                     _std])
    
# -------------------------- Load .$ file ----------------------------------
class LOAD_DOLLAR:
    def __init__(self, myMaster, select):
        self.data_y = []
        self.data_x = []
        self.step   = []
        self.ylabel = select.yLabel
        self.unit   = []
        
        for j_dirName in  select.dirNames:
            for j_var in range(0, len(select.sltId_vars)):
                filePrefix = [x for x in os.listdir(j_dirName) if '.$pj' in x.lower()][0].rsplit('.', 1)[-2]
                fileDir =   j_dirName +  '\\' + \
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
                    fodID = open(fileDir, 'rb')
                    if dataInfo_obj.dataType == '4':
                        readMethod = np.float32
                    else:
                        readMethod = np.float64
                        
                    data = np.fromfile(fodID, readMethod)
                    y = data[list(range(dataInfo_obj.idx_var_in_file,\
                                        dataInfo_obj.num_vars*dataInfo_obj.len_vars,\
                                        dataInfo_obj.num_vars))]
                    self.data_y.append(y)
                    x = np.arange(0, 
                                  dataInfo_obj.timeStep* dataInfo_obj.len_vars, 
                                  dataInfo_obj.timeStep)
                    self.data_x.append(x)
                    
                    fodID.close();
                    
                    unit = myMaster.varUnitList[select.sltId_vars[j_var]]
                    self.unit.append(unit)
                    
                    # if convert unit?
                    if unit in ['A','A/T', 'A/TT']:
                        unit_get = myMaster.unitCombobox.get()
                        if unit_get in ['deg', 'deg/s', 'deg/s2']:
                            self.data_y[-1] = self.data_y[-1] * 180/np.pi
                        if unit_get in ['rpm']:
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
        if self.sltId_wholeDir == ():
            tk.messagebox.showerror('','Please select a directory.')
            return 0
        else:
            self.dirNames   = []
            for id_dirName in self.sltId_wholeDir:
                self.dirNames.append(
                myMaster.dirTree.parent(id_dirName) + '\\' + \
                myMaster.dirTree.item(id_dirName)['text']
                );  
            
        # select vars in the listbox and get the file names
        sltId_vars  = myMaster.varList.curselection()
        self.varNames    = [myMaster.varList.get(i) for i in sltId_vars]

        ''' Re-mapping 
        The index(or indices) of the selected variable(s) in the filtered list 
        is not the "real" index(or indices) of that in the total variable list,  
        so it has to be re-mapped.
        '''
        id_vars     = []
        for i_var in range(0, len(self.varNames)):
            id_vars.append(myMaster.VarNameList.index(self.varNames[i_var])) 
                
        self.sltId_vars  = tuple(id_vars)

        # Variable Unit
        self.varUnit    = [myMaster.varUnitList[i] for i in self.sltId_vars]
       
        # y labels
        self.yLabel = []   
        self.CREATE_YLABEL(myMaster)
        
        
        # hold-on checkbox
        self.hold_on_var = myMaster.hold_on_var.get()
        
        
    # Create labels
    def CREATE_YLABEL(self, myMaster):
        for i_dirName in self.dirNames:
            for i_var in range(0, len(self.sltId_vars)):
                ylab = i_dirName +'\\'+ \
                        myMaster.VarNameList[self.sltId_vars[i_var]]
                ylab = ylab.split('\\')[-3] + ' ' + \
                       ylab.split('\\')[-2] + \
                       ylab.split('\\')[-1]
                self.yLabel.append(ylab)
            
    


>>>>>>> d0ccabc4620743ca03706404509f3fd84632e7e0
# ----------------------------- Create new lists for statistics -------------
class CREATE_STAT():
    def __init__(self, myMaster):
        # Show statistics ------------------------------------------------------
        self.frame_stat = myMaster
        self.create_stat()
        
    def create_stat(self):
        self.statTree = ttk.Treeview(self.frame_stat, height = 4,
                                     columns = ('1', '2', '3', '4', '5'))
        self.statTree.grid(row = 0, column = 3)
        self.statScrolly = ttk.Scrollbar(self.frame_stat, orient='vertical', 
                                        command=self.statTree.yview)
        self.statScrolly.grid(row = 0, column = 4, sticky = 'ns')
        self.statTree.configure(yscroll=self.statScrolly.set)
        
        self.statTree.heading('#0', text = 'Mean')
        self.statTree.heading(1,    text = 'Max')
        self.statTree.heading(2,    text = 'Min')
        self.statTree.heading(3,    text = 'Std')
        self.statTree.heading(4,    text = 't for Max')
        self.statTree.heading(5,    text = 't for Min')
        self.statTree.column('#0', width = 100,  anchor='w')
        self.statTree.column(1,    width = 100,  anchor='w')
        self.statTree.column(2,    width = 100,  anchor='w')
        self.statTree.column(3,    width = 100,  anchor='w')
        self.statTree.column(4,    width = 100)
        self.statTree.column(5,    width = 100)
        
    
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
<<<<<<< HEAD
#        page = myMaster.myMaster.master
#        width = (page.winfo_screenmmwidth() - 40) /25.4
#        height = (page.winfo_screenmmheight() - 60) /25.4 *0.9
#        self.hostFig, self.ax = plt.subplots(figsize = (width, height))
        self.hostFig, self.ax = plt.subplots(figsize = (19, 8), dpi = 60)
=======
        page = myMaster.myMaster.master
        width = (page.winfo_screenmmwidth() - 40) / 25.4
        height = (page.winfo_screenmmheight() - 40) / 25.4 * 0.8
        print(page.winfo_screenmmwidth(), page.winfo_screenmmheight())
        self.hostFig, self.ax = plt.subplots(figsize = (width, height))
        # self.hostFig, self.ax = plt.subplots(figsize = (19, 8), dpi = 60)
>>>>>>> d0ccabc4620743ca03706404509f3fd84632e7e0
        self.hostFig.subplots_adjust(left = 0.08, right = 0.82)
        self.plotCanvas = FigureCanvasTkAgg(self.hostFig, master = myMaster.tab)
        
        self.plotCanvas.get_tk_widget().grid(row = 0, column = 0, 
                                columnspan = 2, sticky = 'WEN')  
        self.ax.legend(handles  = myMaster.lns, 
                                   loc = 'lower left',
                                   bbox_to_anchor= (0, 1.00),
                                   ncol = 3)
        

# ----------------------------- Create a New Tab -----------------------------
class NewTab():
    # main = Main
    def __init__(self, main):
        
        self.myMaster       = main
        self.plotted_vars   = {}        # sensors that have been plotted, no duplicates
        self.lns            = []        # figure handles used to plot legends
        self.secYPos        = 1         # secondary y axes postion
#        self.setX           = 0         # a flag, 0 for time x axis,
                                        #         1 for customized x axis
        self.custom_x       = 0         # 0 for no customized x axis is selected,
                                        # 1 for one sensor is selected
        self.plot_varobjs   = []        # save plotted sensor objects

        
        # hopefully the maximum number of tabs should not be over 10
        self.tab = tk.Frame(self.myMaster.tabMenu)
        self.tab.bind("<Double-Button-1>", self.myMaster.callback_del_tab)
        tabNums = len(self.myMaster.tabMenu.tabs())
        self.myMaster.tabMenu.add(self.tab, text= 'Tab ' + str(tabNums+1))
        
        # Create a new canvas -------------------------------------
        self.canvas = self.callback_create_canvas()
        self.myMaster.tabMenu.select(self.tab) # Select the created tab, just for convenience
        
        # Create a new navigation toolbar -------------------------
        self.toolbar = self.callback_create_toolbar()
    
    def callback_create_stat(self):
        return CREATE_STAT(self.myMaster.frame3)
    
    def callback_create_toolbar(self):
        return CREATE_TOOLBAR(self.tab, self.canvas)
        
    def callback_create_canvas(self):
        return CREATE_CANVAS(self)
                
    def callback_clear_stat(self):
        for item in self.myMaster.statList.statTree.get_children():
            self.myMaster.statList.statTree.delete(item)
            
    def clear_del(self):
        for item in self.myMaster.delTable.get_children():
            self.myMaster.delTable.delete(item)
        
    
    def UPDATE_PLOTTEDVARS(self, select):
        # add new plotted sensors
        for i in range(0, len(select.varNames)):
            if select.varNames not in self.names_sensor:
                self.names_sensor.insert(-1, select.varNames[i])

    def CLEAR_PLOTTEDVARS(self):
#        self.myMaster.axisCombobox['value'] = ()
#        self.myMaster.axisCombobox.set('')
        pass
        
    def new_next_tab(self):
        self.tab = tk.Frame(self.myMaster.tabMenu)   
        self.myMaster.tabMenu.add(self.tab, text = '*')
        
        

# -------------------------------- Open a file ------------------------------
class open_file:
    
    def __init__(self, master, fileNames):
        
        for j_file in fileNames:
            
            j_file      = j_file.replace('/', '\\')
            
            fileName    = j_file.rsplit('\\', 2)[-1]
            
            parentDir   = j_file[0:j_file.rfind(fileName)]
            
            caseName    = j_file.rsplit('\\', 2)[-2]
            
            groupName   = j_file.rsplit('\\', 2)[-3]
            
            
            master.dirTree.insert('', 'end', groupName, text = groupName)
            master.dirTree.insert(groupName, 'end', text = caseName)
            
            if j_file.find('%') != -1:
                info_pctFile = load_percent(parentDir + '\\' + \
                                            fileName)
                update_varlist(master, info_pctFile)
            else:
                tk.messagebox.showerror('Error!','Please select .% file(s)!')
                break
                return 0
            
            
# ---------------------------- Open a directory ------------------------------
class open_dir:
    
    def __init__(self, master, folderName):
        
        self.master = master
        folderName  = folderName + '\\'
        self.rec_folder_read(folderName)
        
    # Recursive function to find the lowest level folder    
    def rec_folder_read(self, folder):
        if os.path.isdir(folder):
            if not any(['.$pj' in x.lower() for x in os.listdir(folder)]) :
                for in_folder in os.listdir(folder):
                    temp_folder = folder + in_folder + '\\'
                    self.rec_folder_read(temp_folder)
                
            else:
                groupName = folder[0:-1].rsplit('\\',1)[-2]
                caseName = folder[0:-1].rsplit('\\', 1)[-1]
                if  groupName not in self.master.dirTree.get_children():
                    self.master.dirTree.insert('', 'end', groupName, text = groupName)
                self.master.dirTree.insert(groupName, 'end', text = caseName)                
                read_files_in_folder(self.master, folder)           
        else:   
            pass
        
        

""" Read each file in one case """
def read_files_in_folder(mainpage, folder):
        
<<<<<<< HEAD
    fileNames   = os.listdir(folder)    # all files in the directory
    
    """ kick out files not with extension .% or .$ """
    i_file = 0
    while i_file < len(fileNames):
        if ('.%' not in fileNames[i_file]) and \
           ('.$' not in fileNames[i_file]):
            fileNames.pop(i_file)
            i_file -= 1
        i_file += 1
    
    """ access each file .% and .$ """
    regex_dollarFile  = re.compile(r'(.+\.\%\d+)')  # regular expression of .$ files
    for i_file in fileNames: 
        x1 = regex_dollarFile.search(i_file);
        if x1 != None:                      # if .% file
            info_pctFile = load_percent(folder + x1.group(1))   
            update_varlist(mainpage, info_pctFile)
=======
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
            x1 = regex_dollarFile.search(fileNames[i])
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
>>>>>>> d0ccabc4620743ca03706404509f3fd84632e7e0

                
""" Update variable list """
def update_varlist(master, pct_info):
    
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
    
    #   List variables
    for i_var in vars_in_file:
        """ if current variable exists, then skip it, otherwise add it. """
        if i_var not in master.VarNameList:
            master.VarNameList.append(i_var)
            master.varList.insert(tk.END, i_var)   
            master.varDict[i_var] = filename
        
""" ====================== End of Functions ======================= """
        
        
        
# -------------------------------- Main loop ---------------------------
if __name__ == '__main__':
    root = tk.Tk()
    root.wm_state('zoomed')
    HomePage(root)
    root.mainloop()

           
    


