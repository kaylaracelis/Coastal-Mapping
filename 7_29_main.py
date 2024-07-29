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


    # #************* FILE IMPORTS FOR COASTLINE, PING, AND ANGLE DATA ****************** 

     coastline = readFile('/Users/kaylaracelis/Downloads/N30W120 (2)/N30W120.shp')

    # #create and plot antenna stations 
     stations = createAntennaStations()
     abbreviations = createAbbreviations()

    # #import file with pings (RSSI) and angles (bearings)
     ping_file_path = '/Users/kaylaracelis/Downloads/T6178194B_RSSI(in).csv'   
     angle_file_path = '/Users/kaylaracelis/Downloads/T6178194B_Bearing(in).csv'

     angle_df = read_csv_to_df(angle_file_path)
     ping_df = read_csv_to_df(ping_file_path)

    # #convert utc to pacific 
     angle_df['TimeFramePacific'] = angle_df['TimeFrame'].apply(convert_utc_to_pacific)
     ping_df['TimeFramePacific'] = ping_df['TimeFrame'].apply(convert_utc_to_pacific)

    #*************** CREATE FRAME *********************
    # # Create Base Map 
     fig, ax = create_basemap(coastline, stations, abbreviations)

    # # TEST RUN WITH ONE TIMEFRAME (works) [4722]
     row = angle_df.iloc[4722] 

     create_frame(row, stations, ax) 
     save_frame(fig, row['TimeFramePacific']) 

     filename = f'/Users/kaylaracelis/Downloads/NIWCII/testframe.png'
     plt.savefig(filename)
     plt.show()
     plt.close(fig)

    # CREATE ANIMATION 
    #folder_path = '/Users/kaylaracelis/Downloads/NIWCII/FRAMES'
    #output_path = '/Users/kaylaracelis/Downloads/NIWCII/animation1.mp4'

    #rename_files(folder_path)

    #print("done renaming files\n")

    #print("creating animation\n")

    #create_animation(folder_path)

    #print("Done\n")


     return 0

if __name__ == "__main__": 
    main()