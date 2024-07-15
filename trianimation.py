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
import glob 
from moviepy.editor import ImageSequenceClip 

#function that creates a line and rotates it 
def create_line_angle(station, angle): 
    length = .03
    end_x = station.x + length * math.cos(to_radians(angle))
    end_y = station.y + length * math.sin(to_radians(angle))

    point_b = Point(end_x, end_y)

    line = LineString([station, point_b])
    
    return line

def create_highlight_area(station, angle): 
    # Convert angle to radians, get end point and main line. 
    angle_rad = to_radians(angle)
    offset_rad = to_radians(10)
    x1, y1 = station.x, station.y

    length = .03 
    x2 = station.x + length * math.cos(to_radians(angle)) 
    y2 = station.y + length * math.sin(to_radians(angle))

    point_b = Point(x2, y2)
    line = LineString([station, point_b]) 

    # create highlight polygons, 10 degrees in either direction of the line
    highlight_polygons = [] 
    print(f"{angle}")

    highlight_points = [(x1, y1), rotate_point((x2, y2), offset_rad, station = (x1, y1)), rotate_point((x2, y2), -offset_rad, station = (x1, y1))]
    highlight_polygons.append(Polygon(highlight_points))
    # for base_angle in [angle_rad - offset_rad, angle_rad + offset_rad]: 
    #     highlight_points = [(x1, y1), rotate_point((x2, y2), base_angle, station = (x1, y1)), rotate_point((x2, y2), base_angle, station = (x1, y1)) ]

    #     highlight_polygons.append(Polygon(highlight_points))

    #combine highlight polygons into one 
    highlight_area = unary_union(highlight_polygons) 
    print(f"{highlight_area}")

    #create a geodataframe for the highlight area
    gdf_highlight = gpd.GeoDataFrame(geometry = [highlight_area], crs = "EPSG:  4269")

    return gdf_highlight

        
def rotate_point(point, angle, station): 
    ox, oy = station
    px, py = point 
    qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy) 
    qy = oy + np.sin(angle) * (px - ox) - np.cos(angle) * (py - oy) 
    return qx, qy 

def graph_signal(ax, line): 
    x, y = line.xy
    ax.plot(x,y, linewidth = .5, color = 'b', linestyle = '-')

def to_radians(angle):
    return math.radians(angle)

#create map of coast with satellite angle data at specific one frame 
def create_frame(station_angles, stations, ax): 
    columns_to_check = station_angles.index[2:] #start column 2 
    time_frame = station_angles['TimeFramePacific'] # use the pacific time 

    for column in columns_to_check: 
        value = station_angles[column]
        if pd.notna(value) and pd.api.types.is_numeric_dtype(value): 
            signal = create_line_angle(stations[column], 90) # doin stuff [ value + 90] 
            graph_signal(ax, signal)
            highlight = create_highlight_area(stations[column], 90) 
            highlight.plot(ax = ax, color = 'orange', alpha = 0.5)
            

    # Annotate with timestamp in the bottom left corner
    datetime_format = '%y-%m-%d %H:%M:%S: Pacific Time'  # Adjust format as per your data
    timestamp_to_display = datetime.strptime(time_frame, datetime_format)
    ax.annotate(timestamp_to_display.strftime('%Y-%m-%d %H:%M:%S'),
                xy=(0.05, 0.05), xycoords='axes fraction',
                fontsize=10, bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))

#Will probably still want to display fig after saving if calling from main 
def save_frame(fig, timestamp): 
    filename = f'/Users/kaylaracelis/Downloads/NIWCII/FRAMES/{timestamp}.png' 
    plt.savefig(filename)

# #Dont need to display fig when downloading for animation. Must close fig for next map. 
# def save_ani_frame(fig, timestamp): 
#     filename = f'/Users/kaylaracelis/Desktop/NIWC24/frames/{timestamp}.png' 
#     plt.savefig(filename)

def create_image_frames(angle_df, coastline, stations, abbreviations): 
    for index, row in angle_df.iterrows(): 
        #create new fig and axis for each row 
        fig, ax = create_basemap(coastline, stations, abbreviations)

        rowdata = angle_df.iloc[index]
        create_frame(rowdata, stations, ax)
        save_frame(fig, row['TimeFramePacific']) 

        plt.close(fig)

def create_image_frames_from_start(start, angle_df, coastline, stations, abbreviations): 
    for index, row in angle_df.iloc[start:].iterrows():
        #create new fig and axis for each row 
        fig, ax = create_basemap(coastline, stations, abbreviations) 

        rowdata = angle_df.iloc[index]
        create_frame(rowdata, stations, ax)
        save_frame(fig, row['TimeFramePacific'])

        plt.close(fig)

# def extract_timestamp(file_name): 
#     #Assuming format: 'YY-MM-DD HH/MM/SS/ Pacific Time.png 
#     #Replace slashes with colons and spaces appropriately 
#     timestamp_part = file_name.split('/')[-1].split('.png')[0]
#     timestamp = timestamp_part.replace('/', ':').replace(' ', '_')
#     #Example result : 'YY-MM-DD_HH:MM:SS_Pacific_Time.png
#     return timestamp 

# THIS AINT WORK .. or it half works 
def create_animation(folder_path): 
    # retrieve all PNG files in the folder 
    files = glob.glob(os.path.join(folder_path, '*.png'))

    #sort files chronologically 
    files.sort() 

    batch_size = 1000 

    #initialize variables for batch processing 
    batch_number = 1
    start_index = 0 

    while start_index < len(files): 
        #determine the end index of the current batch
        end_index = min(start_index + batch_size, len(files))

        #gather files for the current batch 
        batch_files = files[start_index:end_index]

        #create list to hold images for the batch 
        images = [] 

        #read each image and append the images list 
        for filename in batch_files: 
            images.append(filename)
        
        #create output file for the batch 
        output_filename = f'animation_batch_{batch_number}.mp4'

        #create image sequence clip from the batch of images
        clip = ImageSequenceClip(images, fps=24)

        #save the batch of images as an mp4
        clip.write_videofile(output_filename, codec= 'libx264', fps=24)

        print(f'Batch {batch_number} created: {output_filename}')

        #move to next batch 
        batch_number += 1
        start_index += batch_size 



def rename_files(folder_path): 
    #get a list of all files in the folder 
    files = os.listdir(folder_path) 

    for file_name in files: 
        if file_name.endswith('.png'): 
            #extract timestamp part between the last / and png
            timestamp_part = file_name.split('/')[-1].split('.png')[0]

            #replace slashes and spaces with colons and underscores 
            new_timestamp = timestamp_part.replace('/', ':').replace(' ', '_')

            #construct the new file name 
            new_file_name = f"{new_timestamp}.png"

            #rename the file 
            try: 
                os.rename(os.path.join(folder_path, file_name), os.path.join(folder_path, new_file_name))
                print(f"Renamed {file_name} to {new_file_name}")
            except Exception as e: 
                print(f"Error remaining {file_name}: {e}")




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

    