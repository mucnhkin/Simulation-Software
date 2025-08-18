import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.tri as mtri

import pandas as pd
import numpy as np

test = "path"
shp = gpd.read_file(test)

fig, ax = plt.subplots(figsize=(10,15))

shp.plot(ax=ax)

plt.show()