#!/usr/bin/env python3
"""
This module provides functions for reading, manipulating, and analyzing tidal gauge 
including calculating long-term sea level trends and performing harmonic analysis
to extract tidal constituents.
"""

# import the modules you need here
import argparse
import datetime
from datetime import timedelta
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt #use for  generating figures
import numpy as np #The fundamental package for numerical computation in Python.
import uptide #A Python package specifically designed for tidal analysis and prediction.
from scipy.stats import linregress
import pytz

def read_tidal_data(filename):
    """ Function:read the tidal data form the txt file.
    
        Input-data the path to tidal data txt file. 
        Return-pandas.DataFrame: A DataFrame with a DatetimeIndex ('Datetime') and a
                          'Sea Level' column (as float).
    """
    # Add the data from different file.
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"Waring: File not found: {filename}.")

    # 'sep='\s'tells pandas to use any whitespace (spaces, tabs, newlines) as a separator.
    tide_data = pd.read_csv(filename,sep=r'\s+', header=None,skiprows=11)

    # Rename colums
    tide_data = tide_data.rename(columns={1: 'Date', 2: 'Time', 3: 'Sea Level', 4: 'Residual'})

    # Clean and convert 'Date' and 'Time' colums
    tide_data['Date'] = tide_data['Date'].astype(str).str.strip()
    tide_data['Time'] = tide_data['Time'].astype(str).str.strip()

    #clean and convert "ASLVZZ01" and 'Residual' column.
    for col in ['Sea Level', 'Residual']:
        tide_data[col] = tide_data[col].astype(str).str.replace('M', '', regex=False)
        tide_data[col] = tide_data[col].astype(str).str.replace('N', '', regex=False)
        tide_data[col] = tide_data[col].replace('-99.0000', np.nan)
        tide_data[col] = pd.to_numeric(tide_data[col], errors='coerce')

    #creat 'Datetime' column.
    tide_data['Datetime'] = pd.to_datetime(tide_data['Date'].str.strip() + ' ' + \
                                           tide_data['Time'].str.strip(), \
                                               format='%Y/%m/%d %H:%M:%S')

    #set 'Datetime' as index
    tide_data = tide_data.set_index('Datetime')
    #drop unecessary columns
    tide_data = tide_data.drop(columns=[0])

    return tide_data[['Sea Level', 'Time']]

def extract_single_year_remove_mean(year, data):
    """ Function: extract single year's data and remove the mean. 
    
        Input: year and data
        Return: A new Pandas DataFrame containing: A DatetimeIndex spanning the
                entirety of the specified year based on the data available for that year.
    """
    year_string_start = str(year)+"0101"
    year_string_end = str(year)+"1231"
    year_data = data.loc[year_string_start:year_string_end, ['Sea Level']]

    #remove mean
    mmm = np.mean(year_data['Sea Level'])
    year_data['Sea Level'] -=mmm

    return year_data

def extract_section_remove_mean(start, end, data):
    """ Function: extract data within a period of time and remove the mean.

        Input: start time, end time and data
        Return: Anew Pandas DataFrame containing: A DatetimeIndex spanning the 
            entirety of the specified period of time based on the data available 
            for that time. 
    """
    # select the time range, start:YYYY/MM/DD/00:00:00, end:YYYY/MM/DD/00:00:00
    start_datetime = pd.to_datetime(start)
    end_datetime = pd.to_datetime(end)
    #add 23 hour make sure the end time for the calculation was YYYY/MM/DD 23:00:00.
    end_datetime += timedelta(hours=23)

    section_data = data.loc[start_datetime:end_datetime, ['Sea Level']]

    #calculated the mean and remove it
    mmm = np.mean(section_data['Sea Level'])
    section_data['Sea Level'] -=mmm

    return section_data

