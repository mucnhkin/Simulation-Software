import tkinter as tk
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, shape
import os


class MapControl():

    def __init__(self, canvas, shallow_color =None, deep_color = None, shape_path = None):
        
        # required 
        self.canvas = canvas
        self.polygon_ids={}
        self.selected_polygon_id = None
        self.min_depth = 0
        self.max_depth = 0

        # testing
        self.canvas_width = 700
        self.canvas_height = 700

        #set color
        if shallow_color == None :
            self.shallow_color = (170, 201, 250)
        else:
            self.shallow_color = shallow_color

        if deep_color == None:
            self.deep_color =(0, 0, 26)
        else:
            self.deep_color = deep_color

        self.map_init(shape_path)
        
    

    def depth_loc(self, x, y):
        """
        Returns the depth of the area polygon
        """
        self.selected_polygon_id

        closest_items = self.canvas.find_closest(x+5, y+5) 

        # if closet item was found
        if closest_items:
            clicked_item_id = closest_items[0]

            if clicked_item_id in self.polygon_ids:

            
                # If a polygon was previously selected, restore its original color
                if self.selected_polygon_id and self.selected_polygon_id in self.polygon_ids:
                    original_color = self.polygon_ids[self.selected_polygon_id]['color']
                    self.canvas.itemconfigure(self.selected_polygon_id, fill=original_color)

                # Highlight
                self.canvas.itemconfigure(clicked_item_id, width=0, fill="red")
                self.selected_polygon_id = clicked_item_id
            
                # Print information
                print(f"Clicked on polygon with ID: {clicked_item_id}")
                print(f"Depth: {self.polygon_ids[clicked_item_id]['depth1']}, {self.polygon_ids[clicked_item_id]['depth2']}")


    def set_depth_color(self, current_depth, min_d, max_d):
        """
        Calculates a color in a gradient from light-blue to dark blue.
        """
        # normilize values, 0 for light, 1 for dark
        if max_d == min_d:
            normalized_depth = 0
        else:
            normalized_depth = (current_depth - min_d) / (max_d - min_d)
    
        # change the base rgb values
        r = int(self.shallow_color[0] + normalized_depth * (self.deep_color[0] - self.shallow_color[0]))
        g = int(self.shallow_color[1] + normalized_depth * (self.deep_color[1] - self.shallow_color[1]))
        b = int(self.shallow_color[2] + normalized_depth * (self.deep_color[2] - self.shallow_color[2]))

        # Convert the RGB to hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def map_init(self, shp_path):
        """
        Setups the map and draws it to the canvas
        """
        if shp_path == None:
            print("No map selected")
            return

        shape_path = shp_path
        self.shp = gpd.read_file(shape_path)
        self.min_depth = self.shp['DRVAL2'].min()
        self.max_depth = self.shp['DRVAL2'].max()
        minx, miny, maxx, maxy = self.shp.total_bounds


        # Calculate the geographic width and height
        geo_width = maxx - minx
        geo_height = maxy - miny

        buffer = 20
        x_scale = (self.canvas_width - buffer) / geo_width
        y_scale = (self.canvas_height - buffer) / geo_height

        scale = min(x_scale, y_scale)

        x_offset = (self.canvas_width - geo_width * scale) / 2
        y_offset = (self.canvas_height - geo_height * scale) / 2

        for index, row in self.shp.iterrows():
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
                    new_x = (x_geo - minx) * scale # + x_offset
                    new_y = (maxy - y_geo) * scale # + y_offset
                    scaled_coords.extend([new_x, new_y])
                # get depth color
                fill_color = self.set_depth_color(depth2, self.min_depth, self.max_depth)
                # Draw the scaled polygon on the canvas and store in dictinary
                id=self.canvas.create_polygon(scaled_coords, fill=fill_color, width=0, tags="map")
                self.polygon_ids[id]={"depth1": depth1, "depth2": depth2, "color": fill_color}
        