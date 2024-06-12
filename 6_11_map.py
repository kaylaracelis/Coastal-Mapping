import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.ops import unary_union 
from shapely.geometry import Polygon
from shapely.geometry import box

def main(): 

    #path to shapefile
    coastline = readFile('NIWC/socal_mapping/data/N30W120.shp')

    #define the bounding box coordinates 
    north, south, east, west = 33, 30, -117.0, -117.5

    #clip the coastline
    clipped_coastline = clipToBoundingBox(coastline, north, south, east, west)

    #plot the clipped coastline 
    fix, ax = plotCoast(clipped_coastline)

    #display the plot
    displayPlot(ax)
    return 0

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

def plotCoast(coast): 
    #plot the coastline with higher resolution
    fig, ax = plt.subplots(figsize=(15, 15), dpi = 400)
    coast.plot(ax=ax, color = 'blue', edgecolor = 'black', linewidth = 0.3)
    return fig, ax

def displayPlot(ax): 
    #set plot title and labels 
    ax.set_title('Socal Coastline', fontsize = 16)
    ax.set_xlabel('Longitude', fontsize = 6)
    ax.set_ylabel('Latitude', fontsize = 6) 

    #add a grid and background
    ax.grid(True) 
    ax.set_facecolor('lightgrey')

    #adjust font size for numbers on axis 
    ax.tick_params(axis = 'both', which = 'major', labelsize = 6)
    ax.tick_params(axis = 'both', which = 'minor', labelsize = 6)

    #display the plot 
    plt.tight_layout()
    plt.show()


#calling main
if __name__ == "__main__": 
    main()