def join_data(data1, data2):
    """ Function: joins two tidal data DataFrames. 

    Input:data1 and data2 
    Return: pd.DataFrame: A new DataFrame containing the joined data, 
            or None if either input is None.
        
    """
    if data1 is None or data2 is None:
        print("[join_data] One or both input datasets are None")
        return None
    if not isinstance(data1, pd.DataFrame) or not isinstance(data2, pd.DataFrame):
        print("[join_data] One or both inputs area not vlid DataFrames")
        return None

    combined = pd.concat([data1, data2])
    combined = combined[~combined.index.duplicated(keep='first')]
    combined = combined.sort_index()
    return combined

def sea_level_rise(data):
    """ Function: calculating and show the figure for the long_term trend in sea level.
    
        Input: Time series data for 'Sea Level'
        Return: The slop and linear trend line. 
    """
    plot_data = data.copy()

    #Drop Sea level is NaN
    plot_data = plot_data.dropna(subset=['Sea Level'])

    # ensure data was joined by time order
    plot_data = plot_data.sort_index()

    print(plot_data['Sea Level'].describe())

    #creat a time valu for liner regression (m/hour)
    time_deltas = plot_data.index - plot_data.index[0]
    time_hour = time_deltas.total_seconds() / 3600

    #linear regression
    slope, intercept, _, p_value, _= linregress(time_hour, plot_data['Sea Level'])
    trend_line = slope*time_hour + intercept
    print("Slope:", slope)

    #seting for figures.
    fig_sea_level=plt.figure()
    ax=fig_sea_level.add_subplot(111)
    ax.plot(plot_data.index, plot_data['Sea Level'], color="blue", lw=1,
            label="Sea Level Data for Aberdeen(m)")
    ax.plot(plot_data.index, trend_line, color="red", linestyle='-', lw=1,
            label=f"Long_term Trend({slope:.2e} m/hour)")
    ax.set_xlabel("Datetime")
    ax.set_ylabel("Sea Level (m)")
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    ax.set_xlim(plot_data.index.min(), plot_data.index.max())
    ax.set_title("Sea Level Trend Analysis (m/hour)")

    # fig_Sea_Level.tight_layout()
    # plt.show() #

    return slope, p_value

def tidal_analysis(data, constituents, start_datetime):
    """Function: To perform a harmonic analysis on a given time series of sea level 
                data to extract the amplitude and phase of specified tidal constituents.
        
        Input: data-A DataFrame containing the 'Sea Level' time series to be analyzed.
               constituents-A list of tidal consituents for which amplitudes 
               and phases are to be calculated.
               start_datetime-the starting datetime of the data segment being analyzed. 
        Return:amplitudes-A dictionary where keys are the constituent names (e.g., 'M2', 'S2') 
               and values are their calculated amplitudes. 
               phases-A dictionary where keys are the constituent names and values are
               their calculated phases. 
    """
    if isinstance(start_datetime, str):
        start_datetime = datetime.datetime.fromisoformat(start_datetime)

    # Ensure start datetime is UTC
    if start_datetime.tzinfo is None:
        start_datetime = start_datetime.replace(tzinfo=pytz.UTC)
    else:
        start_datetime = start_datetime.astimezone(pytz.UTC)

    # Creat a copy
    data_cleaned = data.copy()

    # Change the timezone into UTC
    if data_cleaned.index.tz is None:
        data_cleaned.index = data_cleaned.index.tz_localize(pytz.UTC, ambiguous= 'NaT', \
                                                            nonexistent= 'NaT')
    else:
        data_cleaned.index = data_cleaned.index.tz_convert(pytz.UTC)

    # Handle NaN values
    initial_len = len(data_cleaned)
    data_cleaned.dropna(subset=['Sea Level'], inplace=True)
    if len(data_cleaned) < initial_len:# check the data after cleaned
        print(f"Removed {initial_len - len(data_cleaned)} rows with NaN values in 'Sea Level'.")
    if data_cleaned.empty:
        print("Error: After remobing NaNs, the data segment is empty")
        return {}, {}
    # Extract sea level and convert time index to seconds
    sea_level = data_cleaned['Sea Level'].to_numpy()
    times_64 = data_cleaned.index.to_numpy(dtype='datetime64[ns]')
    start_time_ns = np.datetime64(pd.Timestamp(start_datetime), 'ns')
    times_seconds = (times_64 - start_time_ns).astype('timedelta64[s]').astype(float)

    # Set up tidal analysis
    tide_obj = uptide.Tides(constituents)
    tide_obj.set_initial_time(start_datetime)
    amplitude, phases = uptide.harmonic_analysis(tide_obj, sea_level, times_seconds)

    return amplitude, phases

