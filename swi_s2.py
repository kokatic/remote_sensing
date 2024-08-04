import rasterio
import numpy as np

def calculate_swi(nir_band_path, swir_band_path, output_path):
    with rasterio.open(nir_band_path) as nir_dataset:
        nir = nir_dataset.read(1).astype('float32')
        profile = nir_dataset.profile
    with rasterio.open(swir_band_path) as swir_dataset:
        swir = swir_dataset.read(1).astype('float32')
    np.seterr(divide='ignore', invalid='ignore')
    swi = (nir - swir) / (nir + swir)  
    profile.update(dtype=rasterio.float32, count=1, driver='GTiff', compress='lzw')
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(swi, 1)


# Example file paths
nir_band_path = 'data/20m/T32SKC_20240430T102021_B8A_20m.jp2'  # Band 8 (NIR)
swir_band_path = 'data/20m/T32SKC_20240430T102021_B11_20m.jp2'  # Band 11 (SWIR)
output_path = 'output/swi.tif'  # Output NDVI file

calculate_swi(nir_band_path, swir_band_path, output_path)
