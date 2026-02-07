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
        self.row_space = self.get_cell_spacing(self.width)  #rows involve width
        self.col_space = self.get_cell_spacing(self.height) #cols involve hieght
        self.cell_size = self.row_space
        self.draw_test_grid()

    def get_cell_spacing(self, length):
        """
        returns the cell spacing for the grid
        """
        return length // self.cells_n 
    
    def draw_test_grid(self):
        """Creates the grid"""
        pos_x = 0
        pos_y = 0
        radius = 1
        for row in range(self.cells_n): # iterate down the screen
            tmp = []
            is_water = False
            for col in range(self.cells_n): # iterate across the screen
                ovrlap_obj = self.canvas.find_overlapping(pos_x, pos_y, pos_x, pos_y)
                target_ojb = self.canvas.find_withtag("map")
                for id in ovrlap_obj:
                    if id in target_ojb:
                        is_water = True
                        break                       
                if is_water:
                    cell = Cell(id=0)
                    cell.pos_x = pos_x
                    cell.pos_y = pos_y
                    cell.row = row
                    cell.col = col
                    self.canvas.create_oval(pos_x-radius, pos_y-radius, pos_x+radius, pos_y+radius, fill='white', tags='cell')
                else:
                    cell = Cell(id=1)
                    self.canvas.create_oval(pos_x-radius, pos_y-radius, pos_x+radius, pos_y+radius, fill='red', tags='cell')
                tmp.append(cell)
                pos_x += self.col_space
                is_water = False

            self.grid.append(tmp)
            pos_y += self.row_space
            pos_x = 0
        
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





        
