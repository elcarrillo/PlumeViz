#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2023-10-31
# Last Modified: 2023-03-28
# Affiliation: Vanderbilt University

import numpy as np
import pandas as pd
import os
import subprocess
import random
import math
import itertools


plumeria_loc = '/Users/carrile/documents/masters_work/plume_fort_v2.3.1/plumeria'  ## location where your version of PLUMERIA is stored
dir_loc  = 'inp_u_w_t_d_var_11_07_2023_nan_adj'
out_loc  = 'out_u_w_t_d_var_11_07_2023_nan_adj' 

csv_path   = 'plumeria_data/plume_values_main_u_w_t_d_var_11072023_nan.csv'  # dir where data is stored


gas_frac = .03
humid    = 0  

os.makedirs(dir_loc, exist_ok=True)
os.makedirs(out_loc, exist_ok=True)


def make_inp_file(output_name, magma_temp, gas_frac, vent_diam, vent_vel, water_wt, humid, out_loc):
    lines = [
        "#  Input file for the Fortran version of Plumeria.",
        "#  Lines that begin with a '#' are comment lines.",
        "",
        "#  Output file name",
        f"{out_loc}/Grid_Runs_out_{output_name}.txt",
        "",
        "#  Information on whether to read met. input file.",
        "#  The first line should supply a yes or no. If that line is yes, the next line",
        "#  should be the name of the input file used.",
        "no                                #are you supplying a file of atmospheric properties?", 
        # line 11, # add sounding file loc here if needed
        " #",
        "#  Tropospheric properties (used only if no atmospheric file is used)",
        "",
        "0.                   #Air temperature at vent, Celsius.",
        f"{humid}.                  #Air relative humidity",
        "-0.0065              #thermal lapse rate in troposphere (K/m upward--should be negative)",
        "11000.               #Elevation of tropopause (m asl)",
        "9000.0                #Tropopause thickness, m",
        "0.0016                #thermal lapse rate above tropopause (K/m--should be positive)",
        "",
        "#  Vent properties",
        "",
        "0.0                            #Vent elevation (m asl)",
        f"{vent_diam}                #vent diameter (m)",
        f"{vent_vel}                 #exit velocity (m/s)",
        f"{water_wt}                   #mass fraction added water",
        "",
        "#   Magma properties",
        "",
        f"{magma_temp}                 #magma temperature",
        f"{gas_frac}                 #mass fraction gas in magma",
        "1000.                #magma specific heat, J/kg K",
        "2500.                #magma density (DRE), kg/m3"
    ]

    with open(f"{dir_loc}/Grid_Runs_in_{output_name}.txt", "w") as file:
        file.write("\n".join(lines))



def single_run(file_name):
    try:
        # remove leading and trailing whitespace from the file name
        file_name = file_name.strip()
        subprocess.run([plumeria_loc, f"{dir_loc}/Grid_Runs_in_{file_name}.txt"], timeout=.5)
    except subprocess.TimeoutExpired:
        print(f"Execution of '{file_name}' timed out.")
    except Exception as e:
        print(f"Error executing '{file_name}': {e}")


def multiple_runs(file_list):
    skipped_files = []
    for output_file in file_list:
        try:
            single_run(output_file)
        except:
            skipped_files.append(output_file)
    
    if skipped_files:
        print("Skipped files:")
        for skipped_file in skipped_files:
            print(skipped_file)




# define the list parameters
parameter_combinations = [
        {'vent_vel': 75, 'magma_temp': 700.0},
        {'vent_vel': 75, 'magma_temp': 900.0},
        {'vent_vel': 75, 'magma_temp': 1100.0},
        {'vent_vel': 100, 'magma_temp': 700.0},
        {'vent_vel': 100, 'magma_temp': 900.0,},
        {'vent_vel': 100, 'magma_temp': 1100.0},
        {'vent_vel': 125, 'magma_temp': 700.0},
        {'vent_vel': 125, 'magma_temp': 900.0},
        {'vent_vel': 125, 'magma_temp': 1100.0},
    ]

# iterate over the CSV paths and run each combination
run_count = 0 
for config in parameter_combinations:
    df = pd.read_csv(csv_path)
    vent_vel = config['vent_vel']            ## define velocity parameter
    magma_temp = config['magma_temp']        ## define magma temperature paramter

    df = df.loc[(df['initial velocity (m/s)'] == vent_vel ) & (df['magma temperature (c)'] == magma_temp )]                                # get rid of data from failed runs
    df = df[['mass fraction water added','vent adjusted (m)']]

    # adjust other parameters as needed

    tuple_list = [(row['mass fraction water added'], row['vent adjusted (m)']) for _, row in df.iterrows()]
    # os.makedirs(dir_loc, exist_ok=True)
    # os.makedirs(out_loc, exist_ok=True)
    
    input_name_list = []
    for water_wt, vent_diam in tuple_list: 
        run_count = run_count + 1
        output_name = "run" + str(run_count)
        make_inp_file(output_name, magma_temp, gas_frac, vent_diam, vent_vel, water_wt, humid, out_loc)
        input_name_list.append(output_name)

    # execute plumeria runs for this configuration
    multiple_runs(input_name_list)

print('All configurations completed!')