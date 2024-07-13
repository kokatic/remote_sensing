import rasterio
import numpy as np

def calculate_evi(red_band_path, nir_band_path, blue_band_path, output_path):
    try:
        # Open the red, NIR, and blue bands as rasterio datasets
        with rasterio.open(red_band_path) as red_dataset, \
             rasterio.open(nir_band_path) as nir_dataset, \
             rasterio.open(blue_band_path) as blue_dataset:

            # Read data from rasterio datasets
            red = red_dataset.read(1, masked=True).astype('float32')
            nir = nir_dataset.read(1, masked=True).astype('float32')
            blue = blue_dataset.read(1, masked=True).astype('float32')

            # Calculate EVI
            G = 2.5
            C1 = 6
            C2 = 7.5
            L = 1
            epsilon = 1e-6  # Small epsilon value to avoid division by zero
            denominator = nir + C1 * red - C2 * blue + L
            evi = np.where(denominator != 0, G * ((nir - red) / denominator), np.nan)

            # Clip EVI values to range [-1, 1]
            evi = np.clip(evi, -1, 1)

            # Update the profile for the EVI output
            profile = red_dataset.profile
            profile.update(dtype=rasterio.float32, count=1, driver='GTiff', compress='lzw')

            # Write the EVI result to a new JP2 file
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(evi, 1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
# Example file paths
red_band_path = 'data/Toshka/S2A_MSIL2A_20240227T082911/T36QUL_20240227T082911_B04_10m.jp2'  # Red band
nir_band_path = 'data/Toshka/S2A_MSIL2A_20240227T082911/T36QUL_20240227T082911_B08_10m.jp2'  # Near-Infrared band
blue_band_path = 'data/Toshka/S2A_MSIL2A_20240227T082911/T36QUL_20240227T082911_B02_10m.jp2'  # Blue band
output_path = 'output/evi.tif'  # Output EVI file

calculate_evi(red_band_path, nir_band_path, blue_band_path, output_path)
