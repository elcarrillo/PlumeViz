#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2023-05-01
# Last Modified: 2024-06-21
# Affiliation  : Fisk University, Vanderbilt University

'''
Description:
This script visualizes plumeria output data, focusing on the mixture density versus the mass fraction 
of external water. The primary function, plot_density_vs_mass_fraction, generates the plot using data from 
a CSV file thus Plumeria results must be extracted into csv first. 

note: please change file paths, directory names, and parameters as needed. The current paramater labels 
are from a pre-defiend list (see README) eg initial magma temperature => 'magma temperature (c)'
'''


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
#import colormaps as cmaps
import logging
import sys

# set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# global constants and configurations for plotting
PLOT_PARAMS = {
    'legend.title_fontsize': 'xx-small',
    'axes.labelsize': 16,
    'font.size': 16,
    'legend.fontsize': 10,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'font.family': 'serif',
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.minor.visible': True,
    'ytick.minor.visible': True,
    'xtick.top': True,
    'ytick.right': True,
    'figure.autolayout': True  # Get tight layout 
}

def configure_plot_params(params):
    """
    configure matplotlib plot parameters.
    """
    plt.rcParams.update(params)

def k2c(temp):
    """
    convert temperature from Kelvin to Celsius.
    """
    return temp - 273

def plot_density_vs_mass_fraction(file_path, save_plots='no', plots_dir='plots_thermodynamic/'):
    """
    plot mixture density vs. mass fraction of external water with an inset plot for mass fractions.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        sys.exit(1)

    df = df.loc[(df['initial velocity (m/s)'] == 100) & (df['magma temperature (c)'] == 900)]
    df['T_mix (c)'] = df['T_mix'].apply(k2c)

    minvalueT = df['T_mix (c)'].min()
    maxvalueT = df['T_mix (c)'].max()
    df_w = df.sort_values(by=['mass fraction water added'])
    min_w = df_w[df_w['T_mix (c)'] == minvalueT]['mass fraction water added'].values[0]

    norm = mcolors.Normalize(vmin=minvalueT, vmax=maxvalueT)
    third_variable = 'T_mix (c)'
    size = [8, 7]
    ## theme = cmaps.imola # uses colormaps library
    theme = 'viridis_r'

    f, ax = plt.subplots(figsize=size)
    sns.scatterplot(data=df, y='mixture density (kg/m3)', x='mass fraction water added',
                    palette=theme, hue=third_variable, legend=True, s=100, style='magma temperature (c)', hue_norm=norm)
    ax.get_legend().remove()

    sm = plt.cm.ScalarMappable(cmap=theme, norm=norm)
    sm.set_array([])
    f.colorbar(sm, ax=ax, label=r'$T_{mix}$ [°C]', pad=0.01)

    plt.ylabel(r'$\rho_{mix}$ [kg m$^{-3}$]')
    plt.xlabel(r'Mass fraction of external water, $w$')

    axin = inset_axes(ax, width="55%", height="50%", loc='upper left',
                      bbox_to_anchor=(0.13, .01, 1, 1), bbox_transform=ax.transAxes, borderpad=1.5)
    sns.scatterplot(data=df, y='m_v', x='mass fraction water added', palette=theme, hue=third_variable, hue_norm=norm, marker='o', label=r'$m_v$', s=50, ax=axin)
    sns.scatterplot(data=df, y='m_l', x='mass fraction water added', palette=theme, hue=third_variable, hue_norm=norm, marker='X', label=r'$m_l$', s=50, ax=axin)
    sns.scatterplot(data=df, y='m_m', x='mass fraction water added', palette=theme, hue=third_variable, hue_norm=norm, marker='^', label=r'$m_m$', s=50, ax=axin)

    def text_position(x_or_y, index, plus_or_minus_n):
        return df[x_or_y].values[index] + plus_or_minus_n * .5 * df[x_or_y].values[index]

    axin.text(text_position('mass fraction water added', 0, .6), text_position('m_v', 0, 1.5), r'$m_v$', fontsize=16)
    axin.text(text_position('mass fraction water added', 0, .6), text_position('m_l', 1, -1.9), r'$m_l$', fontsize=16)
    axin.text(text_position('mass fraction water added', 0, .6), text_position('m_m', 0, -.08), r'$m_m$', fontsize=16)
    axin.get_legend().remove()

    axin.tick_params(axis="x", direction="in")
    axin.tick_params(axis="y", direction="in")
    axin.tick_params(top=True, right=True)
    axin.yaxis.set_label_text('Mass fraction', fontsize=14)
    axin.xaxis.set_label_text(r'Mass fraction of external water, $w$', fontsize=14)
    axin.axvline(x=min_w, color='lightgray', linestyle='solid', linewidth=1, zorder=0)
    ax.axvline(x=min_w, color='lightgray', linestyle='solid', linewidth=1, zorder=0)
    axin.text(.2, .45, r'$ T_{mix}^{min} = 100.2$°C', fontsize=14, snap=True)
    ax.text(.2, 3.5, r'$ T_{mix}^{min} = 100.2$°C')

    if save_plots == 'yes':
        plt.savefig(f'{plots_dir}/rho_mix_and_mass_fracs.png', bbox_inches="tight")
    else:
        plt.show()

if __name__ == "__main__":
    configure_plot_params(PLOT_PARAMS)
    file_path = 'plumeria_data/plume_values_main_u_w_t_d_varied_11072023_t1100max_u125max_adj.csv'
    plot_density_vs_mass_fraction(file_path, save_plots='no')
