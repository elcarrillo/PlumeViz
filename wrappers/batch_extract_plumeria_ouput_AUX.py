#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Author       : Edgar Carrillo
# Created      : 2023-07-01
# Last Modified: 2024-09-08
# Affilation   : Fisk University, Vanderbilt University

import pandas as pd
import numpy as np
import re
import os



output_dir  = 'out_u_w_t_d_var_11_07_2023_nan_adj' ## ran on 3/27/24 
output_file_path   = 'plumeria_data/plume_values_main_u_w_t_d_var_11072023_nan_adj.csv'  # dir where data is stored- 3/27/24

### use for atmospheric profile runs
def read_if_sounding(run):
    # read plumeria output file, read in 3 sections to simplify data extraction
    values_list = []
    with open(os.path.join(output_dir,run), "r") as output_file:
        lines = output_file.readlines()[5:15]
        end_lines = output_file.readlines()[-4:-1]
        dz_0_line = output_file.readlines()[24]
    
    for line in lines:
        values = float(line.rstrip().split(':')[1])
        values_list.append(values)
    
    for line in end_lines:
        s = re.sub("km", "", line.rstrip())
        values = float(s.split('=')[1])
        values_list.append(values)
    
    def get_data(line):
        vals = list(line.strip().split())
        return [float(i) for i in vals]
    
    dz_0 = get_data(dz_0_line)
    values_list.extend(dz_0)
    
    return values_list   
  


def read(run, expected_length):
    """
    Read and parse specific data from a file, filling missing or unreadable data with NaN.

    Args:
        run (str): The filename to read from.
        expected_length (int): The expected number of data points to extract.
    
    Returns:
        list: A list of extracted values, with NaN for any missing or unreadable data.
    """
    file_path = os.path.join(output_dir, run)
    values_list = [np.nan] * expected_length

    try:
        with open(file_path, "r") as output_file:
            lines = output_file.readlines()

        # Extract lines for the top part of the file
        main_lines = lines[7:20]
        # Extract lines for the bottom part of the file
        end_lines = lines[-4:-1]
        # Extract the dz_0_line if it exists
        if len(lines) > 24:
            dz_0_line = lines[24]
        else:
            dz_0_line = "0"

        # Process main lines
        for i, line in enumerate(main_lines):
            try:
                values_list[i] = float(line.split(':')[1].strip())
            except ValueError:
                print(f"Error converting string to float in main_lines: '{line.strip()}'")
                continue  # If there's a parsing error, leave the corresponding NaN in place

        # Adjust start index for end lines to continue the list
        start_index = len(main_lines)
        for i, line in enumerate(end_lines):
            try:
                values_list[start_index + i] = float(re.sub("km", "", line).strip().split('=')[1])
            except ValueError:
                print(f"Error converting string to float in end_lines: '{line.strip()}'")
                continue  # Leave NaN in place

        # Process dz_0 line to extract multiple float values
        try:
            dz_values = [float(value) for value in dz_0_line.strip().split()]
            values_list[start_index + len(end_lines):start_index + len(end_lines) + len(dz_values)] = dz_values
        except ValueError:
            print(f"Error converting string to float in dz_0_line: '{dz_0_line.strip()}'")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while reading or parsing the file {run}: {e}")

    return values_list






# make list of output file names
plumeria_output_list = [p_file for p_file in os.listdir(output_dir) if p_file.endswith('.txt')]


def data_list(data, expected_length):
    try:
        data_to_append = read(data, expected_length)
        if data_to_append is None or len(data_to_append) != expected_length:
            raise ValueError("Invalid data encountered.")
    except ValueError as ve:
        print(ve)
        data_to_append = [np.nan] * expected_length
    return data_to_append

expected_length = 33
# create the list of all extracted data, writes 0 if file has incomplete data
def data_list(data):
    try: 
        data_to_append = read(data, expected_length)
        if data_to_append is None or len(data_to_append) != expected_length:
            raise ValueError("Invalid data encountered.")
    except:
        #data_to_append = '0'
        data_to_append = [np.nan] * expected_length
    ## Note: read function cannot read corrupt files, at times plumeira can output files in odd(corrupt?) format(encoding issue?),
        ##       data from failed runs cannot be extracted so this will also return an error
    return data_to_append


ls = [data_list(l) for l in plumeria_output_list]

