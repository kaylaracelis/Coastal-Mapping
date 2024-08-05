import pandas as pd 
import numpy as np
import csv
from datetime import datetime
import pytz 

#USING DATAFRAMES 

#reads file into dataframe
def read_csv_to_df(file_path):
    df = pd.read_csv(file_path)
    return df

#converts time into pacific 
def convert_utc_to_pacific(utc_time_str):
    
    # Define UTC and Pacific time zones
    utc_zone = pytz.timezone('UTC')
    pacific_zone = pytz.timezone('US/Pacific')

    if isinstance(utc_time_str, str): 
        try: 
            utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
            #convert 
            return utc_time.strftime("%y-%m-%d %H:%M:%S: Pacific Time")
        except ValueError: 
            return utc_time_str


def count_pings_per_timeframe(data): 
    headers = data.columns.tolist()

    #get time frame header and data 
    time_frame_header = headers[0]
    time_frames = data[time_frame_header]

    #determine the number of rows in the dataframe 
    num_rows = len(data) 

    ping_summary = []

    columns_to_check = headers[2:] 

    for i in range(num_rows): 
        time_frame = time_frames.iloc[i] #access time frame value at index
        ping_count = 0

        for column in columns_to_check: 
            value = data[column].iloc[i] #acces value in row i of the current col

            #check if the value is numeric 
            if pd.api.types.is_numeric_dtype(data[column]): 
                ping_count += 1

        if ping_count > 1: 
            ping_summary.append((time_frame, ping_count))
    
    return ping_summary

def print_ping_summary(data, output_file): 
   ping_summary = count_pings_per_timeframe(data) 

   with open(output_file, mode = 'a', encoding ='utf-8') as file: 
       file.write("\n\nPing Summary: \n")
       for time_frame, ping_count in ping_summary: 
           file.write(f"{time_frame} - {ping_count} pings\n") 
