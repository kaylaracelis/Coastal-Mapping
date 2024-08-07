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

#same as trianimation except that theres framework for adjusting the length of the signal visualization based on RSSI 

def create_point(station, angle, length): # 
    end_x = station.x + length * math.cos(to_radians(angle))
    end_y = station.y + length * math.sin(to_radians(angle))

    point_b = Point(end_x, end_y)

    return point_b

#function that creates a line and rotates it 
def create_line_angle(station, angle, length): 

    point_b = create_point(station, angle, length)
    line = LineString([station, point_b])
    
    return line

def length_from_rssi(rssi): 
    return 
    ## FUNCTION CONVERTING RSSI INTO LENGTH 

def create_highlight_area(station, angle, length): 
    # Convert angle to radians, get end point and main line. 
    
    angle_a = angle + 10
    angle_b = angle - 10

    point_a = create_point(station, angle_a, length)
    point_b = create_point(station, angle_b, length)

    # create highlight polygons, 10 degrees in either direction of the line
    highlight_polygons = [] 
    print(f"{angle}")

    highlight_points = [(station.x, station.y), (point_a.x, point_a.y), (point_b.x, point_b.y)]
    highlight_polygons = [Polygon(highlight_points)]
    highlight_area = unary_union(highlight_polygons) 
    print(f"{highlight_area}")

    #create a geodataframe for the highlight area
    gdf_highlight = gpd.GeoDataFrame(geometry = [highlight_area], crs = "EPSG:  4269")

    return gdf_highlight

MAX_OVERLAPS = 4  # Maximum number of overlaps to consider

def check_overlap(highlight_areas, depth=0):
    result = []
    new_highlight_areas = []
    
    # Iterate through each pair of highlight areas
    for i in range(len(highlight_areas)):
        for j in range(i + 1, len(highlight_areas)):
            area_i = highlight_areas[i]['geometry'].iloc[0]
            area_j = highlight_areas[j]['geometry'].iloc[0]

            # Check if areas i and j intersect
            if area_i.intersects(area_j):
                # Get intersection area
                intersection = area_i.intersection(area_j)
                intersection_area = intersection.area

                result.append([intersection_area, depth + 1])

                # Replace the original highlight areas with the intersected area
                new_highlight_area = gpd.GeoDataFrame(geometry=[intersection])
                new_highlight_areas.append(new_highlight_area)
    
    # Limit the number of new overlaps considered
    new_highlight_areas = new_highlight_areas[:MAX_OVERLAPS]
    
    # If no new overlaps found or reached maximum depth, return the current result
    if not new_highlight_areas or depth >= MAX_OVERLAPS - 1:
        return result
    
    # Recursively call check_overlap with the newly formed highlight areas
    result.extend(check_overlap(new_highlight_areas, depth + 1))
    
    return result

def plot_highlight_areas(highlight_areas, result, ax):
    
    # Get max depth to determine color map
    max_depth = max(item[1] for item in result) if result else 0
    
    # Plot each highlight area with color based on depth
    for i, gdf in enumerate(highlight_areas):
        color = plt.cm.viridis(result[i][1] / max_depth) if max_depth > 0 else 'blue'
        gdf.plot(ax=ax, facecolor=color, alpha=0.4)
    
    return ax
            
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

##********************************CHANGING SHIT IN HERE *****************************  BE WARY 
#create map of coast with satellite angle data at specific one frame 
def create_frame(station_angles, station_RSSI, stations, ax): 
    columns_to_check = station_angles.index[2:] #start column 2 
    time_frame = station_angles['TimeFramePacific'] # use the pacific time 
    highlight_areas = []

    for column in columns_to_check: 
        value = station_angles[column]

        if pd.notna(value) and pd.api.types.is_numeric_dtype(value): 

            rssi = station_RSSI[column] 
            length = length_from_rssi(rssi)

            #PUT STUFF HERE ABOUT CONVERTING RSSI INTO APPROPRIATE DISTANCE 

            signal = create_line_angle(stations[column], 90, length) # doin stuff [ value + 90] 
            graph_signal(ax, signal)
            highlight = create_highlight_area(stations[column], 90, length) 
            highlight_areas.append(highlight)

    #call check_overlap function
    overlap_results = check_overlap(highlight_areas)

    #plot highlighted areas colorcoded by overlap depth 
    ax = plot_highlight_areas(highlight_areas, overlap_results, ax)

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

#*****CHANGING STUFF IN HERE 
def create_image_frames(angle_df, ping_df, coastline, stations, abbreviations): ##################################
    for index, row in angle_df.iterrows(): 
        #create new fig and axis for each row 
        fig, ax = create_basemap(coastline, stations, abbreviations)

        anglerowdata = angle_df.iloc[index]
        pingrowdata = ping_df.iloc[index]
        create_frame(anglerowdata, pingrowdata, stations, ax)
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


if __name__ == "__main__":
    # Example GeoDataFrame initialization
    polygon1 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    polygon2 = Polygon([(1, 1), (3, 1), (3, 3), (1, 3)])
    polygon3 = Polygon([(2, 2), (4, 2), (4, 4), (2, 4)])
    
    gdf1 = gpd.GeoDataFrame(geometry=[polygon1])
    gdf2 = gpd.GeoDataFrame(geometry=[polygon2])
    gdf3 = gpd.GeoDataFrame(geometry=[polygon3])
    
    highlight_areas = [gdf1, gdf2, gdf3]
    
    # Call check_overlap function
    overlap_results, intersected_areas = check_overlap(highlight_areas)

    fig, ax = plt.sublplots(figsize = (8,6))
    
    # Plot highlighted areas color-coded by overlap depth
    highlight_region(intersected_areas, overlap_results, ax)