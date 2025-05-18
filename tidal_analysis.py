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
    
        Input-data the tidal data txt file. 
        Returen-A DataFrame with a DatetimeIndex ('Date') and a
                'Sea Level' column (as float). Returns None if the
                file is not found.
    """
    tide_data = pd.read_csv(filename,sep='\s+', header=None)# 'sep='\s'tells pandas to use any whitespace (spaces, tabs, newlines) as a separator.
    tide_data['Date'] = pd.to_datetime(dict(year=tide_data[0], month=tide_data[1], day=tide_data[2], hour=tide_data[3]))
    # 0 is year, 1 is month, 2 is day, 3 is time. 
    tide_data = tide_data.drop([0,1,2,3], axis = 1)
    tide_data = tide_data.rename(columns={4: "Tide"})
    
    # Replace 'M', 'N', 'T' with NaN in the 'Tide' cloumn. 
    tide_data.replace(to_replace="^M$", value=np.nan, regex=True, inplace=True)
    tide_data.replace(to_replace="^N$", value=np.nan, regex=True, inplace=True)
    tide_data.replace(to_replace="^T$", value=np.nan, regex=True, inplace=True)
    
    tide_data = tide_data.set_index('Date')
    tide_data = tide_data.mask(tide_data['Tide'] < -300)
    # handle potentially erroneous or out-of-range tide readings.
    
    return 0
    
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
    


