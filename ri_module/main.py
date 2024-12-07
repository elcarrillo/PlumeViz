from data_processing import load_data, filter_data, reduce_dataframe, ri_borders
from plotting import plot_data
from constants import COLUMNS
import pandas as pd 

# Define file paths
INPUT_PATH = '../data/input/plumeria_data.csv'
OUTPUT_PATH = '../data/output/collapse_conditions.csv'

def main():
    """Main script to process data, save output, and generate plots."""
    # Load data
    print("Loading data...")
    df = load_data(INPUT_PATH)
    print("Data loaded successfully.")

    # Define conditions
    velocities = [75, 100, 125]
    temperatures = [700, 900, 1100]
    water_fractions = [w / 100 for w in range(61)]  # 0.00 to 0.60 in increments of 0.01

    # Identify Ri borders and collect results
    print("Identifying Ri borders...")
    selected_rows = []
    for vel in velocities:
        for temp in temperatures:
            df_condition = filter_data(df, vel, temp)
            if df_condition.empty:
                continue
            for water_fraction in water_fractions:
                change_points = ri_borders(df_condition, water_fraction)
                if not change_points.empty:
                    selected_rows.append(df_condition.loc[change_points])

    # Combine and save selected rows
    if selected_rows:
        result_df = pd.concat(selected_rows).reset_index(drop=True)
        result_df.to_csv(OUTPUT_PATH, index=False)
        print(f"Collapse conditions saved to {OUTPUT_PATH}.")
    else:
        print("No Ri borders found.")
        result_df = None

    # Prepare data for plotting
    if result_df is not None:
        print("Reducing data for plotting...")
        data_frames = [
            reduce_dataframe(filter_data(result_df, vel, temp))
            for vel in velocities for temp in temperatures
        ]
        print("Data reduction complete.")

        # Generate plots
        print("Generating plots...")
        plot_data(data_frames, COLUMNS["ri"], save_plots=False)
        print("Plots generated successfully.")
    else:
        print("No data to plot.")

if __name__ == "__main__":
    main()
