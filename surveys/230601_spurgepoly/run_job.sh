#! bin/bash

url=https://raw.githubusercontent.com/samsoe/mpg_aerial_survey/main/surveys/230601_spurgepoly/config_file.json

for idx in for idx in {0..9};
do
    gcloud compute instances add-metadata odm-array-$idx --zone us-central1-a --metadata array_idx=$idx,config_url=$url
    gcloud compute instances start odm-array-$idx
done