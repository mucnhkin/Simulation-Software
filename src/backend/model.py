from mesa_geo import GeoAgent, GeoSpace
from mesa import Model
from mesa.time import RandomActivation

class WaterAgent(GeoAgent):
    def __init__(self, unique_id, model, geom):
        super().__init__(unique_id, model, geom)

class WaterModel(Model):
    def __init__(self, geo_df):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.space = GeoSpace()

        # Create agents from geometries in GeoDataFrame
        for i, row in geo_df.iterrows():
            agent = WaterAgent(i, self, row.geometry)
            self.schedule.add(agent)
            self.space.add_agent(agent)

    def step(self):
        self.schedule.step()
