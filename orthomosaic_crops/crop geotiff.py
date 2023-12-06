import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import box
import numpy as np
import os
from rasterio.transform import from_origin


def load_shapefile(file_path):
    """
    Loads a shapefile into a GeoDataFrame.
    """
    return gpd.read_file(file_path)


def get_bounding_boxes(gdf, side_len=1):
    """
    Creates bounding boxes around each point in the GeoDataFrame.
    """
    bounding_boxes = []
    for point in gdf.geometry:
        bbox = box(
            point.x - side_len,
            point.y - side_len,
            point.x + side_len,
            point.y + side_len,
        )
        bounding_boxes.append(bbox)
    return gpd.GeoDataFrame(geometry=bounding_boxes, crs=gdf.crs)


def crop_geotiff(geotiff_path, bounding_boxes):
    """
    Crops the GeoTIFF based on the bounding boxes and returns the cropped images.
    """
    cropped_images = []
    with rasterio.open(geotiff_path) as src:
        for bbox in bounding_boxes.geometry:
            # Create a GeoDataFrame for the bounding box
            bbox_gdf = gpd.GeoDataFrame(geometry=[bbox], crs=bounding_boxes.crs)

            # Transform the bounding box to the GeoTIFF's coordinate system
            bbox_transformed = bbox_gdf.to_crs(src.crs)

            # Crop the image
            out_image, out_transform = mask(
                src, [bbox_transformed.geometry.iloc[0]], crop=True
            )
            cropped_images.append(out_image)

    return cropped_images


def save_cropped_images(cropped_images, output_folder, geotiff_path, prefix="cropped"):
    """
    Saves the list of cropped images to the specified folder.
    """
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the original GeoTIFF to get its metadata
    with rasterio.open(geotiff_path) as src:
        meta = src.meta.copy()

    # Loop through the cropped images and save each
    for i, image in enumerate(cropped_images):
        # Update the metadata for each image
        meta.update(
            {
                "driver": "GTiff",
                "height": image.shape[1],
                "width": image.shape[2],
                "transform": from_origin(
                    0, 0, 1, 1
                ),  # Update with correct transform if available
            }
        )

        # Define the output path
        output_path = os.path.join(output_folder, f"{prefix}_{i}.tif")

        # Write the cropped image to a file
        with rasterio.open(output_path, "w", **meta) as dest:
            dest.write(image)


shapefile_path = "./points.shp"
geotiff_path = "./orthomosaic.tif"
output_folder = "./folder/"

points_gdf = load_shapefile(shapefile_path)
bounding_boxes = get_bounding_boxes(points_gdf)
cropped_images = crop_geotiff(geotiff_path, bounding_boxes)
save_cropped_images(cropped_images, output_folder, geotiff_path)
