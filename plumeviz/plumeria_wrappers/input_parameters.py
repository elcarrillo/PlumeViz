### Last modified: 3/6/2024

"""
Use for bulk runs, i.e., batch_plumeria_input_bulk.py
"""

import os
from batch_vent_functions import binary_log_input

def main():
    # Parameters
    mass_frac_add_water_list = [float(a / 100) for a in range(0, 21)]  # 0 - 21 wt%
    magma_temp_list = [900]
    vent_vel_list = [100]  # Ran 2.1.2024
    humid_list = [0]  # Enter percent, last ran 3.20.24

    # Parameters for vent diameter radius
    min_vent_diameter = 1
    max_vent_diameter = 44000  # Use 32800 for u=150
    interval_size = 6  # Must be >1

    vent_diameter_list = binary_log_input(min_vent_diameter, max_vent_diameter, interval_size)

    # adjust individual vent properties here
    gas_frac = 0.03  #

    # sounding data file and location
    line11 = 'test.txt'  # "Data_sounding_READY/2012_7_17_00_85996072_profile.txt"

    # directory locations
    dir_loc = 'inp_TEST'  # Ran 3/07/2024
    out_loc = 'out_TEST'  # Ran 3/07/2024
    csv_path = 'plumeria_data/00plumeria_TEST.csv'  # Directory where original data is to be saved, ran 3/7/2024

    # Plumeria location
    plumeria_loc = '/Users/carrile/documents/masters_work/plume_fort_v2.3.1/plumeria'

    # create directories if they do not exist
    os.makedirs(dir_loc, exist_ok=True)
    os.makedirs(out_loc, exist_ok=True)

if __name__ == "__main__":
    main()
