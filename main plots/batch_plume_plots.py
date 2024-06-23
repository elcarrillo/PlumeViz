#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2022-05-12
# Last Modified: 2024-06-21
# Affiliation  : Fisk University, Vanderbilt University

"""
This module plots the results of Plumeria simulations in various styles. 
Specifically, it visualizes the relationship between mass flux, external water content, and maximum plume height. 
For accurate interpretation, ensure the data is filtered to display only the target parameters while keeping others constant. 
Plotting more than three varying values simultaneously can complicate result interpretation.

If you are varying multiple parameters (more than 3), use and modify 'batch_big_plot_multiy.py'.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
import colormaps as cmaps

# Data labels and definitions
size = [8, 8]
x = 'mass flux total (kg/s)'
y = 'mass fraction water added'
z = 'calculated heigth (km)'
z_dry = 'dry plume height (km)'
delta_z = 'delta z (km)'
mer = 'mass flux (kg/s)'
vent = 'vent diameter (m)'
sparks = "sparks heigth (km)"
vel = 'initial velocity (m/s)'
rho_mix = 'mixture density (kg/m3)'
delta_s = 'delta z from sparks Z (km)'
Temp = 'T_mix'
humid = 'Relative humidity, %'
ri = 'Ri'
T_ri = 'Thermal Ri'
g_prime = 'g prime'
delta_z_two_slope = 'delta z norm2'
delta_z_norm = 'delta z norm'
bouyancy_flux = 'F_b'
vent_eq = 'vent equivalent init (m)'

### Import data #####
#file_path = 'plumeria_data/plume_values_main_w_d_hunga_.csv'
file_path = 'plumeria_data/plume_values_main_u_w_t_d_var_11072023_nan_adj_.csv'
df1 = pd.read_csv(file_path)
df = df1

## select data, Mer vs height plots must be for constant velcity and temperature, modify as needed 
df = df1.loc[(df1['initial velocity (m/s)'] ==100) & (df1['magma temperature (c)'] == 900) & (df1['mass flux (kg/s)'] <1.5e10)]



# set plot parameters
theme = 'viridis_r'
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

save_plots = 'no'

def delta_z_func(height, dry_height):
    return height - dry_height

df['delta z (km)' ] = df.apply(lambda a: delta_z_func(a[z],a[z_dry]), axis=1)     # diffrence in wet plume height relative to dry plume height

## Plot 1: Scatter of w vs mer vs z
###################################################
third_variable = 'calculated heigth (km)'
norm = plt.Normalize(df[third_variable].min(), df[third_variable].max())

f, ax = plt.subplots(figsize=size)
sns.scatterplot(data=df, y=y, x=mer, palette=theme, hue=third_variable, hue_norm=norm, s=10, ax=ax)
ax.set(xlabel=r'$M_d \left[ kg \, s^{-1} \right] $', ylabel='mass fraction of external water', xscale='log')
ax.minorticks_on()
ax.get_legend().remove()

sm = plt.cm.ScalarMappable(cmap=theme, norm=norm)
sm.set_array([])
f.colorbar(sm, ax=ax, label=r'$z$ [km]')

if save_plots == 'yes':
    plt.savefig('mass_flux_gradient_sample.png', bbox_inches="tight")
else:
    plt.show()

## Plot 2: Scatter of w vs mer vs delta z
###################################################

third_variable = 'delta z (km)'
#theme_delta_z = cmaps.davos_r
theme_delta_z = 'seismic'

norm = mcolors.TwoSlopeNorm(vmin=df[third_variable].min(), vcenter=10, vmax=df[third_variable].max())

f, ax = plt.subplots(figsize=[10, 10])
sns.scatterplot(data=df, y=y, x=mer, palette=theme_delta_z, hue=third_variable, s=10, hue_norm=norm, ax=ax)
ax.set(xlabel=r'$M_d \, \left[ kg \,s ^{-1} \right]$', ylabel='mass fraction of external water, ' + r'$w$', xscale='log')
ax.minorticks_on()
ax.get_legend().remove()

sm = plt.cm.ScalarMappable(cmap=theme_delta_z, norm=norm)
sm.set_array([])
f.colorbar(sm, ax=ax, label=r'$\Delta z = \frac{H_{wet} - H_{dry}}{H_{dry}} $', extend='both')

buoyancy_threshold_x = 1e8 
buoyancy_threshold_y = 0.19 
text_position_x = 1e4      
text_position_y = 0.10 

ax.annotate('buoyancy threshold', xy=(buoyancy_threshold_x, buoyancy_threshold_y), 
            xytext=(text_position_x, text_position_y),
            arrowprops=dict(facecolor='black', arrowstyle="-|>", connectionstyle="arc3"),
            horizontalalignment='left', verticalalignment='top')

ax.set_ylim([-.01, .41])
ax.set_xlim([1e3, 5e9])

if save_plots == 'yes':
    plt.savefig('mass_flux_gradient_sample.png', bbox_inches="tight")
else:
    plt.show()

## Plot 3: Duo scatter plot
###################################################
#theme_delta_z = cmaps.vik
theme_delta_z = 'seismic'

third_variable = delta_z
norm = mcolors.TwoSlopeNorm(vmin=df[third_variable].min(), vcenter=0, vmax=df[third_variable].max())

f, ax = plt.subplots(1, 2, figsize=[16, 8], gridspec_kw={'width_ratios': [.8, 1], 'wspace': .22})

scatter1 = sns.scatterplot(data=df, y=y, x=mer, palette=theme_delta_z, hue=third_variable, hue_norm=norm, s=10, ax=ax[0])
scatter2 = sns.scatterplot(data=df, y=third_variable, x=mer, palette=theme_delta_z, hue=third_variable, hue_norm=norm, s=10, ax=ax[1])

ax[1].axhline(y=0, color='black', linestyle='dotted', linewidth=1)

for i in [0, 1]:
    ax[i].set(xlabel=r'$M_d \left[ \frac{kg}{s}\right]$', xscale='log')
    ax[i].minorticks_on()
    if i == 0:
        ax[i].set_ylabel(ylabel=r'$w$', labelpad=1)
    elif i == 1:
        ax[i].set_ylabel(ylabel=r'$\Delta \,z \,[km]$', labelpad=1)

annotations1 = [('1', (0.2, 0.8)), ('2', (0.55, 0.8)), ('3', (0.75, 0.8)), ('4', (0.75, 0.35))]
annotations2 = [('1', (0.3, 0.4)), ('2', (0.55, 0.2)), ('3', (0.75, 0.4)), ('4', (0.75, 0.8))]

bbox = dict(boxstyle='round', facecolor='white', edgecolor='black', linewidth=2)
for i, annotations in enumerate([annotations1, annotations2]):
    for text, xy in annotations:
        ax[i].annotate(text, xy=xy, xycoords='axes fraction', fontsize=10, color='black', bbox=bbox)

ax[0].annotate(r'$\bf(a)$', xy=(.02, .02), xycoords='axes fraction', color='black', fontsize=12)
ax[1].annotate(r'$\bf(b)$', xy=(.02, .02), xycoords='axes fraction', color='black', fontsize=12)

sm = plt.cm.ScalarMappable(cmap=theme_delta_z, norm=norm)
sm.set_array([])
cbar = f.colorbar(sm, ax=ax, label=r'$\Delta \,z \,[km]$', pad=.04)
cbar.ax.yaxis.set_label_coords(2, 0.5)

scatter1.legend_.remove()
scatter2.legend_.remove()

plt.tight_layout()
plt.show()

if save_plots == 'yes':
    print('Plots were saved to the current directory.')
else:
    print('No plots were saved.')
