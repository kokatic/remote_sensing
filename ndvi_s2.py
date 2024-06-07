import rasterio
import numpy as np

def calculate_ndvi(red_band_path, nir_band_path, output_path):
    # Open the red and NIR bands as rasterio datasets
    with rasterio.open(red_band_path) as red_dataset:
        red = red_dataset.read(1).astype('float32')
        profile = red_dataset.profile

    with rasterio.open(nir_band_path) as nir_dataset:
        nir = nir_dataset.read(1).astype('float32')

    # Avoid division by zero errors
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate NDVI
    ndvi = (nir - red) / (nir + red)
    
    # Update the profile for the NDVI output
    profile.update(dtype=rasterio.float32, count=1, driver='GTiff', compress='lzw')

    # Write the NDVI result to a new GeoTIFF file
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndvi, 1)


# Example file paths
red_band_path = 'data/T32SKC_20240430T102021_B04_10m.jp2'  # Red band
nir_band_path = 'data/T32SKC_20240430T102021_B08_10m.jp2'  # Near-Infrared band
output_path = 'output/ndvi.tif'  # Output NDVI file

calculate_ndvi(red_band_path, nir_band_path, output_path)
