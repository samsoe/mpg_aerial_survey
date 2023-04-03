# mpg_aerial_survey
## Planning
### Polygon
- Create a polygon for aerial survey area
- Save Polygon in KML file format in accessible cloud location
- Transfer KML to microSD

### Flight Plan
- Insert microSD with polygon KML into DJI RC Pro Controller
- Access polygon on microSD with DJI Pilot

### Ground Control Points
- Utilize gcp_optimizer script for GCP (Ground Control Points) placement within polygon
- Choose gcp_num variable >= 5 for project 
- Output CSV from gcp_optimizer
- Upload CSV to Emlid Flow project


## Mobilization
### Equipment
#### DJI RC Pro Controller (RC_Pro)
- Ensure Polygon KML is accessible in DJI Pilot
- Check battery charge level

#### DJI Mavic 3 Multispectral (M3M)
- Check available memory on M3M (DJI Mavic 3 Multispectrum)

#### Mobile Device
- Ensure planned GCP project is accessible in Emlid Flow
- Check battery charge level

#### Emlid Reach RS2 (RS2)
- Check battery charge level on Base unit
- Check battery charge level on Rover unit

## GCP Placement
### Setup RS2 Base
- Turn on Base
- Connect to Wifi/Hotspot
- Connect to CORS station

## Flight Operations
- Assess obstacles in flight environment

## Post-flight Data Management
- Download to images from microSD on M3M to local machine
- rsync images and RTK files to cloud storage

## Data Processing
- Follow steps in ['odm_workflow' Notebook](odm_workflow.ipynb)