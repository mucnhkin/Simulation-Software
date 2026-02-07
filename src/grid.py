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

import math
import tkinter as tk
import numpy as np
from cell import Cell
from map import MapControl

class Grid:
    # passing from New_gui.py: 
    # width=self.canvas_size[0] -> 700, height=self.canvas_size[1] -> 700, cells_n=self.cell_count, canvas=self.canvas
    def __init__(self, width, height, cells_n, canvas):
        # Number of pixels from beginig to end (width)
        self.width = width
        # Number of pixels from beginig to end (height)
        self.height = height
        self.cells_n = cells_n
        self.grid = []
        self.canvas = canvas
        # Still didnt figure why we need this
        self.img_tk = None
        
        # Calculate spacing (for divisible cell counts, this is exact)
        # Amount of cells that fit in a column
        self.col_space = self.width / self.cells_n 
        # Amount of cells that fit in a row
        self.row_space = self.height / self.cells_n
        self.cell_size = self.width // self.cells_n  # Simple for divisible counts
        
        # Create the grid
        self.draw_test_grid()

    def draw_test_grid(self):
        """Creates the grid"""
        radius = 1
        
        for row in range(self.cells_n):
            tmp = []
            
            for col in range(self.cells_n):
                # Calculate position from index
                pos_x = int(col * self.col_space)
                pos_y = int(row * self.row_space)
                
                # 5 points of a cell. This will be used to validate if a cell is water or land.
                check_points = [
                    (pos_x, pos_y),  # Top-left
                    (pos_x + int(self.col_space), pos_y),  # Top-right
                    (pos_x, pos_y + int(self.row_space)),  # Bottom-left
                    (pos_x + int(self.col_space), pos_y + int(self.row_space)),  # Bottom-right
                    (pos_x + int(self.col_space/2), pos_y + int(self.row_space/2))  # Center
                ]

                target_ojb = self.canvas.find_withtag("map")
                water_count = 0

                # This for loop takes each point in a cell and determins if its water or land
                for px, py in check_points:
                    overlap_obj = self.canvas.find_overlapping(px, py, px, py)
                    if any(id in target_ojb for id in overlap_obj):
                        water_count += 1
                
                # If atleast 3 pixels were specified as water then cell is a water cell
                is_water = (water_count >= 3)
                
                # Create cell
                cell = Cell(id=0 if is_water else 1)
                cell.pos_x = pos_x
                cell.pos_y = pos_y
                cell.row = row
                cell.col = col
                
                # Draw dot
                self.canvas.create_oval(
                    pos_x - radius, pos_y - radius,
                    pos_x + radius, pos_y + radius,
                    fill='white' if is_water else 'red',
                    tags='cell'
                )
                
                tmp.append(cell)
                print(cell.id)
            
            self.grid.append(tmp)
        
    def get_locations(self, start, end):
        self.grid
        def find_cell(pos, cells):
            x, y = pos
            return next((cell for cell in cells if cell.pos_x == x and cell.pos_y == y), None)
        
        start_gen = (cell for row in self.grid for cell in row)
        start_cell = find_cell(start, start_gen)

        end_gen = (cell for row in self.grid for cell in row)
        end_cell = find_cell(end, end_gen)
        print(start_cell)
        print(end_cell)
            

    def __str__(self):
        """
        for debugging purposes
        """
        print(f'Grid length: {len(self.grid)}')
        grid_string = ""
        for row in self.grid:
            for cell in row:
                grid_string += str(cell.id) + " "
            grid_string += "\n"
        return grid_string.strip()





        
