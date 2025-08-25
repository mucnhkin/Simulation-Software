import tkinter as tk
import numpy as np
import pandas as pd
import mesa



from . import agent

class UUVModel(mesa.Model):
    """UUV model testing class"""
    
    def __init__(self, n, spawns, targets, canvas,*args, seed = None, rng = None, **kwargs):
        super().__init__(*args, seed=seed, rng=rng, **kwargs)
        self.num_agents = n
        self.canvas = canvas
        self.spawns = spawns
        self.targets = targets

        #create agents
        for _ in range(self.num_agents):
            tmp_spwn = self.spawns[_]
            agent.UUVAgent.create_agents(model=self, n=1, target=self.targets, spawn=tmp_spwn, canvas=self.canvas)

    def step(self):
        """advance model by one step"""
        self.agents.do("move_to_target")
