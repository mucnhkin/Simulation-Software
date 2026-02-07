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
    def __init__(self, width, height, cells_n, canvas):
        self.width = width
        self.height = height
        self.cells_n = cells_n
        self.grid = []
        self.canvas = canvas
        self.img_tk = None
        
        # Calculate spacing (for divisible cell counts, this is exact)
        self.col_space = self.width / self.cells_n 
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
                
                # Check if water or land
                ovrlap_obj = self.canvas.find_overlapping(pos_x, pos_y, pos_x, pos_y)
                target_ojb = self.canvas.find_withtag("map")
                
                is_water = any(id in target_ojb for id in ovrlap_obj)
                
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





        
