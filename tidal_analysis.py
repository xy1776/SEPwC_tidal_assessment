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
    tide_data = pd.read_csv(filename,sep='\s+', header=None, skiprows=10)# 'sep='\s'tells pandas to use any whitespace (spaces, tabs, newlines) as a separator.
   
    #clean and convert "ASLVZZ01" column. 
    tide_data[4] = tide_data[4].astype(str).str.replace('M', '', regex=False).str.replace('N', '', regex=False) #Remove M and N
    tide_data[4] = tide_data[4].astype(str).str.replace('-99.0000', np.nan) #replace missing values
    tide_data[4] = pd.to_numeric(tide_data[4], errors='coerce') #convert to numeric
    
    # Rename colums
    tide_data = tide_data.rename(columns={1: 'Date', 2: 'Time', 4: 'Sea Level'})
    
    tide_data['Datetime'] = pd.to_datetime(tide_data['Date'] + ' ' + tide_data['Time'])
    tide_data = tide_data.set_index('Datetime')
    
    #drop unecessary columns
    tide_data = tide_data.drop(columns=[0, 3, 5])
    
    return tide_data
    
def extract_single_year_remove_mean(year, data):
   

    return 


def extract_section_remove_mean(start, end, data):


    return 


def join_data(data1, data2):

    return 



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
    


