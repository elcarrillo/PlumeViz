#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2023-07-01
# Last Modified: 2024-09-08
# Affilation   : Fisk University, Vanderbilt University

import numpy as np
import random; random.seed(1)
import math
import itertools

'''
Script to create input list of vent diameter sizes for plumeria software using different 
distributions methods such as random or log increasing values
'''
## create set of random values given a set range
def random_generate(min_vent_diameter, max_vent_diameter, input_value_total):
    randomlist = []
    for i in range(1,input_value_total):
        n = random.randint(min_vent_diameter,max_vent_diameter)
        randomlist.append(n)
    return randomlist

## function to create range of values based on log2, rounds to next integer value
def binary_log(x):
    return math.ceil(math.log2(x))

## create list of 2^x distributed values to use as diameter input 
def binary_log_input(min_vent_diameter, max_vent_diameter, interval_size):
  
    interval_total = binary_log(max_vent_diameter)  ## set how many intervals
    
    i = 0
    bin_log_start_val = 1 ## use 2 to skip first iteration of 2^x
    vent_diameter_array = []

    for x in range(bin_log_start_val,interval_total+1): 
        
        i += 1
        current_max = 2**x
    
        if i == 1:
            range_start = 1
        else:
            range_start = (current_max/2) 
         ## set min range to next interval instead of starting at 1 each time

        if current_max > max_vent_diameter: ## cap max diameter to selected value
            current_max = max_vent_diameter

        vent_diameters  = list(np.round(np.linspace(range_start,current_max,interval_size),4))
        vent_diameter_array.append(vent_diameters)

    ## convert list to single dimension
    vent_diameter_list = list(itertools.chain(*vent_diameter_array)) ## combine into one list
    vent_diameter_list = [*set(vent_diameter_list)] ## 
    # sort list 
    vent_diameter_list.sort()
    return vent_diameter_list