'''create dataframe of values with labels'''
def mer_grid(vent_list):
    columns = ['Relative humidity, %','Air temperature at vent (C)','Air pressure  at vent, atm',
                'vent diameter (m)', 'vent elevation (m)', 'initial velocity (m/s)',
                'magma temperature (c)','weight fraction gas', 'magma specific heat (j/kg k)',
                'magma density (kg/m3)','mixture density (kg/m3)', 'mass fraction water added',
                'mass flux total (kg/s)', 'calculated heigth (km)','sparks heigth (km)',
                'mastin et al 2009 height (km)', 'inum', 'z', 'm_m', 'm_a', 'm_v', 
                'm_l', 'm_i', 'u','r','T_mix','T_air','rho_mix', 'rho_air', 
                'time', 'p_air', 'water', 'ice'
                ]
    df = pd.DataFrame(vent_list, columns=columns)
    return df

df = mer_grid(ls)


############################################################################
## append addtional data  to dataframe that is not calculated by plumeria ##
## for use when changeing external water and mass flux                    ##
############################################################################

m_cal   = 'mass flux total (kg/s)'
ext_w   = 'mass fraction water added'
mer     = 'mass flux (kg/s)'
vent    = 'vent diameter (m)'  
plume_z = 'calculated heigth (km)'  
z_dry   = 'dry plume height (km)'
sparks  = 'sparks heigth (km)'
del_z   = 'delta z (km)'                   ## change in plume height relative to dry plume height
vel     = 'initial velocity (m/s)'         ## eruption velocity (m)
rho_mix = 'mixture density (kg/m3)'        ## density of the eruption mixture, includes external water premix if any is added
delta_s = 'delta z from sparks Z (km)'     ## change in plume height relative to the emprically calculated heigt from sparks et al. (1997)
Temp    = 'T_mix'                          ## temperature of the eruption mixture at the vent 
humid   = 'Relative humidity, %'           ## relative humidity in the atmosphere
vent_eq = 'vent equivalent init (m)'


rho_0  = 1.292      # ambient air density at the vent, kg/m^3
g      = 9.81       # earth gravity constant, m/s^2
T_0    = 273.15     # reference temperature, 
beta   = 1/T_0      # thermal expansin coefficient of air at STP


condition = df[ext_w] == 0 # mask to find the dry eruption mixture density

# Find the index of the first occurrence that satisfies the condition
first_index = condition.idxmax()

# Use the index to select the corresponding value from column_A
rho_dry = float(df.loc[first_index, rho_mix])

def vent_init(vent, rho_mix, w):
    return round(vent *np.sqrt((rho_mix*(1-w))/rho_dry), 1) ## add rounding function?

def mer_eq(r,vel):                ## wont work since i currently cant get exact mer values due plumeria rounding issue
    return np.pi*r**2*5.62*vel


df[vent_eq] = df.apply(lambda a: vent_init( a[vent], a[rho_mix], a[ext_w]),  axis=1)      
df['mer eq']        = df.apply(lambda a: mer_eq(a[vent_eq], a[vel]), axis=1) 


df['run'] = plumeria_output_list                                   # append file name to each row


df['mass flux (kg/s)'] = df.apply(lambda a: a[m_cal]*(1-a[ext_w]), axis=1)      # M_0 = (1-w)M_calculated



df_vent   = df[vent_eq].drop_duplicates(keep = 'first')     # get vent values, no duplicates included
vent_init_list = [float(value) for value in df_vent.astype(str).sort_values(ascending=True)]


'''
grab df per vent init
grab dry height
append column of that value 
'''

### dont need this for the large bulk runs
# for diameter in vent_init_list:
#     #df1 = pd.read_csv(file_path)
#     df  = df.loc[(df['initial velocity (m/s)'] ==75) & (df['magma temperature (c)'] == 700) & (df['mass flux (kg/s)'] <1.5e10)] #& (df[y]) == 0.14] ## change back to u = 100, T = 900
#     if diameter in df['vent equivalent init (m)'].values:                                   ## check if vent value exists in df
#         df_dry_z = df.loc[(df['vent equivalent init (m)'] == diameter) & (df[ext_w] == 0)]  ## get dry plume heights
#         #df.sort_values(by=[vent])
#         if not df_dry_z.empty:                                          # ensure df is not empty
#             dry_z = df_dry_z.iloc[0]['calculated heigth (km)']
#             df.loc[df['vent equivalent init (m)'] == diameter, 'dry plume height (km)'] = dry_z



