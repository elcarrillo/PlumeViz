#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2023-10-23
# Last Modified: 2024-06-21
# Affiliation  : Vanderbilt University


'''
Python Wrapper for Plumeria v2.3.1

This wrapper works witout any modificatons to the Plumeria Fortran Code, note that you will need 
a fortran compilar installed with Plumeria v2.3.1 installed (run the makefile in a terminal)

This wrapper currently allows for multiple values of initial vent diameter, external water content, initial magma temperature,
and relative humidity, but note that the more varying parameters allowed the higher the computational cost (a million simulations would take a few hours) 


'''


import numpy as np
import subprocess
import itertools
from input_parameters import *

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
        # line 11, # add sounding file location here if needed
        " #",
        "#  Tropospheric properties (used only if no atmospheric file is used)",
        "",
        "0.                   #Air temperature at vent, Celsius.",
        f"{humid}.            #Air relative humidity",
        "-0.0065              #thermal lapse rate in troposphere (K/m upward--should be negative)",
        "11000.               #Elevation of tropopause (m asl)",
        "9000.0               #Tropopause thickness, m",
        "0.0016               #thermal lapse rate above tropopause (K/m--should be positive)",
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


def create_input_parameters_combinations():
    """  Create a grid of parameter combinations. """
    combinations = itertools.product(vent_diameter_list, mass_frac_add_water_list, magma_temp_list, vent_vel_list, humid_list)
    return combinations

def run_plumeria(input_file):
    """ Run PLUMERIA with the specified input file. """
    try:
        subprocess.run([plumeria_loc, f"{dir_loc}/Grid_Runs_in_{input_file}.txt"], timeout=0.5)
    except Exception as e:
        print(f"Error running {input_file}: {str(e)}")
        #skipped_files.append(input_file)

def main():
    input_name_list = []
    #skipped_files   = []
    combinations = create_input_parameters_combinations()

    for index, (vent_diam, water_wt, magma_temp, vent_vel, humid) in enumerate(combinations, start=1):
        output_name = f"run{index}"
        make_inp_file(output_name, magma_temp, gas_frac, vent_diam, vent_vel, water_wt, humid, out_loc)
        input_name_list.append(output_name)

    # run PLUMERIA with the generated input files
    for input_file in input_name_list:
        run_plumeria(input_file)

    print('Done, successful run!')

if __name__ == '__main__':
    main()
