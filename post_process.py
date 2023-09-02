import subprocess

subprocess.run(['pip3', 'install', '--upgrade', 'pip'], check=True)
subprocess.run(['sudo', 'apt-get', 'install', 'gdal-bin', 'libgdal-dev', 'libspatialindex-dev'], check=True, input=b'y\n')

packages = ['cython','pyproj','geopandas','pandas','numpy','shapely','fiona','rasterio','scipy', 'rtree','pygeos']

for p in packages:
  subprocess.check_call(['pip3', 'install', p])

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
import rasterio
from rasterio.mask import mask
from rasterio.enums import Resampling
from scipy.spatial import Voronoi

fiona.drvsupport.supported_drivers['KML'] = 'rw'

def download_file(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved as '{save_path}'.")
    else:
        print(f"Error occurred while downloading file from '{url}'.")
        
def get_metadata(attribute):
    curl_command = [
        "curl",
        "-H",
        "Metadata-Flavor: Google",
        f"http://metadata/computeMetadata/v1/instance/attributes/{attribute}"
    ]
    result = subprocess.run(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output = result.stdout.strip()
    return output

def load_kml(path):
  df = gpd.GeoDataFrame()

  # iterate over layers
  for layer in fiona.listlayers(path):
      s = gpd.read_file(path, driver='KML', layer=layer)
      df = pd.concat([df, s], ignore_index=True)
  return df

def copy_to_gcs(local_file_path, bucket_name):
    command = ['gsutil', 'cp', '-r', local_file_path, 'gs://{}/'.format(bucket_name)]
    try:
        subprocess.run(command, check=True)
        print('File copied to Google Cloud Storage successfully.')
    except subprocess.CalledProcessError as e:
        print('Error occurred while copying the file to Google Cloud Storage:')
        print(e)

def mask_to_gdf(gdf, raster_path, output_path):
    # Read the raster file
    src = rasterio.open(raster_path)

    # Reproject the GeoDataFrame to match the projection of the raster, if needed
    gdf = gdf.to_crs(src.crs)

    # Mask the raster using the GeoDataFrame's geometry
    out_image, out_transform = mask(src, gdf.geometry, crop=True)

    # Update the metadata of the cropped raster
    out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform,
        "dtype": out_image.dtype,
        "compress": src.compression.value if src.compression else "none"
    })

    # Save the cropped raster to a new file
    with rasterio.open(output_path, 'w', **out_meta) as dst:
        # Use the original raster's block size and resampling method for better compression
        dst.write(out_image)

def process_images(batch, output_bucket, ortho_res, cutline, suffix, gcp_list_path):
   # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create an 'images' subdirectory
    images_dir = os.path.join(temp_dir, 'images')
    os.mkdir(images_dir)

    if gcp_list_path is not None:
        shutil.move(gcp_list_path, temp_dir)

    for url in batch:
        try:
            subprocess.run(['wget', '-P', images_dir, url], check=True)
            print(f"File downloaded successfully from {url}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while downloading file from {url}:")
            print(e)

    # Execute OpenDroneMap Docker command
    docker_command = [
        "sudo", "docker", "run", "--rm",
        "-v", "{}:/datasets/code".format(temp_dir),
        "opendronemap/odm", "--project-path", "/datasets",
        "--orthophoto-resolution", f"{ortho_res}",
        "--feature-quality", "ultra",
        "--force-gps"
    ]

    process = subprocess.run(docker_command, check=True)
    
    ortho = os.path.join(temp_dir,'odm_orthophoto/odm_orthophoto.tif')
    report = os.path.join(temp_dir,'odm_report/report.pdf')
    ortho_new = ortho.replace('.tif',f'_{suffix}.tif')
    report_new = report.replace('.pdf',f'_{suffix}.pdf')
    
    #mask_to_gdf(cutline, ortho, ortho_new)
    os.rename(ortho, ortho_new)
    os.rename(report, report_new)

    focal_files = [ortho_new, report_new]
    
    for f in focal_files:
        copy_to_gcs(f, output_bucket)
    
    # Cleanup: Remove temporary directory
    shutil.rmtree(temp_dir)

