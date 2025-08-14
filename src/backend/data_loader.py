import geopandas as gpd
import os

def load_coastline(data_dir):
    filepath = os.path.join(data_dir, "ne_10m_coastline.shp")
    coastline = gpd.read_file(filepath)
    return coastline

def load_ocean(data_dir):
    filepath = os.path.join(data_dir, "ne_10m_ocean.shp")
    ocean = gpd.read_file(filepath)
    return ocean


def load_port(data_dir):
    filepath = os.path.join(data_dir, "ne_10m_ports.shp")
    port = gpd.read_file(filepath)
    return port