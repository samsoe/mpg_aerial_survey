import subprocess

packages = ['geopandas', 'pandas', 'numpy', 'shapely', 'pyproj', 'fiona', 'json']

for p in packages:
  subprocess.check_call(['pip', 'install', p])

#pip install -Uqq geopandas pandas numpy shapely pyproj fiona

import os
import shutil
import tempfile
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, box, mapping
from pyproj import CRS
import fiona
import requests
import json

fiona.drvsupport.supported_drivers['KML'] = 'rw'

def download_file(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved as '{save_path}'.")
    else:
        print(f"Error occurred while downloading file from '{url}'.")

def gridify(gdf, side_length: float) -> list:
    # Check if the CRS matches the projected CRS
    if gdf.crs != 'epsg:26911':
        print(f"Warning: CRS does not match 'epsg:26911', it is: {gdf.crs}")
        
    # This assumes that the DataFrame has only one Polygon, else it takes the first one
    poly = gdf.geometry[0]

    minx, miny, maxx, maxy = poly.bounds
    grid_cells = []

    for x in np.arange(minx, maxx, side_length):
        for y in np.arange(miny, maxy, side_length):
            cell_poly = box(x, y, x+side_length, y+side_length)
            if cell_poly.intersects(poly):
                grid_cells.append(cell_poly)
    
    return grid_cells

def expand_to_gcps(focal_poly, gcps, gcp_cutoff=5, step_sz=30, base_buffer=50):
    focal_poly = focal_poly.buffer(base_buffer)
    count = sum(gcps.within(focal_poly.geometry.iloc[0]))
    
    if count < gcp_cutoff:
        while count < gcp_cutoff:
            focal_poly = focal_poly.buffer(step_sz)
            count = sum(gcps.within(focal_poly.geometry.iloc[0]))
    
    return focal_poly

def load_kml(path):
  df = gpd.GeoDataFrame()

  # iterate over layers
  for layer in fiona.listlayers(path):
      s = gpd.read_file(path, driver='KML', layer=layer)
      df = pd.concat([df, s], ignore_index=True)
  return df

def copy_to_gcs(local_file_path, bucket_name):
    command = ['gsutil', 'cp', local_file_path, 'gs://{}/'.format(bucket_name)]
    try:
        subprocess.run(command, check=True)
        print('File copied to Google Cloud Storage successfully.')
    except subprocess.CalledProcessError as e:
        print('Error occurred while copying the file to Google Cloud Storage:')
        print(e)

def filter_manifest(manifest, focal_poly, address_type='url'):
  focal_poly_ll = focal_poly.to_crs(epsg=4326)
  keepers = []
  for index, row in manifest.iterrows():
    point = Point(row['longitude'], row['latitude'])
    if point.within(focal_poly_ll.geometry.iloc[0]):  # only keep points within the polygon
            keepers.append(row[address_type])
  return keepers

def process_images(batch, output_bucket, ortho_res, suffix):
   # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create an 'images' subdirectory
    images_dir = os.path.join(temp_dir, 'images')
    os.mkdir(images_dir)

    for url in batch:
        try:
            subprocess.run(['wget', '-P', images_dir, url], check=True)
            print(f"File downloaded successfully from {url}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while downloading file from {url}:")
            print(e)

    # Execute OpenDroneMap Docker command
    docker_command = [
        "docker", "run", "--rm",
        "-v", "{}:/datasets/code".format(temp_dir),
        "opendronemap/odm", "--project-path", "/datasets",
        "--orthophoto-resolution", f"{ortho_res}",
        "--fast-orthophoto",
        "--force-gps"
    ]

    process = subprocess.run(docker_command, check=True)
    
    ortho = os.path.join(temp_dir,'odm_orthophoto/odm_orthophoto.tif')
    report = os.path.join(temp_dir,'odm_report/report.pdf')
    ortho_new = ortho.replace('.tif',f'_{suffix}.tif')
    report_new = report.replace('.pdf',f'_{suffix}.pdf')
    os.rename(ortho, ortho_new)
    os.rename(report, report_new)

    focal_files = [ortho_new, report_new]
    
    for f in focal_files:
        copy_to_gcs(f, output_bucket)
    
    # Cleanup: Remove temporary directory
    shutil.rmtree(temp_dir)

drainage_buffer_url = 'https://storage.googleapis.com/mpg-aerial-survey/supporting_data/drainage_buffer.kml'


#later these will be updated to gcloud metadata queries:
array_idx = 2
config_url = 'https://raw.githubusercontent.com/samsoe/mpg_aerial_survey/main/config_files/init_testing_config_file.json'
config_file = os.path.basename(config_url)

with open(config_file, 'r') as json_file:
    # Load the JSON data into a Python object
    config = json.load(json_file)

survey_res = config['survey_res']
compute_array_sz = config['compute_array_sz']
flight_plan_url = config['flight_plan_url']
photo_manifest_url = config['photo_manifest_url']
output_bucket =  config['output_bucket']
gcp_editor_url = config['gcp_editor_url']

drainage_buffer = os.path.basename(drainage_buffer_url)
flight_plan = os.path.basename(flight_plan_url)
photo_manifest = os.path.basename(photo_manifest_url)

download_file(drainage_buffer_url, drainage_buffer)
download_file(flight_plan_url, flight_plan)
download_file(photo_manifest_url, photo_manifest)

flight_roi = load_kml(flight_plan)
drainage_poly = load_kml(drainage_buffer)

gcp_areas = flight_roi.difference(drainage_poly)

crs_source = CRS.from_epsg(4326)
crs_target = CRS.from_epsg(26911)

# Set the source CRS of the GeoDataFrame
flight_roi.crs = crs_source
gcp_areas.crs = crs_source

# Reproject the GeoDataFrame to the target CRS
flight_projected_src = flight_roi.to_crs(crs_target)
gcp_areas_projected_src = gcp_areas.to_crs(crs_target)

minx, miny, maxx, maxy = gcp_areas_projected_src.geometry.iloc[0].bounds

# Then, let's create the points
# We are using np.arange that gives us evenly spaced values within a given interval
x_coords = np.arange(minx, maxx, 200)
y_coords = np.arange(miny, maxy, 200)

# Next, we'll create a grid of points within this bounding box
points = []
for x in x_coords:
    for y in y_coords:
        point = Point(x, y)
        if point.within(gcp_areas_projected_src.geometry.iloc[0]):  # only keep points within the polygon
            points.append(point)

gcp_gdf_utm = gpd.GeoDataFrame(geometry=points, crs='EPSG:26911')
gcp_gdf_latlon = gcp_gdf_utm.to_crs(crs_source)

grid_side = 10
grid_cells = [1]*int(1e9)

while len(grid_cells) > compute_array_sz:
  grid_cells = gridify(flight_projected_src, grid_side)
  grid_side += 10

grid_gdf = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs='EPSG:26911')
focal_poly = grid_gdf.to_crs(epsg=26911).loc[[array_idx]]
out_poly = expand_to_gcps(focal_poly, gcp_gdf_utm, step_sz=30)

manifest_df = pd.read_csv('manifest.csv')

target_photos = filter_manifest(manifest_df, focal_poly)

process_images(batch=target_photos, output_bucket=output_bucket, ortho_res=survey_res, suffix=array_idx)
