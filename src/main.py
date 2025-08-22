import tkinter as tk
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, shape
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.patches import Circle
polygon_ids={}
selected_polygon_id = None
def depth_loc(x, y):
    global selected_polygon_id

    closest_items = canvas.find_closest(x+5, y+5) 

    # if closet item was found
    if closest_items:
        clicked_item_id = closest_items[0]

        if clicked_item_id in polygon_ids:

            
            # If a polygon was previously selected, restore its original color
            if selected_polygon_id and selected_polygon_id in polygon_ids:
                original_color = polygon_ids[selected_polygon_id]['color']
                canvas.itemconfigure(selected_polygon_id, fill=original_color)

            # Highlight
            canvas.itemconfigure(clicked_item_id, width=0, fill="red")
            selected_polygon_id = clicked_item_id
            
            # Print information
            print(f"Clicked on polygon with ID: {clicked_item_id}")
            print(f"Depth: {polygon_ids[clicked_item_id]['depth1']}, {polygon_ids[clicked_item_id]['depth2']}")




# max color values
shallow_color = (170, 201, 250)
deep_color = (0, 0, 26)

def get_depth_color(current_depth, min_d, max_d):
    """
    Calculates a color in a gradient from light-blue to dark blue.
    """
    # normilize values, 0 for light, 1 for dark
    if max_d == min_d:
        normalized_depth = 0
    else:
        normalized_depth = (current_depth - min_d) / (max_d - min_d)
    
    # change the base rgb values
    r = int(shallow_color[0] + normalized_depth * (deep_color[0] - shallow_color[0]))
    g = int(shallow_color[1] + normalized_depth * (deep_color[1] - shallow_color[1]))
    b = int(shallow_color[2] + normalized_depth * (deep_color[2] - shallow_color[2]))

    # Convert the RGB to hex
    return f'#{r:02x}{g:02x}{b:02x}'


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
global_x = 0
global_y = 0
canvas_width = 700
canvas_height = 700
canvas = tk.Canvas(background="#011500", master=canvas_frame, width=canvas_width, height=canvas_height)
oval = canvas.create_oval(x, y, x+5, y+5, fill='black', tags='agent')

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



# min depth = light blue, max depth = dark blue
min_depth = shp['DRVAL2'].min()
max_depth = shp['DRVAL2'].max()

for index, row in shp.iterrows():

    # Get the geometry from the current row
    geometry = row['geometry']
    depth1 = row["DRVAL1"]
    depth2 = row["DRVAL2"]
    
    # Check if the geometry is a Polygon
    if geometry.geom_type == 'Polygon':

        # Get the exterior coordinates
        exterior_coords = list(geometry.exterior.coords)
        
        # Apply scaling to each coordinate(so can control the size)
        scaled_coords = []
        for x_geo, y_geo  in exterior_coords:
            # Scale
            new_x = (x_geo - minx) * scale
            new_y = (maxy - y_geo) * scale
            scaled_coords.extend([new_x, new_y])
            

        # get depth color
        fill_color = get_depth_color(depth2, min_depth, max_depth)

        # Draw the scaled polygon on the canvas and store in dictinary
        id=canvas.create_polygon(scaled_coords, fill=fill_color, width=0, tags="map")
        polygon_ids[id]={"depth1": depth1, "depth2": depth2, "color": fill_color}



canvas.lift(oval)
prev_x =0
prev_y = 0
def left(event):
    x=-10
    global global_x
    global prev_x
    global_x += x 
    print(f"({global_x}, {global_y})")
    canvas.move(oval, x, y)
    canvas.create_line(prev_x, prev_y, global_x, global_y, fill="orange", width=2, dash=(3, 3))
    depth_loc(global_x, global_y)
    prev_x = global_x


def right(event):
    x=10
    global global_x
    global prev_x
    global_x += x 
    print(f"({global_x}, {global_y})")
    canvas.move(oval, x, y)
    canvas.create_line(prev_x, prev_y, global_x, global_y, fill="orange", width=2, dash=(3, 3))
    depth_loc(global_x, global_y)
    prev_x = global_x

def up(event):
    y=-10
    global global_y
    global prev_y
    global_y += y
    print(f"({global_x}, {global_y})")
    canvas.move(oval, x, y)
    canvas.create_line(prev_x, prev_y, global_x, global_y, fill="orange", width=2, dash=(3, 3))
    depth_loc(global_x, global_y)
    prev_y = global_y
    
def down(event):
    y=10
    global global_y
    global prev_y
    global_y += y
    print(f"({global_x}, {global_y})")
    canvas.move(oval, x, y)
    canvas.create_line(prev_x, prev_y, global_x, global_y, fill="orange", width=2, dash=(3, 3))
    depth_loc(global_x, global_y)
    prev_y = global_y

root.bind("<Left>", left)
root.bind("<Right>", right)
root.bind("<Up>", up)
root.bind("<Down>", down)

root.mainloop()