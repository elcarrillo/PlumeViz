#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2023-01-19
# Last Modified: 2024-06-18
# Affiliation  : Fisk University, Vanderbilt University

import numpy as np
import pandas as pd
import os
import re

# Set the output directory and CSV path
output_dir = 'out_u_w_t_d_varied_11_07_2023_t1100max_u125max'
csv_path = 'plumeria_data/plume_values_main_u_w_t_d_var_11072023_nan.csv'

def read(run, expected_length):
    """
    Reads and parses specific data from a Plumeria output file.
    Fills missing or unreadable data with NaN.
    """
    values_list = [np.nan] * expected_length
    
    try:
        with open(os.path.join(output_dir, run), "r") as output_file:
            lines = output_file.readlines()[7:20]
            output_file.seek(0)
            end_lines = output_file.readlines()[-4:-1]
            
            for i, line in enumerate(lines):
                try:
                    values_list[i] = float(line.split(':')[1].strip())
                except ValueError:
                    continue

            for i, line in enumerate(end_lines, start=len(lines)):
                try:
                    values_list[i] = float(re.sub("km", "", line).split('=')[1].strip())
                except ValueError:
                    continue
    except Exception as e:
        print(f"Error reading or parsing file {run}: {e}")
    
    return values_list

def read_sounding(run, path, expected_length):
    """
    Reads and extracts data from a sounding file.

    :param run: The filename to read from.
    :param path: The directory where the file is located.
    :param expected_length: The expected number of data points to extract.
    :return: A list of extracted values.
    """
    values_list = [np.nan] * expected_length
    
    try:
        with open(os.path.join(path, f"{run}.txt"), "r") as output_file:
            lines = output_file.readlines()[5:15]
            for i, line in enumerate(lines):
                try:
                    values_list[i] = float(line.split(':')[1].strip())
                except ValueError:
                    continue

            end_lines = output_file.readlines()[-4:-1]
            for i, line in enumerate(end_lines, start=len(lines)):
                try:
                    s = re.sub("km", "", line)
                    values_list[i] = float(s.split('=')[1].strip())
                except ValueError:
                    continue
    except Exception as e:
        print(f"Error reading or parsing file {run}: {e}")

    return values_list

def data_list(data, expected_length, read_func):
    try:
        data_to_append = read_func(data, expected_length)
        if data_to_append is None or len(data_to_append) != expected_length:
            raise ValueError("Invalid data encountered.")
    except ValueError as ve:
        print(ve)
        data_to_append = [np.nan] * expected_length
    return data_to_append

def mer_grid(ls):
    """
    Creates a DataFrame from a list of data values.
    """
    columns = [
        'Relative humidity, %', 'Air temperature at vent (C)', 'Air pressure at vent, atm',
        'vent diameter (m)', 'vent elevation (m)', 'initial velocity (m/s)',
        'magma temperature (c)', 'weight fraction gas', 'magma specific heat (j/kg k)',
        'magma density (kg/m3)', 'mixture density (kg/m3)', 'mass fraction water added',
        'mass flux total (kg/s)', 'calculated heigth (km)', 'sparks height (km)',
        'mastin et al 2009 height (km)'
    ]

    data_list = []
    for data in ls:
        if data is not None and len(data) == len(columns):
            data_dict = {columns[i]: data[i] for i in range(len(columns))}
            data_list.append(data_dict)
        else:
            print(f"Skipping invalid data: {data}")

    df = pd.DataFrame(data_list)
    return df

def adjust_vent(vent, rho_wet, w, rho_dry):
    """
    Adjusts the vent diameter based on mixture density.
    """
    return np.sqrt(rho_dry / (rho_wet * (1 - w))) * vent

if __name__ == "__main__":
    expected_length = 16
    plumeria_output_list = [p_file for p_file in os.listdir(output_dir) if p_file.endswith('.txt')]
    ls = [data_list(l, expected_length, read) for l in plumeria_output_list]
    
    df = mer_grid(ls)

    x = 'mass flux total (kg/s)'
    y = 'mass fraction water added'
    rho_mix = 'mixture density (kg/m3)'
    vent = 'vent diameter (m)'

    df = df.loc[df[vent].notna()]

    condition = df[y] == 0
    first_index = condition.idxmax()
    rho_dry = float(df.loc[first_index, rho_mix])

    df['vent adjusted (m)'] = df.apply(lambda a: adjust_vent(a[vent], a[rho_mix], a[y], rho_dry), axis=1)
    df['mass flux (kg/s)'] = df.apply(lambda a: a[x] * (1 - a[y]), axis=1)

    df.to_csv(csv_path, index=False)
    print('Done, successful extraction! ' + csv_path)