def log_progress(file, bucket):
    with open(file, 'w') as f:
        f.write('done')
    copy_to_gcs(file, bucket)

temp_work = tempfile.mkdtemp()
os.chdir(temp_work)

branch = 'main'

array_idx = int(get_metadata('array_idx')) #dynamic production version
config_url = get_metadata('config_url')#dynamic production version
instance_name = f'odm-array-{array_idx}' #name of instance inferred from index

config_file = os.path.basename(config_url)
download_file(config_url, config_file)

with open(config_file, 'r') as json_file:
    # Load the JSON data into a Python object
    config = json.load(json_file)

gcp_res = str(config['gcp_res'])
gcp_grid_url = f'https://raw.githubusercontent.com/samsoe/mpg_aerial_survey/{branch}/gcp_kmls/upland_gcps_{gcp_res}m.kml'

survey_res = config['survey_res']
compute_array_sz = config['compute_array_sz']
flight_plan_url = config['flight_plan_url']
photo_manifest_url = config['photo_manifest_url']
output_bucket =  config['output_bucket']
gcp_editor_url = config['gcp_editor_url']
optimization_base_url = config['optimization_base_url']
log_bucket = output_bucket + '/logs'

log_progress(f'loaded_config_{array_idx}.txt', log_bucket)

gcp_grid = os.path.basename(gcp_grid_url)
flight_plan = os.path.basename(flight_plan_url)
photo_manifest = os.path.basename(photo_manifest_url)

download_file(gcp_grid_url, gcp_grid)
download_file(flight_plan_url, flight_plan)
download_file(photo_manifest_url, photo_manifest)

shape_related_filetypes = ['.cpg','.dbf','.shp','.shx']

for f in shape_related_filetypes:
    focal_file_base = f'job_polys{f}'
    focal_url = optimization_base_url + focal_file_base
    download_file(focal_url, focal_file_base)

if gcp_editor_url is not None:
    gcp_list = os.path.basename(gcp_editor_url)
    download_file(gcp_editor_url, gcp_list)
else:
    gcp_list = None

log_progress(f'downloaded_supporting_dat_{array_idx}.txt', log_bucket)

flight_roi = load_kml(flight_plan)
gcps = load_kml(gcp_grid)

crs_source = CRS.from_epsg(4326)
crs_target = CRS.from_epsg(26911)

# Set the source CRS of the GeoDataFrame
flight_roi.crs = crs_source
gcps.crs = crs_source

# Reproject the GeoDataFrame to the target CRS
flight_projected_src = flight_roi.to_crs(crs_target)
gcps_projected_src = gcps.to_crs(crs_target)

gcps_flight = gpd.sjoin(gcps_projected_src, flight_projected_src, how='inner', op='within')

base_poly = gpd.read_file('job_polys.shp').set_crs(32611).to_crs(crs_target).loc[array_idx,'geometry']
buffered_poly = base_poly.buffer(10)
manifest_df = pd.read_csv(photo_manifest)
manifest_df['geometry'] = manifest_df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
manifest_gpd = gpd.GeoDataFrame(manifest_df, geometry='geometry', crs=crs_source).to_crs(crs_target)
target_photos = gpd.sjoin(manifest_gpd, gpd.GeoDataFrame(geometry=[buffered_poly]), op='within')['url']

log_progress(f'started_post_processing_{array_idx}.txt', log_bucket)

process_images(batch=target_photos, output_bucket=output_bucket,
                ortho_res=survey_res, cutline=base_poly ,suffix=array_idx,
                gcp_list_path=gcp_list)

log_progress(f'finished_job_{array_idx}.txt', log_bucket)
shutil.rmtree(temp_work)