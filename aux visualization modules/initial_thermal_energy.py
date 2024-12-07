#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Contributors : Edgar Carrillo (1), Kristen Fauria (1)
# Created      : 2023-09-04
# Last Modified: 2024-06-20
# Affiliation  : (1) Vanderbilt University

"""
This script estimates the thermal energy as water is added to a volcanic mixture.

It calculates the thermal energy ratio (water/magma) for varying mass fractions of water added to the magma.
The results are plotted to visualize the relationship between the mass fraction of water and the thermal energy ratio.
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns




## Global  plot parameters
params = {
    'legend.title_fontsize' : 'xx-small',
   'axes.labelsize': 10,
   'font.size': 12,
   'legend.fontsize': 10,
   'xtick.labelsize': 10,
   'ytick.labelsize': 10,
   'xtick.direction' : 'in',
   'ytick.direction':'in',
   'xtick.minor.visible' : True,        
   'ytick.minor.visible' : True,
   'xtick.top' : True,
   'ytick.right': True, 
   'figure.autolayout': True   ## get tight layout 
   }
plt.rcParams.update(params)  # update plot paramters

#constants
T0 = 273.15
cr = 1000    # heat capacicity of magma, J/(kg*K)
cw = 4200    # heat capacity of liquid water J/(kg*K)
tr = 900+T0 # initial temperature of rock in °C
tw = 17.5+T0 # initial temperature of water in °C
Hdry = cr*tr # calculate constants value for dry thermal energy
Hwet = cw*tw # calculate constants value for wet thermal energy

# array of mass fraction of water added 
mass_frac_add_water_list = [float(a * 0.01) for a in range(101)]

#calculare thermal energy H_mix = (Cr*T_r/Cw*T_w) * w
def thermal_energy_calc(w):
	return (Hdry/Hwet)*w

# make dataframe
df = pd.DataFrame(mass_frac_add_water_list, columns=['w'])
df['H_mix'] = df.apply(lambda a: thermal_energy_calc(a['w']), axis=1) 

def main():
	# plot
	f, ax = plt.subplots()
	sns.lineplot(data = df, x = 'w', y = 'H_mix')
	ax.set(xlabel = 'mass ratio (water/magma', ylabel = 'thermal energy ration (water/magma)')
	plt.show()


if __name__=='__main__':
    main()