import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def read_band(file_path):
    """Read a single band from a GeoTIFF image and return it as a numpy array along with the metadata."""
    with rasterio.open(file_path) as src:
        band = src.read(1)  # Read the first (and only) band
        meta = src.meta
    return band, meta

def calculate_ndvi(nir, red):
    """Calculate NDVI from NIR and Red bands."""
    ndvi = (nir - red) / (nir + red)
    return ndvi

def calculate_ndwi(nir, green):
    """Calculate NDWI from NIR and Green bands."""
    ndwi = (green - nir) / (green + nir)
    return ndwi

def detect_changes(index1, index2, threshold):
    """Detect changes between two index images."""
    diff = index2 - index1
    changes = np.abs(diff) > threshold
    return changes, diff

def main(red1_path, nir1_path, green1_path, red2_path, nir2_path, green2_path, output_path, ndvi_threshold=0.3, ndwi_threshold=0.2):
    # Read the bands for the first image
    red1, meta1 = read_band(red1_path)
    nir1, _ = read_band(nir1_path)
    green1, _ = read_band(green1_path)
    
    # Read the bands for the second image
    red2, _ = read_band(red2_path)
    nir2, _ = read_band(nir2_path)
    green2, _ = read_band(green2_path)
    
    # Calculate NDVI and NDWI for both images
    ndvi1 = calculate_ndvi(nir1, red1)
    ndvi2 = calculate_ndvi(nir2, red2)
    
    ndwi1 = calculate_ndwi(nir1, green1)
    ndwi2 = calculate_ndwi(nir2, green2)
    
    # Detect changes and calculate differences
    ndvi_changes, ndvi_diff = detect_changes(ndvi1, ndvi2, ndvi_threshold)
    ndwi_changes, ndwi_diff = detect_changes(ndwi1, ndwi2, ndwi_threshold)
    
    # Create an empty array to store combined changes
    combined_changes = np.zeros(ndvi_changes.shape, dtype=np.uint8)
    
    # Assign different values for different types of changes
    combined_changes[ndvi_changes] = 1  # Value 1 for vegetation changes
    combined_changes[ndwi_changes] = 2  # Value 2 for water changes
    combined_changes[ndvi_changes & ndwi_changes] = 3  # Value 3 for both changes
    
    # Save the change detection result
    meta1.update(dtype=rasterio.uint8, count=1)
    with rasterio.open(output_path, 'w', **meta1) as dst:
        dst.write(combined_changes, 1)
    
    # Create a colormap with distinct colors
    cmap = ListedColormap(['black', 'green', 'blue', 'yellow'])
    bounds = [0, 1, 2, 3, 4]
    norm = plt.Normalize(vmin=0, vmax=4)
    
    # Visualize the result
    plt.figure(figsize=(10, 10))
    plt.imshow(combined_changes, cmap=cmap, norm=norm)
    cbar = plt.colorbar(ticks=[0.5, 1.5, 2.5, 3.5], boundaries=bounds)
    cbar.set_ticklabels(['No Change', 'Vegetation Change', 'Water Change', 'Both Changes'])
    plt.title('NDVI and NDWI Change Detection Result')
    plt.show()


# Example usage
red1_path = 'data\Toshka\S2A_MSIL2A_20170223T082931\T36QUL_20170223T082931_B03_10m.jp2'
nir1_path = 'data\Toshka\S2A_MSIL2A_20170223T082931\T36QUL_20170223T082931_B04_10m.jp2'
green1_path = 'data\Toshka\S2A_MSIL2A_20170223T082931\T36QUL_20170223T082931_B08_10m.jp2'
red2_path = 'data\Toshka\S2A_MSIL2A_20240227T082911\T36QUL_20240227T082911_B03_10m.jp2'
nir2_path = 'data\Toshka\S2A_MSIL2A_20240227T082911\T36QUL_20240227T082911_B04_10m.jp2'
green2_path = 'data\Toshka\S2A_MSIL2A_20240227T082911\T36QUL_20240227T082911_B08_10m.jp2'
output_path = 'output\changes_ndvi_ndwi.tif'
main(red1_path, nir1_path, green1_path, red2_path, nir2_path, green2_path, output_path)
