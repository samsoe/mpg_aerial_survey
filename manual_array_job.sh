url=https://raw.githubusercontent.com/samsoe/mpg_aerial_survey/main/surveys/230601_spurgepoly/config_file.json
idx=0

gcloud compute instances add-metadata odm-array-$idx --zone us-central1-a --metadata array_idx=$idx,config_url=$url
gcloud compute instances start odm-array-$idx
