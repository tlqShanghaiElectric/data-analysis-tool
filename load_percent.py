# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 13:55:36 2018

@author: 12600632
"""

import re 

# ---------------------------------- Open .% file -----------------------
def load_percent(filename, *arg):
    
    varobj = []
    if arg:
        varobj = arg[0]

    fod = open(filename)
    fText    = fod.read()
    
    
    #   find data type ! FORMATR*(4/8), 4 for 32 bit, 8 for 64 bit
    regex_dtp   = re.compile(r'\bRECL\b\s+(\d+)')
    dTypeText   = regex_dtp.search(fText)
    datatype = dTypeText.group(1)
    
    #   TIME STEP
    regex_step  = re.compile(r'\bSTEP\b\s+(\d+\.\d+[E]?[-+]?\d{1,})')
    stepText    = regex_step.search(fText)
    #   time step need to be rounded, otherwise a time length error will occur
    #   when variable length is long
    timestep = float('{:2.2f}'.format(float(stepText.group(1))))

    #   rad/s - deg/s - rpm Conversion
    regex_varUnit   = re.compile(r'\bVARUNIT\b\s+(.*)')
    varUnitText     = regex_varUnit.search(fText)
    regex_varUnit2  = re.compile(r'(\S+)')
    varunit         = regex_varUnit2.findall(varUnitText.group(1))           


    #   N DIMENSIONS
    regex_NDimens   = re.compile(r'\bNDIMENS\b\s+(\d+)')
    NDimensText     = regex_NDimens.search(fText)
    NDimens    = float(NDimensText.group(1))
    
    
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
    if NDimens == 2:
        #   find dimension of variables
        regex_dims  = re.compile(r'\bDIMENS\b\s+(\d+)\s+(\d+)')
        dim_vars    = regex_dims.search(fText)
        num_vars = int(dim_vars.group(1))   # number of vars
        len_vars = int(dim_vars.group(2))   # length of a var

        #   find variable names
        regex_vars  = re.compile(r'VARIAB\s(.+)')
        varText     = regex_vars.search(fText)
        
        regex2  = re.compile(reg_var1)
        vars_in_file = regex2.findall(varText.group(1)) 
        
        # in case the found variables do not match the number of variables
        if len(vars_in_file) != num_vars:
            regex2  = re.compile(reg_var2)
            vars_in_file = regex2.findall(varText.group(1)) 
       
    else:
        #   find dimension of variables
        regex_dims  = re.compile(r'\bDIMENS\b\s+(\d+)\s+(\d+)\s+(\d+)')
        dim_vars    = regex_dims.search(fText)
        num_vars = int(dim_vars.group(1))   # number of vars
        num_axi  = int(dim_vars.group(2))   # number of axial cross-sections
        len_vars = int(dim_vars.group(3))   # length of a var
        
        #   find axial values
        regex_axival    = re.compile(r'\bAXIVAL\b\s+(.+)')
        axivalText      = regex_axival.search(fText)

        regex_axival2   = re.compile(r'(\d+\.\d+)')
        axival     = regex_axival2.findall(axivalText.group(1))

        #   find variable names
        regex_vars  = re.compile(r'VARIAB\s(.+)')
        varText     = regex_vars.search(fText)
            # this trick could be improved!
        regex2      = re.compile(reg_var2) 
        vars_in_file = regex2.findall(varText.group(1)) 
            # remove single quotes in names 
        for i_file in range(0, num_vars):
            vars_in_file[i_file] = vars_in_file[i_file].replace('\'', '')
        
        # in case the found variables do not match the number of variables
        if len(vars_in_file) != num_vars:
            regex2  = re.compile(reg_var1)
            vars_in_file = regex2.findall(varText.group(1)) 
        
        # if there is AXIVAR, extend variables and their units
        varNames_in_file_temp = []
        varUnit_in_file_temp = []
        for i_axival in range(0, num_axi):
            for i_var in range(0, num_vars):
                varNames_in_file_temp.append(vars_in_file[i_var] + \
                                             ' (axial = ' + \
                                             axival[i_axival] + \
                                             ')')
                varUnit_in_file_temp.append(varunit[i_var])
        num_vars = num_axi * num_vars
        vars_in_file = varNames_in_file_temp
        varunit = varUnit_in_file_temp
    fod.close()        
    
    if varobj != []:
        id_var_in_file = vars_in_file.index(varobj.var)    
        return (filename, id_var_in_file, vars_in_file, 
                num_vars, len_vars, datatype, varunit, timestep)
    else:
        return (filename, vars_in_file, 
                num_vars, len_vars, datatype, varunit, timestep)
        