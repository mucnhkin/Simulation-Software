import tkinter as tk
import numpy as np
import pandas as pd
import mesa
import geopandas as gpd
from shapely.geometry import Point, shape
import os

# project imports
from agents.model import UUVModel
import map

# For navigating the project
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_PATH)


# setup intial window
root = tk.Tk()
root.title("Better structure")
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

# some canvas and ojbect values
x = 0
y = 0
global_x = 0
global_y = 0
canvas_width = 700
canvas_height = 700
canvas = tk.Canvas(background="#011500", master=canvas_frame, width=canvas_width, height=canvas_height)
oval = canvas.create_oval(x, y, x+5, y+5, fill='white', tags='agent')
canvas.pack()

# setup the map to be drawn
shape_path = "C:/Users/gtcdu/Downloads/extractedData_harbour_arcmap (1)/zipfolder/Harbour_Depth_Area.shp"
shallow_color = (170, 201, 250)
deep_color = (0, 0, 26)
current_map = map.MapControl(shape_path=shape_path, canvas=canvas, shallow_color=shallow_color, deep_color=deep_color)
canvas.lift(oval)


# get user input and move UUV(non-agent-based)(white)
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
    current_map.depth_loc(global_x, global_y)
    prev_x = global_x


def right(event):
    x=10
    global global_x
    global prev_x
    global_x += x 
    print(f"({global_x}, {global_y})")
    canvas.move(oval, x, y)
    canvas.create_line(prev_x, prev_y, global_x, global_y, fill="orange", width=2, dash=(3, 3))
    current_map.depth_loc(global_x, global_y)
    prev_x = global_x

def up(event):
    y=-10
    global global_y
    global prev_y
    global_y += y
    print(f"({global_x}, {global_y})")
    canvas.move(oval, x, y)
    canvas.create_line(prev_x, prev_y, global_x, global_y, fill="orange", width=2, dash=(3, 3))
    current_map.depth_loc(global_x, global_y)
    prev_y = global_y
    
def down(event):
    y=10
    global global_y
    global prev_y
    global_y += y
    print(f"({global_x}, {global_y})")
    canvas.move(oval, x, y)
    canvas.create_line(prev_x, prev_y, global_x, global_y, fill="orange", width=2, dash=(3, 3))
    current_map.depth_loc(global_x, global_y)
    prev_y = global_y

# bind keycodes to functions
root.bind("<Left>", left)
root.bind("<Right>", right)
root.bind("<Up>", up)
root.bind("<Down>", down)

# setup the agent model
model_test = UUVModel(1, canvas=canvas)

# reantimate the canvas to see changes(UUV-agent-based)the oragne one
def animate():
    """Animation loop that steps the model and updates the canvas."""
    model_test.step()
    # Schedule the next call to this function after 50 milliseconds
    root.after(50, animate)
root.after(100, animate)


root.mainloop()

def main():
    print("main loop")

if __name__ == "__main__":
    main()