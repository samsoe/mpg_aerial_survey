#! bin/bash

# Transfer hello_world.txt to cloud storage
gsutil cp /usr/local/bin/datasets/hello_world.txt gs://mpg-aerial-survey/automation/output_ortho/ > /tmp/gsutil.log 2>&1

# Print dialogue for debugging
if [ $? -ne 0 ]; then
    echo "gsutil command failed. Check /tmp/gsutil.log for details."
fi