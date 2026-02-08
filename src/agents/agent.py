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
import numpy as np
import heapq
import pandas as pd
import mesa
import geopandas as gpd
from shapely.geometry import Point, shape

from PIL import Image, ImageTk

import os
#print(os.getcwd())
#print("CWD printed for debug") #comments for debug
icon_path = os.path.join(os.getcwd(), "resources", "EnemyUUV.png")
#print(icon_path)

#user defined
from map import MapControl
from cell import Cell

from salinity import Salinity
from temperature import Temperature

class UUVAgent(mesa.Agent):                         #AS OF 11/14/25 Mike has added speed and has start path be dest (see lines 62-68)
    """UUV agent testing class"""
    DEFAULT_COLOR = "#FD0202"
    SPRITE_PATH = icon_path
    def __init__(self, model, spawn, map, canvas, grid, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        #Spawn variable
        self.spawn = spawn
        self.is_complete = False
        self.Speed = 1  # This value is multiplied by the added unit movement in x and y per step
        self.status = True  # for cuuv to kill the UUV >:}

        #Calculate cell size (used for pathfinding)
        if len(grid) > 0 and len(grid[0]) > 1:
            self.cell_size = grid[0][1].pos_x - grid[0][0].pos_x
        else:
            self.cell_size = 14  # fallback

        # Set a default destination - will be updated in first step()
        self.dest = [9, 33]  # fallback destination

        #Assign position to the grid via the spawn location 
        self.position = [grid[spawn[1]][spawn[0]].pos_x, grid[spawn[1]][spawn[0]].pos_y]
        #Set up salinity and temperature
        self.salinity = Salinity()
        self.temp = Temperature()

        # tkinter gui variables (color,map,canvas,oval on map,lifting)
        self.color = kwargs.get('color', self.DEFAULT_COLOR)
        self.map = map
        self.canvas = canvas
        #self.oval = self.canvas.create_oval(self.position[0]-5,self.position[1]-5, self.position[0]+5, self.position[1]+5, fill=self.color, tags='agent')
        #self.canvas.lift(self.oval)
        #Commented out for icons

      
        try:
            img = Image.open(icon_path)  
            img = img.resize((20, 20), Image.Resampling.LANCZOS)  # change size here
            self.icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print("Error loading agent icon:", e)
            self.icon = None

        if self.icon is not None:
            self.sprite = self.canvas.create_image(
            self.position[0], 
            self.position[1], 
            image=self.icon,
            tags="agent"
        )
        else:
            # fallback: draw oval if icon fails
            self.sprite = self.canvas.create_oval(
            self.position[0]-5, self.position[1]-5,
            self.position[0]+5, self.position[1]+5,
            fill=self.color,
            tags="agent"
        )
        self.canvas.lift(self.sprite)
        # depth varibles
        self.depth_preferd = [10, 20]
        self.depth_min = 5
        self.depth_max = 30

        # Search parameters
        self.grid = np.array(grid)
        self.ROW, self.COL = self.grid.shape
        self.grid = grid
        self.path = None

        #Grid and A* debug
        self.a_star_search()
        #print(f"Grid shape: {self.ROW} x {self.COL}")
        #print(f"Running A* from {spawn} to {self.dest}")
        #print(f"A* path result: {self.path}")

        # Check if agent has a path, if not fallback to the direct destination (either the initalized taget)
        # or the hard coded fallback cell
        if self.path is None or len(self.path) == 0:
            # print(f"No path found or path empty, using direct destination")
            tmp = self.grid[self.dest[0]][self.dest[1]]
            self.next_target = tmp
            # print(f"Next target (direct): pos_x={tmp.pos_x}, pos_y={tmp.pos_y}")
        else:
            tmp = self.path[0]
            self.next_target = self.grid[tmp[0]][tmp[1]]
            # print(f"Next target from path[0]: {tmp} -> pos_x={self.next_target.pos_x}, pos_y={self.next_target.pos_y}")

        # Debug
        #print(f"=== END SEEKER INIT DEBUG ===\n")
        #print(spawn, " Debugging spawn")

    #Method used to get the direction to the target
    def getTargetDir(self) -> list:
        #Grab target position
        target_x = self.next_target.pos_x
        target_y = self.next_target.pos_y
        #print(f'target: {target_x}x{target_y}') DEBUGGGG
        # print(f'pos:{self.position}')
        # Calculate our new x and y position based on the targets position and our current position
        new_x = target_x - self.position[0]
        new_y = target_y - self.position[1]
        new_vector = np.array([new_x, new_y])
        magnitude = np.linalg.norm(new_vector)
        unit_vector = 0

        #get the next depth
        # current_depth = self.map.depth_loc(x=self.position[0], y=self.position[1])

        # print(f'mag:{magnitude}')
       
        if(magnitude == 0):
            if not self.path:
                 #Check if the taget is destroyed 
                # print("target is destroyed")
                #Set our unit vector to 0 to stop movement
                unit_vector = [0, 0]
                self.reset()
                return unit_vector
            else:
                #Pops the wayoint from the path
                self.path.pop(0)
                # Defensive: check if path is empty before accessing
                if not self.path or len(self.path) == 0:
                    #If path is empty return 0 (to stop movement)
                    # print("No path available")
                    return [0, 0]
                #If waypoints remain, set the next target to the waypoint
                tmp = self.path[0]
                self.next_target = self.grid[tmp[0]][tmp[1]]
                # print(f'next target: {self.next_target}')
                #Return 0 still for this step, agent will move to target on next step
                unit_vector = [0, 0]
        else:
            #If magnitude isnt 0, calculate new unit vector for movement
            unit_vector = new_vector / magnitude
        # print(f'unitvector{unit_vector}')
        return unit_vector
    
    #Step function that is used to move the agent towards its target
    def step(self):
        """simple move towards target set function"""
        # Check if agent is dead
        if not self.status:
            return
        
        # Update target destination dynamically
        targets = self.model.get_target_positions()

        # NO TARGETS REMAIN - STOP MOVEMENT
        if not targets:
            # print(f"Agent {self.unique_id} stopping - no valid targets remain")
            self.is_complete = True
            #Change color to indicate idle state
            try:
                self.canvas.itemconfig(self.oval, fill="gray")
            except Exception:
                pass
            return  # Exit step() - don't move

        # Find closest target to current position
        closest_target = None
        min_distance = float('inf')
        
        for target in targets:
            target_pixel_x = target[0]
            target_pixel_y = target[1]
            
            # Calculate distance from current position to this target
            distance = ((target_pixel_x - self.position[0])**2 + 
                    (target_pixel_y - self.position[1])**2)**0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_target = target
        
        # Use the closest target
        target_pixel_x = closest_target[0]
        target_pixel_y = closest_target[1]
        
        target_grid_col = int(target_pixel_x / self.cell_size)
        target_grid_row = int(target_pixel_y / self.cell_size)
        new_dest = [target_grid_row, target_grid_col]
        
        # Update if target moved OR if next_target is invalid
        # Update if target moved OR if next_target is invalid
        if self.dest != new_dest or not hasattr(self, 'next_target') or self.next_target is None:
            old_dest = self.dest
            self.dest = new_dest
            
            # ✅ Calculate current grid position
            current_grid_col = int(self.position[0] / self.cell_size)
            current_grid_row = int(self.position[1] / self.cell_size)
            current_grid_col = max(0, min(current_grid_col, self.COL - 1))
            current_grid_row = max(0, min(current_grid_row, self.ROW - 1))
            
            # ✅ Update spawn to current position
            self.spawn = [current_grid_col, current_grid_row]
            
            # ✅ Recalculate A* path
            print(f"Agent {self.unique_id}: Recalculating path from {self.spawn} to {self.dest}")
            self.a_star_search()
            
            # ✅ Use FIRST WAYPOINT from path, not final destination
            if self.path and len(self.path) > 0:
                tmp = self.path[0]
                self.next_target = self.grid[tmp[0]][tmp[1]]  # ← Waypoint, not destination!
                print(f"  Following path with {len(self.path)} waypoints")
            else:
                # No path found
                self.next_target = self.grid[new_dest[0]][new_dest[1]]
                print(f"  WARNING: No path found!")
            
            if self.dest != old_dest:
                print(f"Target moved from {old_dest} to {self.dest}")
        
        # Get our new direction by getting the direction to the target
        new_direction = self.getTargetDir()
        
        # Check if we're still moving
        if new_direction is None or (new_direction[0] == 0 and new_direction[1] == 0):
            # print(f"Agent {self.unique_id} stopped - no valid direction")
            return
        
        # Obtain our new coordinates via our speed * our direction
        new_x = self.Speed * (np.round(new_direction[0]).astype(int))
        new_y = self.Speed * (np.round(new_direction[1]).astype(int))
        
        # Set our position to our new coordinates
        self.position = np.array([self.position[0] + new_x, self.position[1] + new_y])
        # Move the canvas oval in proportion
        #self.canvas.move(self.oval, new_x, new_y)     
       #no more oval 
        self.canvas.move(self.sprite, new_x, new_y)
        
        # Salinity data
        """"
        nearest_salinity_point = self.salinity.find_nearest_point(self.position)
        if nearest_salinity_point:
            top_salinity = nearest_salinity_point["top_salinity"]
            bottom_salinity = nearest_salinity_point["bottom_salinity"]
            print(f"Agent at position {self.position} is near salinity point {nearest_salinity_point['coordinates']}")
            print(f"Top Salinity in ppt: {top_salinity}, Bottom Salinity in ppt: {bottom_salinity}")
        else:
            print(f"No salinity data found for agent at position {self.position}")     

        # Temperature data
        nearest_temp_point = self.temp.find_nearest_point(self.position)
        if nearest_temp_point:
            top_temp = nearest_temp_point["top_temp"]
            bottom_temp = nearest_temp_point["bottom_temp"]
            print(f"Agent at position {self.position} is near temp point {nearest_temp_point['coordinates']}")
            print(f"Top temp in C: {top_temp}, Bottom temp in C: {bottom_temp}")
        else:
            print(f"No temp data found for agent at position {self.position}")
        
        #print(f"=== END AGENT {self.unique_id} STEP ===\n")
    """
    #A star search algorithm
    def a_star_search(self):
        """A* search algorithm"""
        # FIX: self.spawn is [col, row] but A* needs [row, col]
        start_row = self.spawn[1]
        start_col = self.spawn[0]

        # Check if the source and destination are valid
        if not self.is_valid(start_row, start_col) or not self.is_valid(self.dest[0], self.dest[1]):
            print("Source or destination is invalid")
            return

        # Check if the source and destination are unblocked
        if not self.is_unblocked(start_row, start_col) or not self.is_unblocked(self.dest[0], self.dest[1]):
            print("Source or the destination is blocked")
            return

        # Check if we are already at the destination
        if self.is_destination(start_row, start_col):
            print("We are already at the destination")
            return

        # Initialize the closed list (visited cells)
        closed_list = [[False for _ in range(self.COL)] for _ in range(self.ROW)]
        # Initialize the details of each cell
        cell_details = [[Cell(id=0) for _ in range(self.COL)] for _ in range(self.ROW)]

        # Initialize the start cell details using corrected [row, col]
        i = start_row
        j = start_col
        cell_details[i][j].f = 0
        cell_details[i][j].g = 0
        cell_details[i][j].h = 0
        cell_details[i][j].parent_row_i = i
        cell_details[i][j].parent_col_j = j

        # Initialize the open list (cells to be visited) with the start cell
        open_list = []
        heapq.heappush(open_list, (0.0, i, j))

        # Initialize the flag for whether destination is found
        found_dest = False

        # Main loop of A* search algorithm
        while len(open_list) > 0:
            # Pop the cell with the smallest f value from the open list
            p = heapq.heappop(open_list)

            # Mark the cell as visited
            i = p[1]
            j = p[2]
            closed_list[i][j] = True

            # For each direction, check the successors
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dir in directions:
                new_i = i + dir[0]
                new_j = j + dir[1]

                # If the successor is valid, unblocked, and not visited
                if self.is_valid(new_i, new_j) and self.is_unblocked(new_i, new_j) and not closed_list[new_i][new_j]:
                    # If the successor is the destination
                    if self.is_destination(new_i, new_j):
                        # Set the parent of the destination cell
                        cell_details[new_i][new_j].parent_row_i = i
                        cell_details[new_i][new_j].parent_col_j = j
                        print("The destination cell is found")
                        # Trace and print the path from source to destination
                        self.trace_path(cell_details, self.dest)
                        found_dest = True
                        return
                    else:
                        # Calculate the new f, g, and h values
                        g_new = cell_details[i][j].g + 1.0
                        h_new = self.calculate_h_value(new_i, new_j)
                        f_new = g_new + h_new

                        # If the cell is not in the open list or the new f value is smaller
                        if cell_details[new_i][new_j].f == float('inf') or cell_details[new_i][new_j].f > f_new:
                            # Add the cell to the open list
                            heapq.heappush(open_list, (f_new, new_i, new_j))
                            # Update the cell details
                            cell_details[new_i][new_j].f = f_new
                            cell_details[new_i][new_j].g = g_new
                            cell_details[new_i][new_j].h = h_new
                            cell_details[new_i][new_j].parent_row_i = i
                            cell_details[new_i][new_j].parent_col_j = j

        # If the destination is not found after visiting all cells
        if not found_dest:
            self.path = []
            print("Failed to find the destination cell")

    #Helper function of the A* algorithm to trace the movement
    def trace_path(self, cell_details, dest):
        """Trace the movement of the a*"""
        # print("The Path is ")
        path = []
        row = dest[0]
        col = dest[1]

        # Trace the path from destination to source using parent cells
        while not (cell_details[row][col].parent_row_i == row and cell_details[row][col].parent_col_j == col):
            path.append((row, col))
            temp_row = cell_details[row][col].parent_row_i
            temp_col = cell_details[row][col].parent_col_j
            row = temp_row
            col = temp_col

        # Add the source cell to the path
        path.append((row, col))
        # Reverse the path to get the path from source to destination
        path.reverse()
        self.path = path

        # Print the path
        # for i in path:
        #     print("->", i, end=" ")
        # print()

    #Helper to check if a cell is valid (in the bounds)
    def is_valid(self, row, col):
        """Check if a cell is valid"""
        return (row >= 0) and (row < self.ROW) and (col >= 0) and (col < self.COL)

    # Helper to check if a cell is unblocked
    def is_unblocked(self, row, col):
        """check if cell is unblocked"""
        return self.grid[row][col].id != 1

    #Check if the cell is the destination
    def is_destination(self, row, col):
        """check if cell is the destination"""
        return row == self.dest[0] and col == self.dest[1]

    #calculate the guess value of a cell, Euclidean
    def calculate_h_value(self, row, col):
        """calculate the guess value of a cell, Euclidean"""
        return ((row - self.dest[0]) ** 2 + (col - self.dest[1]) ** 2) ** 0.5

    # Cleanup function called by reset sim to clear the oval
    def cleanup(self):
        """Remove canvas items created by this agent."""
        try:
            if hasattr(self, "oval") and self.oval is not None:
                try:
                    self.canvas.delete(self.oval)
                except Exception:
                    pass
#For sprites, no longer ovals
            if hasattr(self, "sprite") and self.sprite is not None:
                try:
                    self.canvas.delete(self.sprite)
                except Exception:
                    pass
        except Exception:
            pass

    def reset(self):
        """Reset the agent for another run"""
        print("i am reseting")
        spawn = self.spawn
        self.position = [self.grid[spawn[1]][spawn[0]].pos_x, self.grid[spawn[1]][spawn[0]].pos_y]
        tmp = self.path[0]
        self.next_target = self.grid[tmp[0]][tmp[1]]
        self.status = True