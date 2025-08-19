import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point



# Read the file and plot it
shape_path = "C:/Users/gtcdu/Downloads/extractedData_harbour_arcmap (1)/zipfolder/Harbour_Depth_Area.shp"
shp = gpd.read_file(shape_path)
fig, ax = plt.subplots(figsize=(6,6))
ax.set_facecolor("Green")
shp.plot(ax=ax, column="DRVAL1", cmap="Blues", legend=True)


def format_coord(event):
  # check if in plot
    if event.inaxes:
    # Get the mouse coordinates in data space
        x, y = event.xdata, event.ydata
        mouse_point = Point(x, y)

        # Iterate through each row (polygon) in the GeoDataFrame
        for x ,row in shp.iterrows():
            #  Check if the mouse point is within the current polygon
            if row.geometry.contains(mouse_point):
                # If it is, get the depth value
                depth = row['DRVAL1']
                # Display the coordinates and depth on the status bar
                ax.format_coord = lambda x, y: f'Lat: {event.ydata:.4f}, Lon: {event.xdata:.4f}, Depth: {depth:.2f}m'
                return # Exit the function once we find a match
    
        ax.format_coord = lambda x, y: f'Lat: {event.ydata:.4f}, Lon: {event.xdata:.4f}'


fig.canvas.mpl_connect('motion_notify_event', format_coord)
# ax.format_coord = format_coord

plt.show()

