import rasterio
import numpy as np

def calculate_mndwi(green_band_path, nir_band_path, output_path):
    # Open the green and NIR bands as rasterio datasets
    with rasterio.open(green_band_path) as green_dataset:
        green = green_dataset.read(1).astype('float32')
        profile = green_dataset.profile

    with rasterio.open(nir_band_path) as nir_dataset:
        nir = nir_dataset.read(1).astype('float32')

    # Avoid division by zero errors
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate MNDWI
    mndwi = (nir - green) / (nir + green)
    
    # Update the profile for the MNDWI output
    profile.update(dtype=rasterio.float32, count=1, driver='GTiff', compress='lzw')

    # Write the MNDWI result to a new GeoTIFF file
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(mndwi, 1)

# Example file paths
green_band_path = 'data/Toshka/S2A_MSIL2A_20240227T082911/T36QUL_20240227T082911_B03_10m.jp2' 
nir_band_path = 'data/Toshka/S2A_MSIL2A_20240227T082911/T36QUL_20240227T082911_B08_10m.jp2'  # Near-Infrared band


output_path = 'output/gndvi.tif'  # Output MNDWI file

calculate_mndwi(green_band_path, nir_band_path, output_path)