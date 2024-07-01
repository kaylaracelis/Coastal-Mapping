import geopandas as gpd                     #IMPORTS FOR TRI-ANIMATION
from shapely.geometry import Point, LineString 
import math 

import geopandas as gpd                     #IMPORTS FOR COASTLINE PLOT
import os
import contextily as ctx
import matplotlib.pyplot as plt
from shapely.ops import unary_union 
from shapely.geometry import box, MultiPolygon, Point, Polygon
from coastlinePlot import *

import pandas as pd

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
    ax.annotate(x,y, linewidth = .5, color = 'b', linestyle = '-')

def to_radians(angle): 
    return math.radians(angle)

#create map of coast with satellite angle data at specific one frame 
def create_frame(station_angles, ax): 
    columns_to_check = station_angles.index[2: ]
    time_frame = station_angles['TimeFrame']

    annotations = []

    for column in columns_to_check: 
        value = station_angles[column]
        if pd.notna(value) and pd.api.types.is_numeric_dtype(value): 
            signal = create_line_angle(station_angles[column], value + 90) 
            annotation = graph_signal(ax, signal) 
            annotations.append(annotation)

    
def remove_annotations(annotations): 
    for annotation in annotations: 
        annotation.remove()
    


