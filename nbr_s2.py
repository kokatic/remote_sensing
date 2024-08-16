import rasterio
import numpy as np

def calculate_nbr(nir_band_path, swir_band_path, output_path):
    with rasterio.open(nir_band_path) as nir_dataset:
        nir = nir_dataset.read(1).astype('float32')
        profile = nir_dataset.profile

    with rasterio.open(swir_band_path) as swir_dataset:
        swir = swir_dataset.read(1).astype('float32')

    np.seterr(divide='ignore', invalid='ignore')

    # Calculate NBR
    nbr = (nir - swir) / (nir + swir)

    # Update the profile for the NBR output
    profile.update(dtype=rasterio.float32, count=1, driver='GTiff', compress='lzw')

    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(nbr, 1)

# Example file paths
nir_band_path = 'data/algeria/T31SFA_20230822T102609_B8A_20m.jp2'   # Band 8 (NIR)
swir_band_path = 'data/algeria/T31SFA_20230822T102609_B12_20m.jp2'  # Band 12 (SWIR)
output_path = 'output/nbr2.tif'  # Output NBR file

calculate_nbr(nir_band_path, swir_band_path, output_path)
