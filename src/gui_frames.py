# --- Project Information ---
# Project: UUV Simulation Framework
# Version: 1.0.0
# Date: November 2025
#
# --- Authors and Contributors ---
# Primary:
# - Gunner Cook-Dumas (SCRUM Manager, Backend, Agent, Model, and GA Stucture)
# - Justin Mosman (developer)
# - Michael Cardinal (developer)
#
# Secondary:
# - Lauren Milne (SCRUM Product Owner)
#
# --- Reviewers/Bosses ---
# - Prof. Lance Fiondella, ECE, University of Massachusetts Dartmouth
# - Prof. Hang Dinh, CIS, Indiana University South Bend

import tkinter as tk

#Below are various frames / menus that are used within the main app window:

#Menu frame, used on the right side of the sim, holds most general frames such as map selection
# agent menu, simulation settings, etc.
class Menu(tk.Frame):
    """Handles the menu for the other sub menus (right side of the window)"""
    def __init__(self, parent, size, color):
        super().__init__(parent, width=size[0], height=size[1], bg=color, border=5)
        self.padding = 5
        self.pack(side='right', padx=self.padding, pady=self.padding)
        self.pack_propagate(False)

# File menu (bottom of screen), holds the hover cursor location and the step interval slider
class FileMenu(tk.Frame):
    '''Handles the file menu and output'''
    def __init__(self, parent, size, color):
        super().__init__(parent, width=size[0], height=size[1], bg=color, relief='flat')
        self.padding = 5
        self.pack(side='bottom', padx=self.padding, pady=self.padding)
        self.pack_propagate(False)

# Canvas Frame, the canvas is where the map is loaded, this is simply the border frame that holds the canvas
class CanvasFrame(tk.Frame):
    '''controls the frame canvas that the simulation runs in'''
    def __init__(self, parent, size):
        super().__init__(parent, background="#333333", width=size[0] + 10, height=size[1] + 10, relief="raised", border=5)
        self.padding = 5
        self.parent = parent
        self.width = size[0]
        self.height = size[1]
        self.pack(side='left', padx=self.padding, pady=self.padding)
        self.pack_propagate(False)
        self.grid_propagate(False)

# Canvas Map, the actual canvas that is drawn on for the simulation
class CanvasMap(tk.Canvas):
    '''Handles the physcal canvas to draw on for simulation'''
    def __init__(self, parent, size):
        super().__init__(background="#040404", master=parent, width=size[0], height=size[1],
                         highlightthickness=0, bd=0)
        self.pack()
        self.parent = parent
        self.pack_propagate(False)
        self.start_x=0
        self.start_y=0
        self.end_x=0
        self.end_y=0
        self.current_rect = None

        self.bind("<Button-1>", self.get_start_xy, add='+') #first press
        self.bind("<ButtonRelease-1>", self.get_end_xy, add='+') #release
        self.bind("<B1-Motion>", self.update_rectangle_mouse_drag, add='+') #update

    def get_start_xy(self, event):
        """Get the coords for start x and start y"""
        # (start x, start y, end x, end y)
        print(f"can_select {self.parent.parent.can_select} and can_spawn {self.parent.parent.can_spawn}")
        if self.parent.parent.can_select is True and self.parent.parent.can_spawn is False:
            self.start_x, self.start_y, _, _ = self.parent.parent.snap_to_grid(event.x, event.y)
            self.current_rect=self.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='white', tags="spawn_sel")
            # self.start_x, self.start_y = event.x, event.y
        else:
            print("CAN NOT SELECT")

    def get_end_xy(self, event):
        """Get the coords for the end x and end y"""
        if self.parent.parent.can_select is True and self.parent.parent.can_spawn is False:
            self.current_rect = None

    def update_rectangle_mouse_drag(self, event):
        """Updates the selection rectangle on mouse drag"""
        if self.current_rect:
            self.end_x, self.end_y, _, _ = self.parent.parent.snap_to_grid(event.x, event.y)
            self.coords(self.current_rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def viable_spawn_pos(self):
        all_rect_ids = self.find_withtag("spawn_sel")
        # print(f"all spawn selections {all_rect_ids}")
        return all_rect_ids


# General Frames, this is a class that is used as a general outline for many menus, it's meant to not
# be very specific functionality wise and is more so used for simple menus like the file selection and
# config menu
class GeneralFrames(tk.Frame):
    '''general frames in the menus'''
    def __init__(self, parent, size, color=None, side=None, anchor=None, text=None):
        super().__init__(parent, width=size[0], height=size[1], bg=color, border=5, bd=2, relief='solid')
        self.padding = 5
        self.pack(side=side, padx=self.padding, pady=self.padding)
        self.pack_propagate(False)
        if text != None:
            self.title = tk.Label(self, text=text, font=("Arial", 13, "bold"))
            self.title.pack(side='top', pady=(0, 2))
            self.file_bar = tk.Frame(self, bg="black", height=2)
            self.file_bar.pack(side="top", fill="x", pady=(0, 8))
