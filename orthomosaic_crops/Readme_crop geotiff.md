# README.md for GeoTIFF Cropping Tool

## Overview
This Python script is designed to handle the cropping of GeoTIFF images based on geographic points defined in a shapefile. It utilizes libraries such as `geopandas`, `rasterio`, and `shapely` to perform geographic operations and manipulate raster data.

## Features
- **Load Shapefile**: Reads a shapefile into a GeoDataFrame.
- **Bounding Box Creation**: Generates bounding boxes around each point in the GeoDataFrame.
- **Crop GeoTIFF**: Crops a GeoTIFF image based on specified bounding boxes.
- **Save Cropped Images**: Saves each cropped portion of the GeoTIFF as a separate file.

## Dependencies
- geopandas
- rasterio
- shapely
- numpy
- os

## Installation
Ensure you have the required dependencies installed. You can install them using pip:
```bash
pip install geopandas rasterio shapely numpy
```

## Usage
1. **Set File Paths**: Update `shapefile_path`, `geotiff_path`, and `output_folder` with the appropriate file locations.

2. **Run Script**: Execute the script to crop the GeoTIFF based on points in the shapefile and save the cropped images.

```python
points_gdf = load_shapefile(shapefile_path)
bounding_boxes = get_bounding_boxes(points_gdf)
cropped_images = crop_geotiff(geotiff_path, bounding_boxes)
save_cropped_images(cropped_images, output_folder, geotiff_path)
```

## Functions
### `load_shapefile(file_path)`
Loads a shapefile into a GeoDataFrame.

### `get_bounding_boxes(gdf, buffer=1)`
Creates bounding boxes around each point in the GeoDataFrame.

### `crop_geotiff(geotiff_path, bounding_boxes)`
Crops the GeoTIFF based on the bounding boxes.

### `save_cropped_images(cropped_images, output_folder, geotiff_path, prefix="cropped")`
Saves the cropped images to a specified folder.

## Notes
- Ensure the coordinate reference system (CRS) of the shapefile and the GeoTIFF are compatible.
- The script assumes a buffer of 1 meter around each point for creating bounding boxes, which can be adjusted.