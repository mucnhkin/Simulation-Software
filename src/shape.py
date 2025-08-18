import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from shapely.geometry import Point

import pandas as pd
import numpy as np

# def on_motion(event):
#     if event.inaxes:
#         # Get data coordinates
#         x_data, y_data = event.xdata, event.ydata
#         # Customize the status bar text
#         status_text = f"X: {x_data:.2f}, Y: {y_data:.2f} | Custom Info: Hello!"
#         # Update the status bar (this part depends on the backend and environment)
#         # In interactive backends, simply returning the string might work,
#         # or you might need to access the toolbar object directly.
#         # For simplicity, this example just prints to console.
#         print(status_text)



shape_path = "C:/Users/gtcdu/Downloads/extractedData_harbour_arcmap (1)/zipfolder/Harbour_Depth_Area.shp"
shp = gpd.read_file(shape_path)

fig, ax = plt.subplots(figsize=(6,6))

colum_data = shp["DRVAL1"]

shp.plot(ax=ax, column="DRVAL1", cmap="Blues", legend=True)

# fig.canvas.mpl_connect('motion_notify_event', on_motion)
original_prop = {'facecolor': shp.plot(ax=ax, column="DRVAL1", cmap="Blues").get_children()[0].get_facecolors()}
highlighted_poly = None

def format_coord(event):
    highlighted_poly = None

    # Check if the mouse is within the axes of the plot
    if event.inaxes:
    # Get the mouse coordinates in data space
        x, y = event.xdata, event.ydata
        mouse_point = Point(x, y)

        # Iterate through each row (polygon) in the GeoDataFrame
        for index, row in shp.iterrows():
            #  Check if the mouse point is within the current polygon
            if row.geometry.contains(mouse_point):
                # If it is, get the depth value
                depth = row['DRVAL1']
                # Display the coordinates and depth on the status bar
                ax.format_coord = lambda x, y: f'Lat: {event.ydata:.4f}, Lon: {event.xdata:.4f}, Depth: {depth:.2f}m'
                # fig.canvas.draw_idle()

                # Highlight the selected polygon.
                # First, revert the previous highlight if it exists.
                # if highlighted_poly is not None:
                    # highlighted_poly.remove()

                # Create a new plot of just the selected polygon with a highlight style
                # highlight_style = {
                    # 'facecolor': 'red',
                    # 'edgecolor': 'black',
                    # 'linewidth': 0,
                    # 'alpha': 0.8
                # }
                # highlighted_poly = shp.iloc[[index]].plot(ax=ax, **highlight_style).get_children()[0]

                return # Exit the function once we find a match
    
        ax.format_coord = lambda x, y: f'Lat: {event.ydata:.4f}, Lon: {event.xdata:.4f}'
        # fig.canvas.draw_idle()
        # If a polygon was highlighted but the mouse has moved out, remove the highlight
        # if highlighted_poly is not None:
            # highlighted_poly.remove()
            # highlighted_poly = None
            # return 'x=%1.4f, y=%1.4f, Depth=%1.2f'%(x, y, colum_data)
# 
fig.canvas.mpl_connect('motion_notify_event', format_coord)
# ax.format_coord = format_coord
plt.show()

