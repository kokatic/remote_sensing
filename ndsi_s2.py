import rasterio
import numpy as np

def calculate_ndsi(nir_band_path, swir_band_path, output_path):
    # Open the NIR and SWIR bands as rasterio datasets
    with rasterio.open(nir_band_path) as nir_dataset:
        nir = nir_dataset.read(1).astype('float32')
        profile = nir_dataset.profile

    with rasterio.open(swir_band_path) as swir_dataset:
        swir = swir_dataset.read(1).astype('float32')

    # Avoid division by zero errors
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate NDSI
    ndsi = (nir - swir) / (nir + swir)
    
    # Update the profile for the NDSI output
    profile.update(dtype=rasterio.float32, count=1, driver='GTiff', compress='lzw')

    # Write the NDSI result to a new GeoTIFF file
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndsi, 1)

# Example file paths
nir_band_path = 'data/Toshka/S2A_MSIL2A_20240227T082911/20/T36QUL_20240227T082911_B8A_20m.jp2'  # NIR band
swir_band_path = 'data/Toshka/S2A_MSIL2A_20240227T082911/20/T36QUL_20240227T082911_B11_20m.jp2' # SWIR band
output_path = 'output/ndsi.tif'  # Output NDSI file

# Calculate NDSI
calculate_ndsi(nir_band_path, swir_band_path, output_path)

