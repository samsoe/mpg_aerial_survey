#!/usr/bin/python
import os

def get_metadata(attribute):
  curl_command = ["curl", "-H", "Metadata-Flavor: Google", f"http://metadata/computeMetadata/v1/instance/{attribute}"]
  result = subprocess.run(curl_command, capture_output=True, text=True)
  return result.stdout.strip()

def copy_to_gcs(local_file_path, bucket_name):
    command = ['gsutil', 'cp', local_file_path, 'gs://{}/'.format(bucket_name)]
    try:
        subprocess.run(command, check=True)
        print('File copied to Google Cloud Storage successfully.')
    except subprocess.CalledProcessError as e:
        print('Error occurred while copying the file to Google Cloud Storage:')
        print(e)

targ_bucket = "mpg-aerial-survey/supporting_data/testing"

idx = int(get_metadata('array_idx'))
fname = 'hellow_world_{}.txt'.format(str(idx))
dst = os.path.join("/usr/local/bin/datasets/", fname)

# Open the file in write mode
file = open(dst, "w")

# Write the text into the file
file.write(f"Node {idx} says hi!")

# Close the file
file.close()

copy_to_gcs(dst, targ_bucket)
