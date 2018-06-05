# -*- coding: utf-8 -*-
"""
Created on Fri May 25 13:46:36 2018

@author: 12600632
"""


import numpy as np
'''
  ---------------- Rainflow Counting Algorithm --------------------

 Input: 
 1. x, load history, time series data

 Output:
 1. del, damage equivalent load, DEL
 
'''

def dat2tp(x):
    '''
    get peaks and troughs, i.e. local maxima and minima
    
    tp, an array including local maxima and minima
    ind, index of tps in the original x
    
    '''
    diffx   = (x[1:-1]-x[0:-2]) * (x[1:-1]-x[2:])
    ind     = np.where(diffx > 0)[0] + 1
    ind     = np.insert(ind, 0, 0)
    ind     = np.append(ind, len(x)-1)
    tp      = x[ind]
    return tp, ind

def rearrangeTS(x):
    '''
    rearrange tps to begin and end with the maximum peak
    '''
    ind_max = np.where(x == max(x))[0][0]
    x = np.append(x, x[0:ind_max])
    x = np.delete(x, np.arange(0, ind_max))
    
    return x
    

def tp2rfc4p(tp):
    ''' 
    count whole cycle using 4-point method
    
    tp, an array including turning poits
    N, number of whole cycles
    
    Sw, Sh, load range of whole cycles and half cycles
    
    Nw, Nh, number of whole cycles and half cycles
    
    length of tp is rounded to be even
    '''
    
    i = 0
    L = len(tp)    
    Nw = 0
    _tp = tp
    Sw = []
#    Sh = []
    
    ''' 4-pt method '''
    while i < L-3:
        x1, x2, x3, x4 = _tp[i], _tp[i+1], _tp[i+2], _tp[i+3]
        a = abs(x2 - x1)
        b = abs(x3 - x2)
        c = abs(x4 - x3)
        if b <= a and b < c:
            Nw += 1
            Sw.append(b)
            _tp = np.delete(_tp, [i+1, i+2])
            L = len(_tp)
            i = 0
        else:
            i += 1
    
    res = _tp
    
    return np.array(Sw), res



def tp2rfcSimple(tp):
    ''' 
    count whole cycle using simple rfc method
    
    tp, an array including turning poits
    N, number of whole cycles
    
    Sw, Sh, load range of whole cycles and half cycles
    
    Nw, Nh, number of whole cycles and half cycles
    
    length of tp is rounded to be even
    '''
    
    i = 0
    L = len(tp)    
    Nw = 0
    _tp = tp
    Sw = []

    '''   Simple RF counting '''
    while i < L-2:
        x1, x2, x3 = _tp[i], _tp[i+1], _tp[i+2]
        a = abs(x2 - x1)
        b = abs(x3 - x2)
        if b >= a:
            Nw += 1
            Sw.append(a)
            _tp = np.delete(_tp, [i, i+1])
            L = len(_tp)
            i = 0
        else:
            i += 1
    
    res = _tp

    return np.array(Sw), res




def res2rfc(res):
    ''' half cycle using residue ? '''

#    if np.mod(len(res), 2) != 0:
#        res = np.delete(res, -1)
#    
#    Sh = abs(res[np.arange(0,len(res),2)] - res[np.arange(1,len(res),2)])
    
    Sh = np.array([])
    i = 0 
    while i < len(res)-1:
        Shrange = abs(res[i] - res[i+1])
        Sh = np.append(Sh, Shrange)
        i += 1
    
    return Sh



def calc_del(*arg):
    ''' calculate DEL 
        input: 
            S, load range
            T, the duration of the original time history
            f, frequency for equivalent loads
            n, number of bins
            m, inverse S-N slope; 10 numbers in Bladed, i.e. 3 - 12, 
                especilally interested in m = 4, 10 
                
        n_in_bin, number of cycles in load range
        bin_edges, edges of bins
                
        ni*Si = countings in each bin * the upper limit of each bin
        
        DEL = (sum(ni*Si^m/T/f))^(1/m)
    '''


    S, T, f, n, m = arg[0], arg[1], arg[2], arg[3], arg[4]
    
    DEL = []
    Sw = S[0]/1000
    Sh = S[1]/1000
    
    Swh = np.append(Sw, Sh)
    edges = np.linspace(min(Swh), max(Swh), n+1)
    n_in_bin, bin_edges = np.histogram(Sw, bins = edges) 
    n_in_bin = np.array([float(i) for i in n_in_bin])
    
    for Sh_i in Sh:
        i = 0
        while i <= n:
            if bin_edges[i] < Sh_i and Sh_i < bin_edges[i+1]:
                n_in_bin[i] += 0.5
                i = n+1
            else:
                i += 1

 
    for mi in m:
        del_i = (sum(n_in_bin * bin_edges[1:]**mi) / 600 / f) ** (1/mi)
        DEL.append(del_i)
    
    
    return DEL
    

def scale_hours(t_in_year):
    ''' scale total calculation hours to the standard 8766 hours '''
#    if t_in_year < 8766:
#        dt = 8766 - t_in_year
#    else:
#        dt = t_in_year - 8766
        
    # if only one single load case, just return 8766
    return 8766



def cal_del(x, n, m, T, t, method):
    ''' main program call this function
    x, time series load history
    n, number of bins
    m, inverse S-N slope
    T, design life of wind turbine, eg. 20 years
    t, design 8766 hours per year  
    method, 4pt or 3pt
    '''
    
    
    ''' if 3pt method, rearrange time series to begin and end with the maximum'''
    if method == '3pt':
        x = rearrangeTS(x)
    
    ''' 1. get peaks and troughs, i.e. local maxima and minima '''
    tp, ind = dat2tp(x)
    
    ''' 2. rainflow counting '''
    if method == '4pt':
        Sw, res = tp2rfc4p(tp)
    if method == '3pt':
        Sw, res = tp2rfcSimple(tp)
    
    ''' 2.1 process residues '''
    Sh = res2rfc(res)
    
    ''' 3. DEL '''
    t = scale_hours(t)
    f = 1e7/(T * t *3600)    # 3600s per hour
    DEL = calc_del([Sw, Sh], T, f, n, m)
    
    
    return DEL