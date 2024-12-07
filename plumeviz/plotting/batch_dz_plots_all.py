#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2023-04-21
# Last Modified: 2024-06-22
# Affiliation  : Fisk University, Vanderbilt University


"""
This script generates DZ plots for Plumeria simulation results, depicting variables such as upward velocity, plume bulk temperature, plume bulk density, 
and mass fractions of vapor, air, liquid, and ice as functions of plume height. These plots are intended for single run results. 
If you need to plot multiple runs, consider adding a sorting method to manage the plotted results effectively.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import LogLocator
from joblib import Parallel, delayed
from timeit import default_timer as timer
from contextlib import suppress

# Global Variables and Paths
n_cores = os.cpu_count()
#path_plots = '/Volumes/ed_ext/'
output_dir = 'output_TEST/'
plot_dir = 'Plots_TEST/'

data_labels = [
    'inum', 'z', 'm_m', 'm_a', 'm_v', 'm_l', 'm_i', 'u', 'r', 'T_mix', 
    'T_air', 'rho_mix', 'rho_air', 'time', 'p_air', 'rho_water', 'rho_ice'
]

# Global plot Parameters
params = {
    'legend.title_fontsize': 'xx-small',
    'axes.labelsize': 10,
    'font.size': 12,
    'legend.fontsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'text.usetex': False
}
plt.rcParams.update(params)
plot_size = [15, 7]
colors = ['black', 'navy', 'blueviolet', 'royalblue', 'teal', 'lightseagreen', 'green', 'yellowgreen']
line_color = mcolors.CSS4_COLORS[colors[3]]

def get_data(line):
    vals = line.strip().split()
    with suppress(ValueError):
        vals = [float(i) for i in vals]
    return vals

def split_into_columns(row_of_data):
    row_of_data = row_of_data.rstrip()
    values = float(row_of_data.split(':')[1])
    return values

def read_mer_and_w(run):
    with open(os.path.join(output_dir, run), "r") as output_file:
        lines = output_file.readlines()[10:20]
    values_list1 = [split_into_columns(line) for line in lines]
    vent_diameter = values_list1[-10]
    external_water_wt = values_list1[-2]
    mass_eruption_rate = "{:.2e}".format(values_list1[-1])
    return external_water_wt, mass_eruption_rate, vent_diameter

def read_txt(run):
    with open(os.path.join(output_dir, run), "r") as output_file:
        dz_lines = output_file.readlines()[24:-5]
    values_list = [get_data(dz_line) for dz_line in dz_lines]
    return values_list

def make_plots(run_name):
    w, mer, v = read_mer_and_w(run_name)
    plot_output_name = run_name.replace('.txt', '.png')
    try:
        extracted_data = read_txt(run_name)
        extracted_data_stack = np.vstack(extracted_data)

        df = pd.DataFrame(extracted_data_stack, columns=data_labels)

        x_labels = [
            r'$u \, \left( \frac{m}{s}\right)$', r'$T_{mix} (°C)$', r'$ \rho \, \left(\frac{kg}{m^3}\right) $',
            'mass fraction, vapor & air', 'mass fraction, liquid & ice'
        ]
        f, axs = plt.subplots(1, 5, figsize=plot_size, sharey=True)

        state = 0
        for i in range(5):
            axs[i].grid(True, linestyle='--', linewidth=0.5, color='grey')
            axs[i].grid(which='minor', color='lightgrey', linestyle=':', linewidth=0.5)
            axs[i].minorticks_on()
            axs[i].tick_params(axis="x", direction="in")
            axs[i].tick_params(axis="y", direction="in")
            axs[i].tick_params(which='minor', axis="x", direction="in")
            axs[i].tick_params(which='minor', axis="y", direction="in")
            axs[i].set_xlabel(x_labels[state])
            state += 1

        axs[0].set_ylabel('z above vent (km)')

        U = df['u']
        Z = df['z'] / 1000
        T = df['T_mix'] - 273
        m_A = df['m_a']
        m_V = df['m_v']
        m_L = df['m_l']
        m_I = df['m_i']
        Rho = df['rho_mix']
        Rho_a = df['rho_air']

        axs[0].plot(U, Z, linewidth=2, color=line_color)
        axs[1].plot(T, Z, linewidth=2, color=line_color)
        axs[2].plot(Rho, Z, linewidth=2, color=line_color, label=r'$\rho_m$')
        axs[2].plot(Rho_a, Z, linewidth=2, color='black', label=r'$\rho_a$')
        axs[3].semilogx(m_V, Z, linewidth=2, color=line_color, label=r'm$_{v}$')
        axs[3].semilogx(m_A, Z, linewidth=2, color='black', label=r'm$_{a}$')
        axs[4].semilogx(m_L, Z, linewidth=2, color=line_color, label=r'm$_{l}$')
        axs[4].semilogx(m_I, Z, linewidth=2, color='black', label=r'm$_{i}$')

        for i in [2, 3, 4]:
            axs[i].legend(loc=0, fancybox=True, shadow=True)

        for i in [3, 4]:
            axs[i].xaxis.set_minor_locator(LogLocator(base=100))
            axs[i].tick_params(which='minor', labelbottom=False)
            axs[i].set_xlim(left=0.0000001, right=1.1)

        plt.suptitle('MER = ' + str(mer) +'kg/s' +', d = ' + str(v)+ 'm')
        plt.tight_layout()
        plt.savefig(os.path.join(plot_dir, plot_output_name))
        plt.close('all')

    except Exception as e:
        print(f'Failed run {run_name}: {e}')

def get_user_confirmation():
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Operation cancelled by user.")
        exit()

def main():
    start = timer()
    plumeria_output_list = [p_file for p_file in os.listdir(output_dir) if p_file.endswith('.txt')]
    
    # warning if the number of plots exceeds 10
    if len(plumeria_output_list) > 10:
        print(f"Warning: You are about to generate {len(plumeria_output_list)} plots. This may take a significant amount of time.")
        get_user_confirmation()
    
    Parallel(n_jobs=n_cores)(delayed(make_plots)(plumeria_output) for plumeria_output in plumeria_output_list)
    end = timer()
    print(f'Time taken: {end - start} seconds')
    print('Done')

if __name__ == '__main__':
    main()