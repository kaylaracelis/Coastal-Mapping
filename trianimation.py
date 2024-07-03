import geopandas as gpd                     #IMPORTS FOR TRI-ANIMATION
from shapely.geometry import Point, LineString 
import math 

import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation 
import numpy as np
import time 

import geopandas as gpd                     #IMPORTS FOR COASTLINE PLOT
import os
import contextily as ctx
import matplotlib.pyplot as plt
from shapely.ops import unary_union 
from shapely.geometry import box, MultiPolygon, Point, Polygon
from coastlinePlot import *

import pandas as pd
from datetime import datetime
import imageio

#function that creates a line and rotates it 
def create_line_angle(station, angle): 
    length = .03
    end_x = station.x + length * math.cos(to_radians(angle))
    end_y = station.y + length * math.sin(to_radians(angle))

    point_b = Point(end_x, end_y)

    line = LineString([station, point_b])
    
    return line

def graph_signal(ax, line): 
    x, y = line.xy
    ax.plot(x,y, linewidth = .5, color = 'b', linestyle = '-')

def to_radians(angle): 
    return math.radians(angle)

#create map of coast with satellite angle data at specific one frame 
def create_frame(station_angles, stations, ax): 
    columns_to_check = station_angles.index[2: ]
    time_frame = station_angles['TimeFrame']

    for column in columns_to_check: 
        value = station_angles[column]
        if pd.notna(value) and pd.api.types.is_numeric_dtype(value): 
            signal = create_line_angle(stations[column], value + 90) 
            graph_signal(ax, signal)

    # Annotate with timestamp in the bottom left corner
    timestamp_to_display = pd.to_datetime(station_angles['TimeFrame'])
    ax.annotate(timestamp_to_display.strftime('%Y-%m-%d %H:%M:%S'),
            xy=(0.05, 0.05), xycoords='axes fraction',
            fontsize=10, bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))

#Will probably still want to display fig after saving if calling from main 
def save_frame(fig, timestamp): 
    filename = f'/Users/kaylaracelis/Desktop/NIWC24/frames/{timestamp}.png' 
    plt.savefig(filename)

#Dont need to display fig when downloading for animation. Must close fig for next map. 
def save_ani_frame(fig, timestamp): 
    filename = f'/Users/kaylaracelis/Desktop/NIWC24/frames/{timestamp}.png' 
    plt.savefig(filename)
    plt.close()

def create_image_frames(angle_df, coastline, stations, abbreviations): 
    for index, row in angle_df.iterrows(): 
        #create new fig and axis for each row 
        fig, ax = plt.subplots() 

        create_basemap(coastline, stations, abbreviations)

        create_frame(row, stations, ax)
        save_frame(fig, row['TimeFrame']) 

# def update_frame(row, stations, ax, coastline, abbreviations): 
#     ax.clear() # clear previous plot 
#     create_basemap(coastline, stations, abbreviations)

#     #add frame data
#     ax = create_frame(row, stations, ax)

#     return row

# def get_interval(first_time, next_time): 
#     duration = next_time - first_time
#     interval = duration.seconds * 5

#     return interval 


# def animate(fig, angle_df, stations, coastline, abbreviations): 
#     #create a duplicate with shift to get interval 
#     angle_df['nextTimeFrame'] = angle_df['TimeFrame'].shift(-1)

#     #convert columns to datetime 
#     angle_df['TimeFrame'] = pd.to_datetime(angle_df['TimeFrame']) 
#     angle_df['nextTimeFrame'] = pd.to_datetime(angle_df['nextTimeFrame'])

#     time_diffs = angle_df.apply(lambda row: get_interval(row['TimeFrame'], row['nextTimeFrame']), axis = 1)

#     #time_diffs = angle_df['TimeFrame'].diff().dt.total_seconds().values * 1000 

#     #create animation 
#     ani = FuncAnimation(fig, update_frame, frames = angle_df['TimeFrame'], blit = True, interval = 200)

#     #save animation 
#     ani.save('animation.mp4', writer = 'ffmpeg')

#     plt.show()

    