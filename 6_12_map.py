import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.ops import unary_union 
from shapely.geometry import Polygon
from shapely.geometry import box, MultiPolygon, Point

def main(): 

    #path to shapefile
    coastline = readFile('NIWC/socal_mapping/data/N30W120.shp')

    #define the bounding box coordinates 
    north, south, east, west = 33, 32.5, -117.0, -117.4

    #clip the coastline
    clipped_coastline = clipToBoundingBox(coastline, north, south, east, west)

    #plot the clipped coastline 
    fix, ax = plotCoast(clipped_coastline)

    #add points near the coordinates 32.707 N, 117.173 W
    points = createPoints()

    #plot and label points 
    plotPoints(ax, points)

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

#TEST 
def createLandPolygon(coastline, north, south, east, west): 
    #create bounding box polygon
    bbox = box(west, south, east, north) 

    #merge all coastline geometries into a single geometry 
    coastline_union=unary_union(coastline.geometry)

    #split the bounding box with the coastline 
    land_polygons = bbox.difference(coastline_union)

    #ensure the result is a MultiPolygon
    if isinstance(land_polygons, Polygon): 
        land_polygons = MultiPolygon([land_polygons])

    return land_polygons

def createPoints(): 
    #generate points near the specified coordinates 
    #Note: 0.00001deg is like 30-40 feet. Choosing points at random. 
    points = [
        Point(-117.170, 32.708), 
        Point(-117.168, 32.681), 
        Point(-117.238, 32.67), 
        Point(-117.157, 32.657), 
        Point(-117.255, 32.72)
    ]
    return points

def plotPoints(ax, points):
    #plot and label points 
    for i, point in enumerate(points): 
        ax.plot(point.x, point.y, 'ro')
        ax.text(point.x, point.y, f'Point{i+1}', fontsize=8, ha= 'right') #label point

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
