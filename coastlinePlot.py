import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import unary_union 
from shapely.geometry import Polygon
from shapely.geometry import box, MultiPolygon, Point
import geopandas as gpd
import contextily as ctx

def create_basemap(coastline, stations, abbreviations): 

    #define the bounding box coordinates 
    # COORDINATES FOR ALL STATIONS = 33.3, 32.53, -117.08, -117.5

    # COORDINATES FOR STATIONS 1-3 = 33.3, 33.18, -117.37, -117.5

    north, south, east, west = 33.3, 33.18, -117.37, -117.5 #ST 1-3

    #clip the coastline
    clipped_coastline = clipToBoundingBox(coastline, north, south, east, west)

    #plot the clipped coastline 
    fig, ax = plotCoast(clipped_coastline)

    #set plot title and labels 
    ax.set_title('Socal Coastline', fontsize = 16)
    ax.set_xlabel('Longitude', fontsize = 8)
    ax.set_ylabel('Latitude', fontsize = 8) 

    #add a grid and background
    ax.grid(True) 
    ax.set_facecolor('lightgrey')

    #convert coastline to Web Mercador (BASEMAP)
    clipped_coastline = clipped_coastline.to_crs(epsg=4269)

    #add basemap COLORED(BASEMAP)
    # ctx.add_basemap(ax, zoom = 12, crs = 'EPSG:4269', source = ctx.providers.OpenStreetMap.Mapnik)

    #add basemap BLACK&WHITE (BASEMAP)
    ctx.add_basemap(ax, zoom = 12, crs = 'EPSG:4269', source = ctx.providers.CartoDB.Positron)

    plotStations(ax, stations, abbreviations)

    return fig, ax


def readFile(shapefile_path): 
    #read shapefile using geopandas
    coast = gpd.read_file(shapefile_path)

    return coast 

def clipToBoundingBox(coast, north, south, east, west): 
    #create a bounding box 
    bbox = box(west, south, east, north)

    #clip the geodataframe to the bounding box 
    clipped_coast = coast.clip(bbox)
    return clipped_coast


def createAntennaStations(): 
    #create points for the antenna stations with their labels
    stations = {
        'V3023D363087': Point(-117.444597, 33.26738265),
        'V30B0154CF14': Point(-117.4194677, 33.2367467),
        'V3023D156846': Point(-117.4022308, 33.2137784),
        'V30B0154B2DE': Point(-117.2046347, 32.68884619),
        'V3023D368F92': Point(-117.1458056, 32.64076046),
        'V3023D368BAA': Point(-117.1586888, 32.66467077),
        'V30B0154E9A4': Point(-117.111427, 32.63882786),
        'V30B0154B2A1': Point(-117.1311581, 32.60645698),
        'V3023D36E6B0': Point(-117.1229701, 32.53529558)
    }
    return stations

def createAbbreviations(): 
    # Create a dictionary for abbreviations
    abbreviations = {
        'V3023D363087': 'ST1',
        'V30B0154CF14': 'ST2',
        'V3023D156846': 'ST3',
        'V30B0154B2DE': 'ST4',
        'V3023D368F92': 'ST5',
        'V3023D368BAA': 'ST6',
        'V30B0154E9A4': 'ST7',
        'V30B0154B2A1': 'ST8',
        'V3023D36E6B0': 'ST9'
    }
    return abbreviations

def plotStations(ax, stations, abbreviations): 
    #plot and label antenna stations 
    for label, point in stations.items(): 
        abbreviation = abbreviations[label]
        ax.plot(point.x, point.y, 'go', markersize = 5, label = f"{abbreviation} ({label})") #bo is blue
        ax.text(point.x, point.y, abbreviation, fontsize = 7, ha = 'right')

    #add a legend 
    handles, labels = ax.get_legend_handles_labels()
    unique_labels= dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys(), title= "Station Abbreviations", loc = 'upper right', fontsize = 5)

    return ax


#   FUNCTION CAN BE USED IN THE FUTURE TO PLOT NESTING SITES. 
# def createPoints(): 
#     #generate points near the specified coordinates 
#     #Note: 0.00001deg is like 30-40 feet. Choosing points at random. 
#     points = [
#         Point(-117.170, 32.708), 
#         Point(-117.168, 32.681), 
#         Point(-117.238, 32.67), 
#         Point(-117.157, 32.657), 
#         Point(-117.255, 32.72)
#     ]
#     return points

def plotPoints(ax, points):
    #plot and label points 
    for i, point in enumerate(points): 
        ax.plot(point.x, point.y, 'ro', markersize = 3)
        ax.text(point.x, point.y, f'Point{i+1}', fontsize=5, ha= 'right') #label point
    
    return ax

def plotCoast(coast): 
    #plot the coastline with higher resolution
    fig, ax = plt.subplots(figsize=(15, 15), dpi = 400)
    coast.plot(ax=ax, color = 'blue', edgecolor = 'black', linewidth = 0.3)

    return fig, ax

def saveSVG(ax, filename = 'coastal_map.svg'): 

    # #adjust font size for numbers on axis (FOR PDF SAVE)
    # ax.tick_params(axis = 'both', which = 'major', labelsize = 6)
    # ax.tick_params(axis = 'both', which = 'minor', labelsize = 6)

    # adjust font size for numbers on axis based on figure size (FOR SVG)
    figure_size = ax.figure.get_size_inches()
    font_size = min(8, 8 * (figure_size[0] + figure_size[1]) / 2) # adjust as needed 
    ax.tick_params(axis = 'both', which = 'major', labelsize = font_size)
    ax.tick_params(axis = 'both', which = 'minor', labelsize = font_size)

    #display the plot 
    plt.tight_layout()

    #get the current working directory (SVG)
    current_dir = os.getcwd()

    #construct the full filepath (SVG)
    file_path = os.path.join(current_dir, filename)

    #save the plot as SVG 
    plt.savefig(file_path, format = 'svg')
