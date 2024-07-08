import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def read_band(file_path):
    """Read a single band from a GeoTIFF image and return it as a numpy array along with the metadata."""
    with rasterio.open(file_path) as src:
        band = src.read(1).astype('float32') # Read the first (and only) band
        meta = src.profile
    return band, meta

def calculate_ndvi(nir, red, ndvi_threshold):
    """
    Calculate NDVI from NIR and Red bands and apply thresholding.

    Parameters:
    - nir: numpy array, Near Infrared band
    - red: numpy array, Red band
    - ndvi_threshold: float, threshold value for NDVI

    Returns:
    - ndvi_changes: numpy boolean array, True where NDVI change exceeds threshold
    - ndvi: numpy array, calculated NDVI
    """
    # Avoid division by zero errors
    ndvi = (nir - red) / (nir + red)
    ndvi_changes = (ndvi > ndvi_threshold)
    return ndvi_changes, ndvi

def calculate_ndwi(nir, green, ndwi_threshold):
    """
    Calculate NDWI from NIR and Green bands and apply thresholding.

    Parameters:
    - nir: numpy array, Near Infrared band
    - green: numpy array, Green band
    - ndwi_threshold: float, threshold value for NDWI

    Returns:
    - ndwi_changes: numpy boolean array, True where NDWI change exceeds threshold
    - ndwi: numpy array, calculated NDWI
    """
    ndwi = (green - nir) / (green + nir)
    ndwi_changes = (ndwi > ndwi_threshold)
    return ndwi_changes, ndwi

def detect_changes(index1_changes, index2_changes, threshold):
    """Detect changes between two boolean index images."""
    # XOR to find where changes occurred between index1 and index2
    diff = np.logical_xor(index1_changes, index2_changes)
    # Logical AND to combine diff with index2_changes to get significant changes
    changes = np.logical_and(diff, index2_changes)
    return changes, diff

def main(red1_path, nir1_path, green1_path, red2_path, nir2_path, green2_path, ndvi_output_path, ndwi_output_path, combined_output_path, ndvi_threshold=0.22, ndwi_threshold=0):
    # Read the bands for the first image
    red1, meta = read_band(red1_path)
    nir1, _ = read_band(nir1_path)
    green1, _ = read_band(green1_path)
    
    # Read the bands for the second image
    red2, _ = read_band(red2_path)
    nir2, _ = read_band(nir2_path)
    green2, _ = read_band(green2_path)
    
    # Calculate NDVI and NDWI for both images
    ndvi_changes1, ndvi1 = calculate_ndvi(nir1, red1, ndvi_threshold)
    ndvi_changes2, ndvi2 = calculate_ndvi(nir2, red2, ndvi_threshold)
    
    ndwi_changes1, ndwi1 = calculate_ndwi(nir1, green1, ndwi_threshold)
    ndwi_changes2, ndwi2 = calculate_ndwi(nir2, green2, ndwi_threshold)
    
    # Detect changes and calculate differences
    ndvi_changes, ndvi_diff = detect_changes(ndvi_changes1, ndvi_changes2, ndvi_threshold)
    ndwi_changes, ndwi_diff = detect_changes(ndwi_changes1, ndwi_changes2, ndwi_threshold)
    
    # Create an empty array to store combined changes
    combined_changes = np.zeros(ndvi_changes.shape, dtype=np.uint8)
    
    # Identify areas with both types of changes
    ndvi_only_changes = ndvi_changes & ~ndwi_changes
    ndwi_only_changes = ndwi_changes & ~ndvi_changes
    both_changes = ndvi_changes & ndwi_changes
    
    # Assign different values for different types of changes
    combined_changes[ndvi_only_changes] = 1  # Value 1 for NDVI changes only
    combined_changes[ndwi_only_changes] = 2  # Value 2 for NDWI changes only
    combined_changes[both_changes] = 3       # Value 3 for both NDVI and NDWI changes
    
    meta.update(dtype=rasterio.float32, count=1, driver='GTiff', compress='lzw')

    # Avoid division by zero errors
    np.seterr(divide='ignore', invalid='ignore')

    # Save the NDVI changes result
    with rasterio.open(ndvi_output_path, 'w', **meta) as dst:
        dst.write(ndvi_changes, 1)
        
    # Save the NDWI changes result
    with rasterio.open(ndwi_output_path, 'w', **meta) as dst:
        dst.write(ndwi_changes, 1)
    
    # Save the combined changes result
    with rasterio.open(combined_output_path, 'w', **meta) as dst:
        dst.write(combined_changes, 1)
    
    # Visualize the NDVI, NDWI, and combined changes
    cmap_ndvi = ListedColormap(['black', 'green'])
    cmap_ndwi = ListedColormap(['black', 'blue'])
    cmap_combined = ListedColormap(['black','yellow'])
    norm_combined = plt.Normalize(vmin=0, vmax=3)
    
    # Create a figure with three subplots
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    
    # Plot NDVI Changes
    im1 = axs[0].imshow(ndvi_changes, cmap=cmap_ndvi)
    axs[0].set_title('NDVI Changes')
    axs[0].set_aspect('auto')  # Adjust aspect ratio if necessary
    fig.colorbar(im1, ax=axs[0], ticks=[0, 1], boundaries=[0, 0.5, 1])
    
    # Plot NDWI Changes
    im2 = axs[1].imshow(ndwi_changes, cmap=cmap_ndwi)
    axs[1].set_title('NDWI Changes')
    axs[1].set_aspect('auto')  # Adjust aspect ratio if necessary
    fig.colorbar(im2, ax=axs[1], ticks=[0, 1], boundaries=[0, 0.5, 1])
    
    # Plot Combined Changes
    im3 = axs[2].imshow(combined_changes, cmap=cmap_combined, norm=norm_combined)
    axs[2].set_title('Combined Changes (NDVI and NDWI)')
    axs[2].set_aspect('auto')  # Adjust aspect ratio if necessary
    fig.colorbar(im3, ax=axs[2], ticks=[1,2,3], boundaries=[1, 1.5,3])
    
    plt.tight_layout()  # Adjust spacing between subplots
    
    plt.savefig('combined_changes_plot.png', dpi=300)  # Export combined changes plot as PNG
    
    plt.show()

# Example usage
green1_path = 'data\Toshka\S2A_MSIL2A_20170223T082931\T36QUL_20170223T082931_B03_10m.jp2'
red1_path   = 'data\Toshka\S2A_MSIL2A_20170223T082931\T36QUL_20170223T082931_B04_10m.jp2'
nir1_path   = 'data\Toshka\S2A_MSIL2A_20170223T082931\T36QUL_20170223T082931_B08_10m.jp2'
green2_path = 'data\Toshka\S2A_MSIL2A_20240227T082911\T36QUL_20240227T082911_B03_10m.jp2'
red2_path   = 'data\Toshka\S2A_MSIL2A_20240227T082911\T36QUL_20240227T082911_B04_10m.jp2'
nir2_path   = 'data\Toshka\S2A_MSIL2A_20240227T082911\T36QUL_20240227T082911_B08_10m.jp2'
ndvi_output_path = 'output\changes_ndvi.tif'
ndwi_output_path = 'output\changes_ndwi.tif'
combined_output_path = 'output\changes_ndvi_ndwi.tif'
main(red1_path, nir1_path, green1_path, red2_path, nir2_path, green2_path, ndvi_output_path, ndwi_output_path, combined_output_path)
