#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2021-12-21
# Last Modified: 2024-06-21
# Affiliation  : Fisk University, Vanderbilt University

'''
Description:
This script visualizes NOAA sounding data, 

NOTE: please change file paths, directory names, and parameters as needed.
'''


import math
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style("darkgrid")

def read_sounding_file(file_path):
    """
    - reads and processes the sounding data file
    - skips the first four lines and returns the remaining lines
    """
    with open(file_path, "r") as sounding_data:
        lines = sounding_data.readlines()[4:]
    lines = [line.strip() for line in lines if line.strip()]
    return lines

def clean_value(value):
    """
    - removes any non-numeric characters from the value
    
    Note: NOAA sounding files contain an E (estimated surface height)sometimes 
    in the Height Columns thus this function is needed to clean the data.
    """
    try:
        return float(value.replace('E', ''))
    except ValueError:
        return None

def process_sounding_data(lines):
    """
    converts lines of sounding data into a DataFrame and cleans numeric values
    """
    data = [line.split() for line in lines]
    df = pd.DataFrame(data, columns=['pressure', 'hgt(m)', 'temp (c)', 'dew pt (c)', 'wd dir', 'wd spd'])
    df['temp (c)'] = df['temp (c)'].apply(clean_value)
    df['dew pt (c)'] = df['dew pt (c)'].apply(clean_value)
    df['hgt(km)'] = df['hgt(m)'].apply(clean_value)/1000   ## clean height data and conver to km
    #df = df.dropna(subset=['temp (c)', 'dew pt (c)', 'hgt(m)'])  # drop rows with NaN values in these columns
    return df

def calculate_relative_humidity(temp, dew):
    """
    calculates the relative humidity given temperature and dew point
    """
    
    beta = 17.625
    lambd = 243.04
    e_top = math.exp((beta * dew) / (lambd + dew))
    e_bot = math.exp((beta * temp) / (lambd + temp))
    rel_h = (e_top / e_bot) * 100
    return rel_h

def add_relative_humidity(df):
    """
    adds a column for relative humidity to the DataFrame
    """
    df['rel_humid (%)'] = df.apply(lambda x: calculate_relative_humidity(x['temp (c)'], x['dew pt (c)']), axis=1)
    return df

def plot_sounding_data(df):
    """
    plots temperature vs. height and relative humidity vs. height
    """
    fig, ax = plt.subplots(1, 2, figsize=(12, 6), sharey = True)
    sns.lineplot(data=df, y='hgt(km)', x='rel_humid (%)',sort=True, orient='y', ax=ax[0]).set(title='Relative Humidity vs Height')
    sns.lineplot(data=df, y='hgt(km)', x='temp (c)', sort=True, orient='y',ax=ax[1]).set(title='Temperature vs Height')
    ax[0].yaxis.set_label_text('Elevation above sea level (km)', fontsize=18)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    sounding_file = '41683870_profile_Yellowstone.txt'  # sample data, update the path to your sounding data file
    lines = read_sounding_file(sounding_file)
    df = process_sounding_data(lines)
    df = add_relative_humidity(df)
    plot_sounding_data(df)
