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


def get_bounding_boxes(gdf, side_len_m=1):
    """
    Creates bounding boxes around each point in the GeoDataFrame. Each bounding box is a square with sides of length `side_len_meters` in meters.

    Parameters:
    gdf (GeoDataFrame): A GeoDataFrame with geometry in a coordinate reference system (CRS) that uses meters as units.
    side_len_m (float): The length of each side of the bounding box in meters.
    """

    half_side = side_len_m / 2  # Calculate half the side length
    bounding_boxes = []
    for point in gdf.geometry:
        bbox = box(
            point.x - half_side,
            point.y - half_side,
            point.x + half_side,
            point.y + half_side,
        )
        bounding_boxes.append(bbox)
    return gpd.GeoDataFrame(geometry=bounding_boxes, crs=gdf.crs)


def crop_and_save_geotiff(
    geotiff_path,
    bounding_boxes,
    output_folder,
    write_images=True,
    prefix="cropped",
    compression_level=6,
):
    """
    Crops the GeoTIFF based on the bounding boxes and saves each cropped image immediately.
    Applies DEFLATE compression with a specified compression level.
    """
    if write_images and not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with rasterio.open(geotiff_path) as src:
        meta = src.meta.copy()

        for i, bbox in enumerate(bounding_boxes.geometry):
            bbox_gdf = gpd.GeoDataFrame(geometry=[bbox], crs=bounding_boxes.crs)
            bbox_transformed = bbox_gdf.to_crs(src.crs)

            out_image, out_transform = mask(
                src, [bbox_transformed.geometry.iloc[0]], crop=True
            )
            meta.update(
                {
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                    "compress": "DEFLATE",
                    "zlevel": compression_level,
                }
            )

            if write_images:
                output_path = os.path.join(output_folder, f"{prefix}_{i}.tif")
                with rasterio.open(output_path, "w", **meta) as dest:
                    dest.write(out_image)


shapefile_path = "./points.shp"
geotiff_path = "./orthomosaic.tif"
output_folder = "./folder/"

points_gdf = load_shapefile(shapefile_path)
bounding_boxes = get_bounding_boxes(points_gdf)
crop_and_save_geotiff(geotiff_path, bounding_boxes, output_folder)
