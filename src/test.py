import rasterio
import numpy as np
import matplotlib.pyplot as plt

# Path to your downloaded GeoTIFF
tif_path = "Simulation-Software/data/TIFF/pearl_harbor.tiff"

# Open the dataset
with rasterio.open(tif_path) as dataset:
    bathy_data = dataset.read(1)  # Read the first (and usually only) band
    profile = dataset.profile      # Metadata (resolution, CRS, etc.)
    transform = dataset.transform  # Geo transform for converting pixel <-> coords

# Replace "no data" values with NaN for easier handling
bathy_data = np.where(bathy_data == profile['nodata'], np.nan, bathy_data)

print("Shape:", bathy_data.shape)
print("CRS:", profile['crs'])
print("Resolution:", profile['transform'][0], "meters per pixel")

with rasterio.open(tif_path) as dataset:
    bounds = dataset.bounds
    print(bounds)

# Quick visualization
plt.imshow(bathy_data)
plt.colorbar(label="Depth (meters)")
plt.title("NOAA Bathymetry")
plt.show()
