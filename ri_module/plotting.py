from src.data_processing import reduce_dataframe
from src.constants import COLUMNS, PLOT_PARAMS
import matplotlib.pyplot as plt
import seaborn as sns

def plot_data(dataframes, ri_to_plot, save_plots=False, output_path='sample.png'):
    """Generate plots for the processed data.

    Args:
        dataframes (list): List of DataFrames to reduce and plot.
        ri_to_plot (str): Column name for the x-axis (e.g., "ri" or "thermal_ri").
        save_plots (bool): If True, save the plot; otherwise, display it.
        output_path (str): File path for saving the plot.
    """
    # Reduce DataFrames for plotting
    dataframes_reduced = [reduce_dataframe(df) for df in dataframes]

    # Update plot parameters
    plt.rcParams.update(PLOT_PARAMS)
    f, ax = plt.subplots(figsize=[8, 8])

    # Define plot styles
    colors = ['black', 'mediumblue', 'cornflowerblue']
    linestyles = ['solid', 'dashed', 'dotted']
    labels = [
        ('u = 75 m/s', [700, 900, 1100]),
        ('u = 100 m/s', [700, 900, 1100]),
        ('u = 125 m/s', [700, 900, 1100]),
    ]

    # Plot each dataset with the corresponding style
    for idx, (color, (velocity_label, temps)) in enumerate(zip(colors, labels)):
        for temp_idx, temp in enumerate(temps):
            linestyle = linestyles[temp_idx]
            label = f'{velocity_label}, T = {temp} °C'
            sns.lineplot(
                data=dataframes_reduced[idx * len(temps) + temp_idx],
                x=ri_to_plot,
                y=COLUMNS["external_water"],
                color=color,
                linestyle=linestyle,
                sort=True,
                orient='y',
                label=label,
            )

    # Customize axes
    xlabel = "Thermal Richardson Number" if ri_to_plot == COLUMNS["thermal_ri"] else "Richardson Number"
    ax.set(xlabel=xlabel, ylabel='Mass Fraction of External Water', xscale='log')
    ax.minorticks_on()
    plt.legend(loc=0, frameon=False)

    # Save or display the plot
    if save_plots:
        plt.savefig(output_path, bbox_inches="tight")
        print(f"Plot saved to {output_path}.")
    else:
        plt.show()