def get_longest_contiguous_data(data):
    """ Function: Identify and extract the longest continuous block of 'Sea Level' data
                from the DataFrame. 
        
        Input: A DataFrame, expected to have a DatetimeIndex and at least a 'Sea Level'
                column. This DataFrame might contain gaps (NaNs) or unevenly spaced data.
        Return: A new DataFrame containing only the 'Sea Level' column, representing the
        longest contiguous block of valid data. 
    """
    # Ensure the timezone is UTC
    if data.index.tz is None:
        data = data.tz_localize(pytz.UTC, ambiguous='NaT', nonexistent='NaT')
    else:
        data = data.tz_convert(pytz.UTC)

    #use the copy to aboid modifying the original DataFrame
    valid_data = data.copy()
    valid_data['Sea Level'] = pd.to_numeric(valid_data['Sea Level'], errors='coerce')
    valid_data = valid_data.dropna(subset=['Sea Level'])

    # Assumes the data should be hourly, identify gaps.
    expected_interval = pd.Timedelta(hours=1)
    # Calculate the difference between consecutive timestamps
    time_diffs = valid_data.index.to_series().diff()
    # Identify where the time difference is greater than expected_intercal
    breaks = (time_diffs > expected_interval + pd.Timedelta(seconds=1)).fillna(False)
    # Each time the break happend, the ID increments
    block_ids = breaks.cumsum()
    # Find the size of each block based on the ID
    block_sizes = valid_data.groupby(block_ids).size()
    # Find the ID of the longest block
    longest_block_id = block_sizes.idxmax()
    # Extract the longest segment
    longest_segment = valid_data[block_ids == longest_block_id][['Sea Level']]

    return longest_segment

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                     prog="UK Tidal analysis",
                     description="Calculate tidal constiuents and RSL from tide gauge data",
                     epilog="Copyright 2024, Jon Hill"
                     )

    parser.add_argument("directory",
                    help="the directory containing txt files with data")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args()
    dirname = args.directory
    verbose = args.verbose

    print(f"Start analysis for directory: {dirname}")
    print(f"DEBUG: Contents of directory {dirname}: {os.listdir(dirname)}")

    all_data_frames = []# Creat empty list.
    FILE_COUNT = 0

    if not os.path.isdir(dirname):
        print(f"Error: The directory '{dirname}' does not exist. Exiting.")
        sys.exit(1)

    # Loop through files in the directory.
    for filename_loop in os.listdir(dirname):
        if filename_loop.lower().endswith('.txt'):
            filepath = os.path.join(dirname, filename_loop)
            if verbose:
                print(f"Attempting to read file: {filepath}")
            individual_file_data = read_tidal_data(filepath)
            #debug
            if individual_file_data.empty:
                print(f"DEBUG: {filepath} returened an Empty DataFrame.")
            else:
                print(f"DEBUG: {filepath} successfully read. First row: {individual_file_data.head(1)}")

            if not individual_file_data.empty:
                all_data_frames.append(individual_file_data)
                FILE_COUNT += 1
            else:
                if verbose:
                    print(f"No data extracted form {filepath}.")
    if FILE_COUNT == 0:
        print("No .txt data files found or successfully processed in the directory.")
        sys.exit(1)

    # Combine the data
    full_tidal_dataset = pd.concat(all_data_frames).sort_index()

    if full_tidal_dataset.empty:
        print("No tidal data collected after combined all files.")
        sys.exit(1)
    if verbose:
        print("Successfully read and joined data from all files.")
