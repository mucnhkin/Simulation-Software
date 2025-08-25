import tkinter as tk
import numpy as np
import pandas as pd
import mesa
import geopandas as gpd
from shapely.geometry import Point, shape





class UUVAgent(mesa.Agent):
    """UUV agent testing class"""

    def __init__(self, model, spawn, target, canvas, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.position = spawn #(x,y)
        self.target = target
        self.canvas = canvas
        self.oval = self.canvas.create_oval(self.position[0],self.position[1], self.position[0]+10, self.position[1]+10, fill='orange', tags='agent')
        self.canvas.lift(self.oval)
        self.getTargetDir()
    
    def getTargetDir(self):
        new_x = self.target[0] - self.position[0]
        new_y = self.target[1] - self.position[1]
        new_vector = np.array([new_x, new_y])
        magnitude = np.linalg.norm(new_vector)
        unit_vector =0
        if(magnitude == 0):
            unit_vector = 0
        else:
            unit_vector = new_vector / magnitude
        return unit_vector
        


    def move_to_target(self):
        """simple move towards target set function"""
        new_direction = self.getTargetDir()
        if np.all(self.target != self.position):
            new_x = np.round(new_direction[0]).astype(int)
            new_y = np.round(new_direction[1]).astype(int)
            self.position = np.array([self.position[0] + new_x, self.position[1]+new_y])
            self.canvas.move(self.oval, new_x, new_y)     