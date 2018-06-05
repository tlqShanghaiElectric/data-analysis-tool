# -*- coding: utf-8 -*-
"""
Created on Tue May 29 13:47:03 2018

@author: 12600771
"""

import math

def getScitificNumber(num):
    """
        present num as sign * a * 10 ^ b
    """

    sign = 1 if num >= 0 else -1
    num = abs(num)
    b = math.floor(math.log10(num))
    a = num / math.pow(10, b)
    return sign, a, b

def prettyNum(num1, num2):
    """
        num1 is the smaller limit and num2 is the bigger limit
        the program is to keep one significant digit of num1 and num2 
    E.g:
        prettyNum(1820, 1960) -> (1820, 1960)               
        prettyNum(1.21e6, 1.8e6) -> (1e6, 2e6)              
        prettyNum(1.21e6, 1.27e6) -> (1e6, 2e6)             
        prettyNum(-1.8e6, -1.21e6) -> (-2e6, -1e6)         
        prettyNum(-1.25e6, -1.21e6) -> (-2e6, -1e6)         
        prettyNum(-1.25e6, 1.21e6) -> (-2e6, 2e6)           
        prettyNum(8.2e5, 1.8e6) -> (0, 2e6)
        prettyNum(-1.8e6, -8.2e5) -> (-2e6, 0)
        prettyNum(-8.2e6, 1.8e7) -> (-1e7, 2e7)
        prettyNum(-8.2e6, 1.8e9) -> (-1e9, 2e9)
        prettyNum(-8.2e8, 1.8e6) -> (-9e8, 1e8)
    """
    
    if num2 < num1:
        num1, num2 = num2, num1

    # For those using scitific numbers
    if abs(num1) >= 10000 and abs(num2) >= 10000:
        # present num as num = sign * a * 10 ^ b
        sign1, a1, b1 = getScitificNumber(num1)
        sign2, a2, b2 = getScitificNumber(num2)

        # update a1 and a2
        a1 = math.floor(a1 * sign1)
        a2 = math.ceil(a2 * sign2)

        num1 = a1 * math.pow(10, b1)
        num2 = a2 * math.pow(10, b2)

        # return pretty number
        if b1 != b2:
            if sign1 == sign2:
                if sign1 > 0:
                    # both are positive
                    num1 = 0
                else:
                    # both are negative
                    num2 = 0
            else:
                if b1 < b2:
                    num1 = -1 * math.pow(10, b2)
                else:
                    num2 = 1 * math.pow(10, b1)

    return num1, num2

