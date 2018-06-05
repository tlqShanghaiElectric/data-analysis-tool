# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 09:47:13 2018

@author: tlqld
"""

import numpy as np
import rainflow
#import math

def calDel(y_raw, m, life, t, T):
    if t < 8766:
        t = 8766
        
    f=1e7/(life*t*3600)
    y = np.asarray(y_raw,dtype='float64')
    counts = rainflow.count_cycles(y)

    s = 0
    for count in counts:
        s += count[1] * np.power(count[0], m)
        
    load = np.power(s/(T*f), 1/m) / 1000 # Unit: kNm
    return load