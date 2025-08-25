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
root.title("fixing agents, adding placement, starting")
app_width = 800
app_height = 600
root.geometry(f'{app_width}x{app_height}')
root.resizable(False, False)

# frames and menus
sim_menu = tk.Frame(root, background='blue', width=200, height=app_height, relief="raised", border=5)
sim_menu.pack(side='left', padx=5, pady=5)
sim_menu.pack_propagate(False)
file_menu = tk.Frame(root, background="grey", width=app_width, height=100, relief="raised", border=5)
file_menu.pack(side='bottom', padx=5, pady=5)
canvas_frame = tk.Frame(root, background='blue', width=700, height=700, relief="raised", border=5)
canvas_frame.pack(side='top',  padx=5, pady=5)

canvas_width = 700
canvas_height = 700
canvas = tk.Canvas(background="#011500", master=canvas_frame, width=canvas_width, height=canvas_height)
canvas.pack()


# ----buttton control----
# start simulation
spawn_point = []
target_point = None
def on_start_click():
    canvas.unbind("<Button-1>")
    start_btn.config(state="disabled")
    global model_test
    global spawn_point
    model_test = UUVModel(n=tracker, canvas=canvas, spawns=spawn_point, targets=target_point)
    root.after(100, animate)

#buttons start and stop
start_btn = tk.Button(sim_menu, text="Start", command=on_start_click, bg="white")
start_btn.pack(side="top")




# ----radio options----

# radion fuctions
tracker = 0
target_n = 0
def handle_click(event):
    global spawn_point
    global tracker
    global target_n
    global target_point
    global selected_option

    if selected_option.get()=="uuv":
        if tracker != 5:
            start = canvas.create_oval(event.x, event.y, event.x + 10, event.y +10, fill="green")
            canvas.lift(start)
            tracker += 1
            tmp_spw = np.array([event.x, event.y])
            spawn_point.append(tmp_spw)
    elif selected_option.get()=="target":
        if target_n != 1:
            target = start = canvas.create_oval(event.x, event.y, event.x + 10, event.y +10, fill="red")
            canvas.lift(target)
            target_n = 1
            target_point = np.array([event.x, event.y])


canvas.bind("<Button-1>", handle_click)

#radio buttons select
selected_option = tk.StringVar()
selected_option.set("uuv")


uuv_start_radio = tk.Radiobutton(sim_menu, text="Spawn uuv point", variable=selected_option, value="uuv")
target_radio = tk.Radiobutton(sim_menu, text="target point", variable=selected_option, value="target")
uuv_start_radio.pack()
target_radio.pack()




# setup the map to be drawn
shape_path = "C:/Users/gtcdu/Downloads/extractedData_harbour_arcmap (1)/zipfolder/Harbour_Depth_Area.shp"
shallow_color = (170, 201, 250)
deep_color = (0, 0, 26)
current_map = map.MapControl(shape_path=shape_path, canvas=canvas, shallow_color=shallow_color, deep_color=deep_color)



# setup the agent model


# reantimate the canvas to see changes(UUV-agent-based)the oragne one
def animate():
    """Animation loop that steps the model and updates the canvas."""
    # Schedule the next call to this function after 50 milliseconds
    root.after(50, animate)
    model_test.step()




root.mainloop()

def main():
    print("main loop")

if __name__ == "__main__":
    main()