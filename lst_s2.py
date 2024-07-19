import rasterio
import numpy as np

def calculate_lst(green_band_path, nir_band_path, red_band_path, output_path):
    # Open the green, NIR, and red bands as rasterio datasets
    with rasterio.open(green_band_path) as green_dataset:
        green = green_dataset.read(1).astype('float32')
        profile = green_dataset.profile

    with rasterio.open(nir_band_path) as nir_dataset:
        nir = nir_dataset.read(1).astype('float32')
    
    with rasterio.open(red_band_path) as red_dataset:
        red = red_dataset.read(1).astype('float32')
    
    # Avoid division by zero errors
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate NDVI
    ndvi = (nir - red) / (nir + red)
    
    # Estimate Emissivity
    emissivity = 0.004 * np.power(ndvi, 2) + 0.986
    
    # Assume a constant brightness temperature (BT) for simplicity
    # This is a simplification and should ideally come from thermal data
    bt = 300  # Kelvin, arbitrary constant temperature
    
    # Calculate LST using the Stefan-Boltzmann law and emissivity
    lst = bt / (1 + (0.00115 * bt / 1.438) * np.log(emissivity)) - 273.15  # Convert to Celsius
    
    # Update the profile for the LST output
    profile.update(dtype=rasterio.float32, count=1, driver='GTiff', compress='lzw')

    # Write the LST result to a new GeoTIFF file
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(lst, 1)

# Example file paths
green_band_path = 'data/portugal/T29SNB_20230807T112119_B03_10m.jp2'  # Green band
nir_band_path = 'data/portugal/T29SNB_20230807T112119_B08_10m.jp2'    # Near-Infrared band
red_band_path = 'data/portugal/T29SNB_20230807T112119_B04_10m.jp2'    # Red band
output_path = 'output/lst_pt.tif'  # Output LST file

calculate_lst(green_band_path, nir_band_path, red_band_path, output_path)