## use vent list from vent_init_list, for the vent equivalent values and not the ven adjusted values 
temp_list = [700, 900, 1100]  # magma temperatures in Celsius
velocity_list = [75, 100, 125]  # initial velocities in m/s

# Convert vent_init_list to a set for faster membership testing
vent_set = set(vent_init_list)

#filter the DataFrame only once for the mass flux condition, since it's constant across all iterations
df_filtered = df[df['mass flux (kg/s)'] < 1.5e10]

# iterate over the unique combiinations of temperature and velocity in the filtered df
for temp, velocity in df_filtered[['magma temperature (c)', 'initial velocity (m/s)']].drop_duplicates().itertuples(index=False):
    if temp in temp_list and velocity in velocity_list:
        # Further filter df_filtered for the current temperature and velocity
        df_temp_vel = df_filtered[(df_filtered['magma temperature (c)'] == temp) & 
                                  (df_filtered['initial velocity (m/s)'] == velocity)]
        # Process only the rows with diameters sin vent_init_list
        for diameter in df_temp_vel['vent equivalent init (m)'].unique():
            if diameter in vent_set:
                # Get dry plume heights for the current diameter with no external water
                df_dry_z = df_temp_vel[(df_temp_vel['vent equivalent init (m)'] == diameter) & 
                                       (df_temp_vel[ext_w] == 0)]
                if not df_dry_z.empty:
                    dry_z = df_dry_z.iloc[0]['calculated heigth (km)']
                    # Update the 'dry plume height (km)' in the original df for the current conditions
                    df.loc[(df['initial velocity (m/s)'] == velocity) & 
                           (df['magma temperature (c)'] == temp) & 
                           (df['vent equivalent init (m)'] == diameter), 
                           'dry plume height (km)'] = dry_z


def delta_z(height, dry_height):
    return height - dry_height


df['delta z (km)' ]     = df.apply(lambda a: delta_z(a[plume_z],a[z_dry]), axis=1)     # diffrence in wet plume height relative to dry plume height


for u in [75,100, 125]:

    df.loc[df['initial velocity (m/s)'] == u]
    if u == 75:    
        ## u = 50
        df['region'] = np.where(df['delta z (km)'] > 3, 4,
                               np.where(df['delta z (km)'] < -3, 2,
                                        np.where((df['delta z (km)'] < 0) & (df['delta z (km)'] >= -3), 1,
                                                 np.where((df['delta z (km)'] > 0) & (df['delta z (km)'] <= 3), 3, np.nan)))) #np.nan or 'dry'
    elif u == 100:
    # ## u = 100
        df['region'] = np.where(df['delta z (km)'] > 6, '4',
                               np.where(df['delta z (km)'] < -6, '2',
                                        np.where((df['delta z (km)'] < 0) & (df['delta z (km)'] >= -6), '1',
                                                 np.where((df['delta z (km)'] > 0) & (df['delta z (km)'] <= 6), '3', 'dry')))) #np.nan or 'dry'
    elif u == 125:
        #  u = 150
        df['region'] = np.where(df['delta z (km)'] > 11, 4,
                               np.where(df['delta z (km)'] < -11, 2,
                                        np.where((df['delta z (km)'] < 0) & (df['delta z (km)'] >= -11), 1,
                                                 np.where((df['delta z (km)'] > 0) & (df['delta z (km)'] <=11), 3, np.nan)))) #np.nan or 'dry'
    else:
        print('error: velocity value not in list ')



def richardson(rho_mix, vent, vel):
    rho    = rho_mix 
    v_d    = vent      # vent diamter, m
    u_0    = vel       # vent exit velocity, m/s
    red_g = (g*(rho-rho_0))/rho_0
    return (red_g * v_d) / (u_0**2)


def richardson_temp(vent, vel, Temp):
    return (g*beta*vent*(T-T_0)) / vel**2

def reduced_gravity(rho_mix):
    return (9.81 *rho_mix - rho_0)/rho_0


deltaz_min = df[del_z].min()
deltaz_max = df[del_z].max()


df['Ri']            = df.apply(lambda a: richardson(a[rho_mix],a[vent_eq],a[vel]), axis=1)
df['Thermal Ri']    = df.apply(lambda a: richardson(a[vent_eq],a[vel],a[Temp]), axis=1) 
df['g prime']       = df.apply(lambda a: reduced_gravity(a[rho_mix]), axis=1) 

###################
### output      ###
###################
df.to_csv(output_file_path, index=False)
print(f"Done! CSV file saved at {output_file_path}")


