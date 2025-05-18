#!/usr/bin/env python3

# import the modules you need here
import argparse
import pandas as pd #useful for reading, manipulating, and analyzing tabular data, like CSV files or time series.
import matplotlib.pyplot as plt #use for  generating figures
import datetime #use for create , manipulate and format data and time objects
import os # use for interacting with the file system - check files path
import numpy as np #The fundamental package for numerical computation in Python.
import uptide #A Python package specifically designed for tidal analysis and prediction.
import math #Includes functions for arithmetic operations, logarithms, trigonometric functions, etc.
import pytz #A library for working with time zones in Python.

def read_tidal_data(filename):
    """ Function:read the tidal data form the txt file.
    
        Input-data the path to tidal data txt file. 
        Returen-pandas.DataFrame: A DataFrame with a DatetimeIndex ('Datetime') and a
                          'Sea Level' column (as float). Returns None if the
                          file is not found or an error occurs.
    """
    tide_data = pd.read_csv(filename,sep='\s+', header=None, skiprows=11)# 'sep='\s'tells pandas to use any whitespace (spaces, tabs, newlines) as a separator.
   
    #clean and convert "ASLVZZ01" and 'Residual' column. 
    for col in [3, 4]:
        tide_data[col] = tide_data[col].astype(str).str.replace('M', '', regex=False).str.replace('N', '', regex=False)
        tide_data[col] = tide_data[col].replace('-99.0000', np.nan)
        tide_data[col] = pd.to_numeric(tide_data[col], errors='coerce')
    
    # Rename colums
    tide_data = tide_data.rename(columns={1: 'Date', 2: 'Time', 3: 'Sea Level', 4: 'Residual'})
    
    #creat 'Datetime' column and set as index 
    tide_data['Datetime'] = pd.to_datetime(tide_data['Date'].str.strip() + ' ' + tide_data['Time'].str.strip(), format='%Y/%m/%d %H:%M:%S')
    tide_data = tide_data.set_index('Datetime')
    
    #drop unecessary columns
    tide_data = tide_data.drop(columns=[0])
    
    return tide_data
    
def extract_single_year_remove_mean(year, data):
    """ Function: extract single year's data and remove the mean. 
    
        Input: year and data
        Returen: A new Pandas DataFrame containing: A DatetimeIndex spanning the
                entirety of the specified year 
                based on the data available for that year.
    """
    year_start_str = f'{year}-01-01'
    year_end_str = f'{year}-12-31'
    
    year_start = pd.to_datetime(year_start_str)
    year_end = pd.to_datetime(year_end_str)
    try: 
        year_data = data.loc[year_start:year_end, ['Sea Level']].copy()
    except KeyError:
        print("Error: 'Sea Level' column not found in the input DataFrame.")
        return None
    except AttributeError:
        print("Error: Input 'data' is not a valid Pandas DataFrame.")
        return None
    
    #calculated the mean of 'Sea Level', excluding NaN 
    tide_mean = year_data ['Sea Level'].mean(skipna=True)
    
    #Impute NaN values with the calculated mean
    year_data['Sea Level'] = year_data['Sea Level'].fillna(tide_mean)
    
    #Substract the mean from the imputed data
    year_data['Sea Level'] -= tide_mean

    return year_data

def extract_section_remove_mean(start, end, data):


    return 


def join_data(data1, data2):
    """ Function: joins two tidal data DataFrames. 

    Input:data1 and data2 
    Returen: pd.DataFrame: A new DataFrame containing the joined data, 
            or None if either input is None.
        
    """
    if data1 is None or data2 is None:
        print("[join_data] One or both input datasets are None")
        return None
    if not isinstance(data1, pd.DataFrame) or not isinstance(data2, pd.DataFrame):
        print("[join_data] One or both inputs area not vlid DataFrames")
        return None
    try:
        combined = pd.concat([data1, data2])
        combined = combined[~combined.index.duplicated(keep='first')]
        combined = combined.sort_index()
        return combined
    
    except Exception as e:
        print(f"[join_data] Error while joining data:{e}")
        return None
    
def sea_level_rise(data):

                                                     
    return 

def tidal_analysis(data, constituents, start_datetime):


    return 

def get_longest_contiguous_data(data):


    return 

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
    


