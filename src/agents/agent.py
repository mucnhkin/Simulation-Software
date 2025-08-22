import tkinter as tk
import numpy as np
import pandas as pd
import mesa
import geopandas as gpd
from shapely.geometry import Point, shape





class UUVAgent(mesa.Agent):
    """UUV agent testing class"""

    def __init__(self, model, canvas, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.position = Point(0, 0)
        self.canvas = canvas
        self.target = Point(25, 25)
        self.oval = self.canvas.create_oval(self.position.x,self.position.y, self.position.x+20, self.position.y+20, fill='orange', tags='agent')
        self.canvas.lift(self.oval)
    
    def move_to_target(self):
        """simple move towards target set function"""
        
        if self.position != self.target:  
            new_x = self.position.x
            new_y = self.position.y  
            if self.position.x > self.target.x:
                new_x -= 1
            elif self.position.x < self.target.x:
                new_x += 1

            if self.position.y > self.target.y:
                new_y -= 1
            elif self.position.y < self.target.y:
                new_y += 1
            self.position = Point(new_x, new_y)
            self.canvas.move(self.oval, new_x, new_y)
    
        
        print(f'{self.position}')