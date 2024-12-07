import pandas as pd
import numpy as np
import os
from src.constants import COLUMNS


def load_data(input_file_path):
    """Load and clean the dataset.

    Args:
        input_file_path (str): Path to the input CSV file.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"File not found: {input_file_path}")
    
    try:
        df = pd.read_csv(input_file_path)
    except Exception as e:
        raise RuntimeError(f"Error reading file {input_file_path}: {e}")
    
    # Drop NaN values in the vent diameter column and reset the index
    df = df.dropna(subset=[COLUMNS["vent_diameter"]]).reset_index(drop=True)
    return df


def filter_data(df, velocity, temperature, water_upper_limit=None, exclude_water=None):
    """Filter data based on velocity, temperature, and water conditions.

    Args:
        df (pd.DataFrame): Input DataFrame.
        velocity (float): Initial velocity condition.
        temperature (float): Magma temperature condition.
        water_upper_limit (float, optional): Upper limit for water fraction. Defaults to None.
        exclude_water (list, optional): List of water fractions to exclude. Defaults to None.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    if not isinstance(velocity, (int, float)):
        raise ValueError("Velocity must be a number.")
    if not isinstance(temperature, (int, float)):
        raise ValueError("Temperature must be a number.")
    if exclude_water and not isinstance(exclude_water, list):
        raise ValueError("exclude_water must be a list of values.")
    
    query = (
        (df[COLUMNS["initial_velocity"]] == velocity)
        & (df['magma temperature (c)'] == temperature)
    )
    if water_upper_limit:
        query &= df[COLUMNS["external_water"]] < water_upper_limit
    if exclude_water:
        query &= ~df[COLUMNS["external_water"]].isin(exclude_water)
    return df.loc[query]


def ri_borders(df_condition, water_fraction):
    """Identify Ri borders based on plume height changes.

    Args:
        df_condition (pd.DataFrame): Filtered DataFrame for specific conditions.
        water_fraction (float): External water fraction value.

    Returns:
        pd.Index: Indices of rows meeting the Ri border condition.
    """
    if df_condition.empty:
        return pd.Index([])  # Return an empty index if the input DataFrame is empty

    df_w = df_condition.loc[df_condition[COLUMNS["external_water"]] == water_fraction]
    if df_w.empty:
        return pd.Index([])  # Handle cases where no rows match the water fraction

    # Sort by mass flux and calculate absolute differences in plume height
    df_w = df_w.sort_values(by=[COLUMNS["mass_flux"]]).copy()
    df_w['diff'] = df_w[COLUMNS["plume_height"]].diff().abs()
    std_dev = np.std(df_w['diff'].dropna())

    try:
        temp = df_w['magma temperature (c)'].iloc[0]
        velocity = df_w[COLUMNS["initial_velocity"]].iloc[0]
    except IndexError:
        return pd.Index([])  # Handle cases where accessing the first element fails

    # Define thresholds based on water fraction and conditions
    if water_fraction >= 0.3:
        threshold = 6 * std_dev
    elif water_fraction >= 0.3 and temp == 700 and velocity == 75:
        threshold = 10 * std_dev
    elif water_fraction < 0.3 and 1000 < temp < 1100 and velocity > 100:
        threshold = 1.5 * std_dev
    elif water_fraction < 0.3 and temp == 1000 and velocity == 125:
        threshold = 3 * std_dev
    else:
        threshold = 8 * std_dev

    return df_w[df_w['diff'] > threshold].index


def reduce_dataframe(df):
    """Reduce DataFrame to unique rows.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Reduced DataFrame with unique rows based on conditions.
    """
    # Filter rows with high water fraction
    high = df[df[COLUMNS["external_water"]] > 0.4]
    
    # Filter rows with low water fraction, sorted by mass flux
    low = df[df[COLUMNS["external_water"]] <= 0.4].sort_values(by=[COLUMNS["mass_flux"]])
    
    # Concatenate unique rows from high and low subsets
    combined = pd.concat([
        high.drop_duplicates(subset=COLUMNS["external_water"]),
        low.drop_duplicates(subset=COLUMNS["external_water"]),
    ])
    return combined.reset_index(drop=True)
