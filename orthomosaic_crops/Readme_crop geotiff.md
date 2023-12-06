# GeoTIFF Cropping Tool

This tool provides a Python-based solution for cropping GeoTIFF files based on a set of points loaded from a shapefile. It uses libraries like `geopandas`, `rasterio`, and `shapely` to handle geographical data and raster operations.

## Features

- **Load Shapefile**: Converts a shapefile into a GeoDataFrame.
- **Create Bounding Boxes**: Generates bounding boxes around each point in the GeoDataFrame.
- **Crop and Save GeoTIFF**: Crops the GeoTIFF based on these bounding boxes and saves each cropped image with DEFLATE compression.

## Requirements

- `geopandas`
- `rasterio`
- `shapely`
- `numpy`
- `os`

## Usage

1. **Load Shapefile**: Provide the path to your shapefile.
   ```python
   shapefile_path = "./points.shp"
   points_gdf = load_shapefile(shapefile_path)
   ```

2. **Create Bounding Boxes**: Specify the side length for the bounding boxes around each point.
   ```python
   bounding_boxes = get_bounding_boxes(points_gdf)
   ```

3. **Crop and Save GeoTIFF**: Specify the path to your GeoTIFF, output folder, and other optional parameters.
   ```python
   geotiff_path = "./orthomosaic.tif"
   output_folder = "./output/"
   crop_and_save_geotiff(geotiff_path, bounding_boxes, output_folder)
   ```

## Functions

### `load_shapefile(file_path)`
Loads a shapefile into a GeoDataFrame.

### `get_bounding_boxes(gdf, side_len=1)`
Creates bounding boxes around each point in the GeoDataFrame.

### `crop_and_save_geotiff(geotiff_path, bounding_boxes, output_folder, write_images=True, prefix="cropped", compression_level=6)`
Crops the GeoTIFF based on the bounding boxes and saves each cropped image. It applies DEFLATE compression with the specified level.

## Example

```python
shapefile_path = "./points.shp"
geotiff_path = "./orthomosaic.tif"
output_folder = "./output/"

points_gdf = load_shapefile(shapefile_path)
bounding_boxes = get_bounding_boxes(points_gdf)
crop_and_save_geotiff(geotiff_path, bounding_boxes, output_folder)
```

This script will load points from `points.shp`, create bounding boxes around each point, and then crop `orthomosaic.tif` based on these bounding boxes, saving the results in the `./output/` directory.

