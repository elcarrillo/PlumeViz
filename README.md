# PlumeViz


## Overview
PlumeViz features a Plumeria Python wrapper, a tool designed to streamline the batch processing and analysis of 1D volcanic plume simulations using Plumeria software. This wrapper automates the generation of input files, execution of simulations, and post-processing of results, making it easier to manage large sets of simulation runs and analyze their outputs efficiently.

**Auxiliary Modules.** 
This repository also includes auxiliary scripts for conducting single and bulk runs of Plumeria. These scripts use specific vent diameter values mapped to secondary values, such as maintaining a constant mass flux while varying external water content. Additionally, the scripts can calculate and visualize thermal energy at the vent, demonstrate how density changes by adding external water, and visualize ambient temperature and humidity using sample NOAA data.

## Features

- **Batch Processing**: Automate the generation and execution of multiple Plumeria simulations.
- **Data Analysis**: Extract and analyze key parameters from the simulation outputs.
- **Plotting Utilities**: Generate various plots to visualize the simulation results.
- **Flexible Configuration**: Easily adjust simulation parameters and directories.

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/elcarrillo/PlumeViz.git
    cd PlumeViz
    ```
2. **Create Virtual Environment**
    - It is **recommended** that you install in a virtual environment so as not to interfere with dependencies in other projects/workflow.
        ```bash
        python -m venv env
        ```
        #### On Windows
        ```bash
        .\env\Scripts\activate
        ```
        #### On macOS/Linux
        ```bash
        source env/bin/activate
        ```
3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    - The colormaps library is optional but provides scientific color mapping if desired.
4. **Set Up Plumeria**:
    - Ensure that the Plumeria software is installed and accessible on your system.
    - Update the `plumeria_loc` variable in the scripts to point to the correct location of the Plumeria executable.
    
## Directory Structure and Contents
```
PlumeViz/
├── README.md                                    # Project documentation
├── requirements.txt                             # List of dependencies
├── README.txt                                   # Additional project documentation
├── How to download and install Plumeria.docx    # Installation guide for Plumeria
├── wrappers/                                    # Directory containing wrapper scripts
│   ├── batch_extract_plumeria_output_MAIN.py
│   ├── batch_plumeria_input_bulk_MAIN.py
│   ├── batch_extract_plumeria_output_AUX.py
│   ├── batch_plumeria_input_bulk_AUX.py
│   ├── batch_vent_functions.py
│   ├── plumeria_single_run.py
│   └── input_parameters.py
├── main_plots/                                  # Directory containing main plotting scripts
│   ├── batch_plot_GRID.py
│   ├── batch_plume_plots.py
│   └── batch_dz_plots_all.py
├── sample_plots/                                # Directory containing sample plots
│   ├── sample.png
│   └── sample2.png
└── aux_plots/                                  # Directory containing aux plotting modules
    ├── 41683870_profile_Yellowstone.txt
    ├── atmospheric_plots.py
    ├── density_plots.py
    └── initial_thermal_energy.py
```

## Usage

### Configuration

Before running the wrapper, you need to configure the parameters for your simulations. The main configuration is done in the `main` function of the script:

- **Mass Fraction of Added Water**: `mass_frac_add_water_list`
- **Magma Temperature List**: `magma_temp_list`
- **Vent Velocity List**: `vent_vel_list`
- **Humidity List**: `humid_list`
- **Vent Diameter**: `min_vent_diameter`, `max_vent_diameter`, `interval_size`
- **Gas Fraction**: `gas_frac`
- **Sounding Data File**: `line11`
- **Directory Locations**: `dir_loc`, `out_loc`
- **CSV Path**: `csv_path`

### Running the Script

1. **Generate Input Files**:
    Modify and run the script `batch_plumeria_input_bulk_MAIN.py` script to generate the Plumeria simulations' input files.

2. **Run Simulations**:
    Execute the Plumeria simulations using the generated input files. This can be done manually or automated using a batch processing script.

3. **Process Outputs**:
    Use the `batch_extract_plumeria_output_MAIN.py` or similar scripts to process the simulation outputs and extract relevant data.

4. **Analyze and Plot Results**:
    Utilize the provided plotting scripts in **\main plots** directory to visualize the results of your simulations.
    
### Example

Here is a basic example of how to configure (using `input_parameters.py`) and run the wrapper:

```python
def main():
    # Configuration parameters
    mass_frac_add_water_list = [float(a / 100) for a in range(0, 21)]
    magma_temp_list = [900]
    vent_vel_list = [100]
    humid_list = [0]

    min_vent_diameter = 1
    max_vent_diameter = 44000
    interval_size = 6

    vent_diameter_list = binary_log_input(min_vent_diameter, max_vent_diameter, interval_size)

    gas_frac = 0.90
    line11 = 'NOAA_sounding_file.txt'

    dir_loc = 'plumeria_input_dir'
    out_loc = 'plumeria_output_dir'
    csv_path = 'plumeria_data.csv' ## extracted data will be saved here

    plumeria_loc = '/Users/carrile/plume_fort_v2.3.1/plumeria'

    os.makedirs(dir_loc, exist_ok=True)
    os.makedirs(out_loc, exist_ok=True)

if __name__ == "__main__":
    main()
```

###### sample figures:

![single run](sample%20plots/sample.png)
![bulk run](sample%20plots/sample2.png)

## Contributing

If you would like to contribute to the development of this wrapper, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Special thanks to the developer of the Plumeria software, Larry Mastin.
- Contributions from discussions with Liam Kelly, Kristen Fauria (the PI of the original research that prompted the need for this Python script), and Tushar Mittal.


## Plumeria Software Information

- Please see the references below for more details about the Plumeria software.
    - Mastin, L. G. (2007), A user-friendly one-dimensional model for wet volcanic plumes, Geochem. Geophys. Geosyst., 8, Q03014, doi:10.1029/2006GC001455.
    - Mastin, L. G. (2014), Testing the accuracy of a 1-D volcanic plume model in estimating mass eruption rate, J. Geophys. Res. Atmos., 119, 2474–2495, doi:10.1002/2013JD020604.
    - Mastin, L.G., (2024), plumeria_wd software.  U.S. Geological Survey software program.  https://doi.org/10.5066/P1HVRKVN
 
## Contact

For questions or support, please contact Edgar Carrillo at [edgarc.ec@gmail.com].
