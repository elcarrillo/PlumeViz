#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2023-09-19
# Last Modified: 2024-06-22
# Affiliation  : Vanderbilt University

"""
This script plots the Plumeria results, focusing on 3x3 grid of mass flux vs. external water content vs. maximum plume height. 
Each panel in the geid will display mer vs external water vs max plume height at a constant initial velocity and initial magma temperature value. 
Ensure your data is filtered to display target parameters with other variables held constant for accurate interpretation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
#import colormaps as cmaps 

def plot_plumeria_results(csv_path, save_plots='no'):
    # Load and filter the data
    df = pd.read_csv(csv_path)
    #df = df.loc[(df['initial velocity (m/s)'] == 100) & (df['magma temperature (c)'] == 900)]

    # Define variables
    x = 'mass flux total (kg/s)'
    mer = 'mass flux (kg/s)'
    y = 'mass fraction water added'
    z = 'calculated heigth (km)'
    ri = 'Ri'

    vel_list = [75, 100, 125]   # Initial velocity masks
    mag_temp = [700, 900, 1100] # Initial magma temperature masks

    # Create conditions and sub-dataframes
    conditions = [
        (df['initial velocity (m/s)'] == vel) & (df['magma temperature (c)'] == temp)
        for vel in vel_list
        for temp in mag_temp
    ]

    data_frames = [df[condition] for condition in conditions]

    ## define the colorpalette for the plots
    #theme = cmaps.lajolla
    #theme = cmaps.davos_r
    theme = 'viridis_r'
    #theme = cmaps.imola_r

    # Global plot parameters
    params = {
        'legend.title_fontsize': 'xx-small',
        'axes.labelsize': 20,
        'font.size': 16,
        'legend.fontsize': 12,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'font.family': 'serif',
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.minor.visible': True,
        'ytick.minor.visible': True,
        'xtick.top': True,
        'ytick.right': True,
        'figure.autolayout': True
    }
    plt.rcParams.update(params)

    # Set the third variable and normalization for hue
    third_variable = 'calculated heigth (km)'
    norm = mcolors.Normalize(vmin=df[z].min(), vmax=df[z].max())

    # create 3x3 subplots
    num_rows = 3
    num_cols = 3
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 10), sharey=True, sharex=True, 
                            gridspec_kw={'width_ratios': [0.8, 0.8, 0.8], 'wspace': 0.001, 'hspace': 0.001})

    for i, df_sub in enumerate(data_frames):
        row = i // num_cols
        col = i % num_cols
        ax = axs[row, col]

        # Ensure hue variable exists and is assigned correctly
        if not df_sub.empty:
            sns.scatterplot(data=df_sub, y=y, x=mer, palette=theme, hue=third_variable, hue_norm=norm, s=5, ax=ax)
            ax.get_legend().remove()
        else:
            sns.scatterplot(data=df_sub, y=y, x=mer, s=5, ax=ax)

        ax.set(xlabel=None, ylabel=None, xscale='log')
        ax.minorticks_on()
        ax.set_xlim([1e3, 2e12])

        ax.annotate(r'$\bf({})$'.format(chr(97 + i)), xy=(0.02, 0.92), xycoords='axes fraction', color='black', fontsize=12)

        u_var = df_sub['initial velocity (m/s)'].max() if not df_sub.empty else "N/A"
        T_var = df_sub['magma temperature (c)'].max() if not df_sub.empty else "N/A"
        annotations = [(f'u = {u_var} m/s\n T = {T_var} °C', (0.5, 0.75))]
        bbox = dict(boxstyle='round', facecolor='white', edgecolor='black', linewidth=2)
        for text, xy in annotations:
            ax.annotate(text, xy=xy, xycoords='axes fraction', fontsize=15, color='black', bbox=bbox)

    # Create colorbar
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=theme, norm=norm), cax=cbar_ax, label=r'$z$ [km]')
    cbar.ax.yaxis.set_ticks_position('right')

    # Adjust the layout
    fig.supxlabel(r'$M_d$ [kg s$^{-1}$]')
    fig.supylabel('Mass fraction of external water, ' + r'$w$')
    fig.subplots_adjust(bottom=0.08, left=0.08, right=0.9, top=0.9)

    # Save or show plot
    if save_plots == 'yes':
        plt.savefig('mass_flux_gradient_sample.png', dpi=300, bbox_inches="tight")
    else:
        plt.show()

if __name__ == "__main__":
    csv_path = 'plumeria_data/plume_values_main_u_w_t_d_var_11072023_nan_adj_.csv'  # Set the file path for the data
    plot_plumeria_results(csv_path, save_plots='no')
