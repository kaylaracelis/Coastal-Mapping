import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
from datetime import datetime
import pytz 
import os
from lineplot import * 

from satelliteDataJuly import *

def main(): 
    
    #create dataframes 
    ping_file_path = '/Users/kaylaracelis/Downloads/T6178194B_RSSI(in).csv'   
    angle_file_path = '/Users/kaylaracelis/Downloads/T6178194B_Bearing(in).csv'

    angle_df = read_csv_to_df(angle_file_path)
    ping_df = read_csv_to_df(ping_file_path)

    #convert UTC to pacific. 
    angle_df['TimeFramePacific'] = angle_df['TimeFrame'].apply(convert_utc_to_pacific)
    ping_df['TimeFramePacific'] = ping_df['TimeFrame'].apply(convert_utc_to_pacific)

    #print(ping_df)
    
    for column_name in ping_df.columns[1:]:
        value = count_column_values(ping_df, column_name) 
        print(f"{column_name} total: {value}\n") 

    # create_station_boxplot(ping_df, "RSSI")
    # create_station_boxplot(angle_df, "Angle_(Degrees)") 
    create_stacked_histogram(ping_df, "RSSI")
    create_stacked_histogram(angle_df, "Angle_(Degrees)")
    # create_line_plot(ping_df, angle_df)

    create_station_boxplot_with_obs(ping_df, "RSSI")
    create_station_boxplot_with_obs(angle_df, "Angle(Degrees)")

def save_plot(plot, title, folder_path='/Users/kaylaracelis/Downloads/NIWCII/'): 
    # Ensure the plot directory exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    if hasattr(plot, 'fig'):  # For FacetGrid
        plot.fig.suptitle(title)
        plot.fig.savefig(f"{folder_path}{title}.png", bbox_inches='tight')
    else:  # For standard Axes
        plt.title(title)
        plot.figure.savefig(f"{folder_path}{title}.png", bbox_inches='tight')
    
    plt.show()


def create_stacked_histogram(df, plot_type): 
    # Identify columns representing stations
    station_columns = [col for col in df.columns if col.startswith('V')]

    # Melt the DataFrame to long format for easier plotting
    df_melted = pd.melt(df, id_vars=['TimeFrame', 'TagId'], value_vars=station_columns,
                        var_name='Station', value_name='Value')
    
    # Print the first few rows of the melted DataFrame for debugging
    print(df_melted.head())

    # Filter out NaN values
    df_melted = df_melted.dropna(subset=['Value'])

    print("DataFrame after dropping NaN Values")
    print(df_melted.head())
    
    # Bin RSSI values if plot_type is RSSI
    if plot_type.lower() == 'rssi':
        df_melted = bin_rssi_values(df_melted)
        if df_melted is None: 
            print("bin_rssi_values returned None")
        else: 
            print("DataFrame after binning Rssi Values")
            print(df_melted.head())
        hue_column = 'Binned Value'
    else:
        hue_column = 'Value'

    df_melted['Station'] = df_melted['Station'].astype('category')

    # Create the stacked histogram using countplot
    plt.figure(figsize=(12, 6))
    plot = sns.histplot(
        data=df_melted,
        x='Station', hue=hue_column,
        palette='viridis',
        multiple = 'stack',
        edgecolor='.3',
        linewidth=.5
    )

    plt.title(f'Stacked Histogram of {plot_type}')
    plt.xlabel('Station')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    
    handles, labels = plt.gca().get_legend_handles_labels()
    if not handles: 
        print("No legend handles found. Ensure the 'hue' parameter is correctly used...")
    else: 
        labels = [f'Value: {label}' for label in labels]  # Add 'Value' prefix to distinguish from 'Station'
        plt.legend(handles, labels, title=f'{plot_type}', loc='upper right', fontsize='medium')

    plt.tight_layout()
    save_plot(plot, f"{plot_type}_Stacked_Histogram")

#///

def bin_rssi_values(df_melted): 
    #ensure value col is numeric 
    df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors = 'coerce')

    #drop rows where value is still nan after conversion 
    df_melted = df_melted.dropna(subset=['Value']) 

    #define bin edges for rssi values 
    # // takes the lower boundary. * 5 to make it a lower multiple of 5 +10 to create the upper boundary above max value
    bin_edges = np.arange(int(df_melted['Value'].min() // 5) * 5, int(df_melted['Value'].max() // 5) * 5 + 10, 5)

    #create binned values 
    df_melted['Binned Value'] = pd.cut(df_melted['Value'], bins = bin_edges, include_lowest = True, labels = bin_edges[:-1]) 

    return df_melted


def create_station_boxplot(df, type): 
    # Get columns 
    station_columns = df.columns[df.columns.str.startswith('V30')]
    
    # Melt the dataframe to long format for easier plotting 
    df_melted = pd.melt(df, id_vars=['TimeFrame', 'TagId'], value_vars=station_columns, 
                        var_name='Station', value_name='Value')

    plt.figure(figsize=(12, 6))
    plot = sns.boxplot(x='Station', y='Value', data=df_melted)

    # Add a custom legend
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label=f'{type}')]
    plt.legend(handles=handles, title='Legend', loc='upper right')

    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Station (TagID)')
    plt.ylabel(type)
    plt.tight_layout()
    save_plot(plot, f"{type}_boxplot")

#create box plot with observations 
def create_station_boxplot_with_obs(df, type): 
    # Get columns 
    station_columns = df.columns[df.columns.str.startswith('V30')]
    
    # Melt the dataframe to long format for easier plotting 
    df_melted = pd.melt(df, id_vars=['TimeFrame', 'TagId'], value_vars=station_columns, 
                        var_name='Station', value_name='Value')

    plt.figure(figsize=(12, 6))
    sns.set_theme(style="ticks")
    ax = plt.gca()

    # Plot the horizontal boxplot
    plot = sns.boxplot(y='Station', x='Value', data=df_melted, orient='h', ax=ax)

    # #scatter plot with custom jitter #    DOESNT WORK! WILL JUST EXIT THE PROGRAM WITHOUT GENERATING A PLOT.. 
    # sns.scatterplot(x='Value_Jitter', y='Station_Jitter', data=df_jittered, size=6, color=".3", alpha=0.5, marker='o', ax=ax)

    # Add in points to show each observation with jitter and transparency
    sns.stripplot(y='Station', x='Value', data=df_melted, size=4, color=".3", linewidth=0, ax=ax,
                  jitter=0.3, alpha=0.2, marker='o')

    # Add a custom legend
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label=f'{type} of reading')]
    plt.legend(handles=handles, title='Legend', loc='upper right')

    plt.xlabel(type)
    plt.ylabel('Station (TagID)')
    plt.tight_layout()
    save_plot(plot, f"{type}_boxplot")

# UNUSED jitter function
# def add_jitter(df, x_jitter = 0.): 
#     df['Value_Jitter'] = df['Value'] + np.random.uniform(-x_jitter, x_jitter, size = len(df)) 
#     return df


def count_column_values(df, column_name): 
    if column_name not in df.columns: 
        raise ValueError(f"column {column_name} doesnt exist ")
    
    total_values = df[column_name].count()
    return total_values

if __name__ == "__main__": 
    main()