import tkinter as tk
import numpy as np
import pandas as pd
import mesa

from . import agent

class UUVModel(mesa.Model):
    """UUV model testing class"""
    
    def __init__(self, n, canvas,*args, seed = None, rng = None, **kwargs):
        super().__init__(*args, seed=seed, rng=rng, **kwargs)
        self.num_agents = n
        self.canvas = canvas
        agent.UUVAgent.create_agents(model=self, n=n, canvas=self.canvas)

    def step(self):
        """advance model by one step"""
        self.agents.do("move_to_target")
