#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2021-11-21
# Last Modified: 2023-11-25
# Affiliation  : Fisk University, Vanderbilt University

"""
Standalone Python wrapper for Plumeria v2.3.1

NOTE: Runs a single simulation only.
"""

import numpy as np
import pandas as pd
import os
import subprocess

# Adjust individual vent properties here 
magma_temp = 900.0
gas_frac = 0.03
vent_diam = 100.0   
vent_vel = 100
water_wt = 0.16  # mass_frac_add_water
humid = 0  # must be percent (%) value

# Sounding data file and location
line11 = 'test.txt'  # Example: "Data_sounding_READY/2012_7_17_00_85996072_profile.txt"

# Directory names for input and output files
inp_loc = 'inp_test_ice'
out_loc = 'out_test_ice'

# Path to Plumeria executable file
plumeria_loc = '/Users/carrile/documents/masters_work/plume_fort_v2.3.1/plumeria'

# Make directories if they do not exist
os.makedirs(inp_loc, exist_ok=True)
os.makedirs(out_loc, exist_ok=True)

def make_inp_file(output_name, magma_temp, gas_frac, vent_diam, vent_vel, water_wt, humid, out_loc):
    """Create input files for a single run with specified parameters."""
    
    lines = [
        "# Input file for the Fortran version of Plumeria.",
        "# Lines that begin with a '#' are comment lines.",
        "",
        "# Output file name",
        f"{out_loc}/Grid_Runs_out_{output_name}.txt",
        "",
        "# Information on whether to read met. input file.",
        "# The first line should supply a yes or no. If that line is yes, the next line",
        "# should be the name of the input file used.",
        "no  # Are you supplying a file of atmospheric properties?", 
        # Uncomment or add sounding file location here if needed, ensure to change previous line to yes
        # line11,
        "",
        "# Tropospheric properties (used only if no atmospheric file is used)",
        "0.0  # Air temperature at vent, Celsius.",
        f"{humid}  # Air relative humidity",
        "-0.0065  # Thermal lapse rate in troposphere (K/m upward--should be negative)",
        "11000.0  # Elevation of tropopause (m asl)",
        "9000.0  # Tropopause thickness, m",
        "0.0016  # Thermal lapse rate above tropopause (K/m--should be positive)",
        "",
        "# Vent properties",
        "0.0  # Vent elevation (m asl)",
        f"{vent_diam}  # Vent diameter (m)",
        f"{vent_vel}  # Exit velocity (m/s)",
        f"{water_wt}  # Mass fraction added water",
        "",
        "# Magma properties",
        f"{magma_temp}  # Magma temperature",
        f"{gas_frac}  # Mass fraction gas in magma",
        "1000.0  # Magma specific heat, J/kg K",
        "2500.0  # Magma density (DRE), kg/m3"
    ]

    with open(f"{inp_loc}/Grid_Runs_in_{output_name}.txt", "w") as file:
        file.write("\n".join(lines))

def single_run(file_name=output_name):
    """Run the Plumeria simulation with the specified input file."""
    try:
        subprocess.run([plumeria_loc, f"{inp_loc}/Grid_Runs_in_{file_name}.txt"], timeout=0.5)
        print('Done, successful run!')
    except subprocess.TimeoutExpired:
        print('Error: Plumeria run timed out.')
    except Exception as e:
        print(f'Error: Could not run Plumeria. {e}')

if __name__ == "__main__":
    # Default name template: f"{out_loc}/Grid_Runs_out_{output_name}.txt"
    output_name = "run1"  # Name your file

    # Create the input file
    make_inp_file(output_name, magma_temp, gas_frac, vent_diam, vent_vel, water_wt, humid, out_loc)

    # Run the simulation
    single_run()
