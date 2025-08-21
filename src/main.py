import tkinter as tk
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, shape
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
canvas_frame = tk.Frame(root, background='blue', width=700, height=700, relief="raised", border=5)
canvas_frame.pack(side='top',  padx=5, pady=5)

x = 0
y = 0
x2 = 0
y2 = 0
canvas_width = 700
canvas_height = 700
canvas = tk.Canvas(background='white', master=canvas_frame, width=canvas_width, height=canvas_height)
oval = canvas.create_oval(x, y, x+50, y+50, fill='black')
oval2 = canvas.create_oval(x2, y2, x2+50, y2+50, fill='black')

canvas.pack()

shape_path = "C:/Users/gtcdu/Downloads/extractedData_harbour_arcmap (1)/zipfolder/Harbour_Depth_Area.shp"
shp = gpd.read_file(shape_path)
minx, miny, maxx, maxy = shp.total_bounds
# Calculate the geographic width and height
geo_width = maxx - minx
geo_height = maxy - miny

buffer = 20
x_scale = (canvas_width - buffer) / geo_width
y_scale = (canvas_height - buffer) / geo_height

scale = min(x_scale, y_scale)

x_offset = (canvas_width - geo_width * scale) / 2
y_offset = (canvas_height - geo_height * scale) / 2

polygon_ids={}

for index, row in shp.iterrows():
    # Get the geometry from the current row
    geometry = row['geometry']
    depth1 = row["DRVAL1"]
    depth2 = row["DRVAL2"]
    
    # Check if the geometry is a Polygon (or MultiPolygon)
    if geometry.geom_type == 'Polygon':
        # Get the exterior coordinates as a list of tuples
        exterior_coords = list(geometry.exterior.coords)
        
         # Apply scaling and offsetting to each coordinate
        scaled_coords = []
        for x_geo, y_geo  in exterior_coords:
            # Scale and offset the x and y coordinates
            new_x = (x_geo - minx) * scale #+ x_offset
            new_y = (maxy - y_geo) * scale# + y_offset
            scaled_coords.extend([new_x, new_y])

        # Draw the scaled polygon on the canvas
        id=canvas.create_polygon(scaled_coords, fill='blue', outline='red', width=0)
        polygon_ids[id]={"depth1": depth1, "depth2": depth2}

canvas.lift(oval)
canvas.lift(oval2)        
def left(event):
    x=-10
    canvas.move(oval, x, y)

def right(event):
    x=10
    canvas.move(oval, x, y)

def up(event):
    y=-10
    canvas.move(oval, x, y)
    
def down(event):
    y=10
    canvas.move(oval, x, y)

def left2(event):
    x2=-10
    canvas.move(oval2, x2, y2)

def right2(event):
    x2=10
    canvas.move(oval2, x2, y2)

def up2(event):
    y2=-10
    canvas.move(oval2, x2, y2)
    
def down2(event):
    y2=10
    canvas.move(oval2, x2, y2)

root.bind("<Left>", left)
root.bind("<Right>", right)
root.bind("<Up>", up)
root.bind("<Down>", down)

root.bind("<a>", left2)
root.bind("<d>", right2)
root.bind("<w>", up2)
root.bind("<s>", down2)

selected_polygon_id = None
def on_canvas_click(event):
    global selected_polygon_id

    # Find the closest item to the click event coordinates
    # find_closest returns a tuple of IDs, so we get the first element
    closest_items = canvas.find_closest(event.x, event.y) 

    if closest_items:  # Check if any item was found
        clicked_item_id = closest_items[0]

        # If a polygon was previously selected, restore its original color
        if selected_polygon_id:
            canvas.itemconfigure(selected_polygon_id, outline="black")

        # Check if the clicked item is a polygon (optional, you can use tags here if desired)
        # For simplicity, we are assuming all canvas items are polygons in this example
        
        # Highlight the clicked polygon
        canvas.itemconfigure(clicked_item_id, outline="purple", width=1, fill="black")
        selected_polygon_id = clicked_item_id  # Update the selected polygon
        print(f"Clicked on polygon with ID: {clicked_item_id}")
        print(f"Depth: {polygon_ids[clicked_item_id]['depth1']},{polygon_ids[clicked_item_id]['depth2']}")

# Bind the left mouse button click event to the canvas
canvas.bind("<Button-1>", on_canvas_click)



# fig, ax = plt.subplots(figsize=(6,6))
# # ax.set_facecolor("Green")

# # matplot graphs
# fig = Figure(figsize=(7,7), dpi=100, facecolor='white')

# ax = fig.add_subplot()
# shp.plot(ax=ax, column="DRVAL1", cmap="Blues", legend=True)

# canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
# canvas.draw()
# toolbar = NavigationToolbar2Tk(canvas, canvas_frame, pack_toolbar=False, )
# toolbar.update()

# canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed quit {event.key}"))
# canvas.mpl_connect("key_press_event", key_press_handler)

# button_quit = tk.Button(master=root, text="Quit", command=root.destroy)

# def update_frequency(event):
#     # check if in plot
#     if event.inaxes:
#     # Get the mouse coordinates in data space
#         x, y = event.xdata, event.ydata
#         mouse_point = Point(x, y)

#         # Iterate through each row (polygon) in the GeoDataFrame
#         for x ,row in shp.iterrows():
#             #  Check if the mouse point is within the current polygon
#             if row.geometry.contains(mouse_point):
#                 # If it is, get the depth value
#                 depth = row['DRVAL1']
#                 # Display the coordinates and depth on the status bar
#                 # ax.format_coord = lambda x, y: f'Lat: {event.ydata:.4f}, Lon: {event.xdata:.4f}, Depth: {depth:.2f}m'
#                 print(f'Lat: {event.ydata:.4f}, Lon: {event.xdata:.4f}, Depth: {depth:.2f}m')
#                 return # Exit the function once we find a match
    
#         ax.format_coord = lambda x, y: f'Lat: {event.ydata:.4f}, Lon: {event.xdata:.4f}'
#     # required to update canvas and attached toolbar!
#     canvas.draw()

# # slider_update = tk.Scale(root, from_=1, to=5, orient=tk.HORIZONTAL, command=update_frequency, label="Frequency [Hz]")
# button_quit.pack(side=tk.BOTTOM)
# fig.canvas.mpl_connect('motion_notify_event', update_frequency)
# # slider_update.pack(side=tk.BOTTOM)
# toolbar.pack(side=tk.BOTTOM, fill=tk.X)
# canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

root.mainloop()