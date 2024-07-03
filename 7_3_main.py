import geopandas as gpd                     #IMPORTS FOR COASTLINE PLOT
import os
import contextily as ctx
import matplotlib.pyplot as plt
from shapely.ops import unary_union 
from shapely.geometry import box, MultiPolygon, Point, Polygon
from coastlinePlot import *

import csv                                  #IMPORTS FOR SATELLITE DATA 
import pytz
from datetime import datetime
from satelliteDataJuly import * 

import geopandas as gpd                     #IMPORTS FOR TRI-ANIMATION
from shapely.geometry import Point, LineString 
import math 
from trianimation import *


def main(): 


    #************* FILE IMPORTS FOR PING AND ANGLE DATA ****************** 

    coastline = readFile('NIWC/socal_mapping/data/N30W120.shp')

    #create and plot antenna stations 
    stations = createAntennaStations()
    abbreviations = createAbbreviations()

    #import file with pings (RSSI) and angles (bearings)
    ping_file_path = '/Users/kaylaracelis/Downloads/T6178194B_RSSI(in).csv'   
    angle_file_path = '/Users/kaylaracelis/Downloads/T6178194B_Bearing(in).csv'

    angle_df = read_csv_to_df(angle_file_path)
    ping_df = read_csv_to_df(ping_file_path)

    #convert utc to pacific 
    angle_df['TimeFramePacific'] = angle_df['TimeFrame'].apply(convert_utc_to_pacific)
    ping_df['TimeFramePacific'] = ping_df['TimeFrame'].apply(convert_utc_to_pacific)

    #*********** PRINT DATATABLES TO TXT ********************************
    # this part is kinda broken right now but it's not my main priority 
    # so I'm going to leave it broken for now and fix it if I need to later. 

    #output_file = '7_1Summary.txt'

    #print_to_text_file(ping_df, angle_df, output_file)
    #print_ping_summary(ping_df, output_file)
    #print(angle_df)

    #print(f"Data and summary printed to {output_file}")

    #*************** CREATE FRAME *********************
    # # Create Base Map 
    fig, ax = create_basemap(coastline, stations, abbreviations)

    # #  TEST RUN (works)
    # line = create_line_angle(stations['V30B0154CF14'], 90)
    # graph_signal(ax, line)
    # displayPlot(ax, 'coastal_map.svg')
    # plt.show()

    # # TEST RUN WITH WHOLE TIMEFRAME (works)
    # row = angle_df.iloc[1] 
    # create_frame(row, stations, ax) 
    # save_frame(fig, row['TimeFramePacific'])
    # plt.show()
    # plt.close(fig)

    # # DOWNLOAD ALL FRAMES INTO FOLDER ! (don't work)
    create_image_frames(angle_df, coastline, stations, abbreviations)
    #please work 


    return 0

if __name__ == "__main__": 
    main()