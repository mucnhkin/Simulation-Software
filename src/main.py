import tkinter as tk
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.patches import Circle


# setup intial window
root = tk.Tk()
root.title("Attemp")
app_width = 800
app_height = 600
root.geometry(f'{app_width}x{app_height}')
root.resizable(False, False)

# frames and menus
sim_menu = tk.Frame(root, background='blue', width=200, height=app_height, relief="raised", border=5)
sim_menu.pack(side='left', padx=5, pady=5)
file_menu = tk.Frame(root, background="grey", width=app_width, height=100, relief="raised", border=5)
file_menu.pack(side='bottom', padx=5, pady=5)
canvas_frame = tk.Frame(root, background='blue', width=300, height=300, relief="raised", border=5)
canvas_frame.pack(side='top',  padx=5, pady=5)


shape_path = "C:/Users/gtcdu/Downloads/extractedData_harbour_arcmap (1)/zipfolder/Harbour_Depth_Area.shp"
shp = gpd.read_file(shape_path)
# fig, ax = plt.subplots(figsize=(6,6))
# ax.set_facecolor("Green")

# matplot graphs
fig = Figure(figsize=(7,7), dpi=100, facecolor='white')

ax = fig.add_subplot()
shp.plot(ax=ax, column="DRVAL1", cmap="Blues", legend=True)

canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
canvas.draw()
toolbar = NavigationToolbar2Tk(canvas, canvas_frame, pack_toolbar=False, )
toolbar.update()

canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed quit {event.key}"))
canvas.mpl_connect("key_press_event", key_press_handler)

button_quit = tk.Button(master=root, text="Quit", command=root.destroy)

def update_frequency(event):
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
    # required to update canvas and attached toolbar!
    # canvas.draw()

# slider_update = tk.Scale(root, from_=1, to=5, orient=tk.HORIZONTAL, command=update_frequency, label="Frequency [Hz]")
button_quit.pack(side=tk.BOTTOM)
fig.canvas.mpl_connect('motion_notify_event', update_frequency)
# slider_update.pack(side=tk.BOTTOM)
toolbar.pack(side=tk.BOTTOM, fill=tk.X)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

root.mainloop()