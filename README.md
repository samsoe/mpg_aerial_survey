# mpg_aerial_survey
## Planning
### Polygon
- Create a polygon for aerial survey area
- Save Polygon in KML file format in accessible cloud location
- Transfer KML to microSD

### Flight Plan
- Insert microSD with polygon KML into DJI RC Pro Controller
- Access polygon on microSD with DJI Pilot

### Ground Control Points (GCP) 
- Utilize gcp_optimizer script for GCP placement within polygon
- Choose gcp_num variable >= 5 for project 
- Output CSV from gcp_optimizer
- Upload CSV to Emlid Flow project


## Mobilization
### Equipment Checks
#### DJI RC Pro Controller (RC_Pro)
- Confirm MicroSD card is in RC_Pro
- Ensure Polygon KML is accessible in DJI Pilot
- Check battery charge level
- Place Controller in M3M case

#### DJI Mavic 3 Multispectral (M3M)
- Confirm MicroSD card is in aircraft
- Check available memory on M3M (DJI Mavic 3 Multispectrum)
- Check charge levels on batteries required for survey missions
- Confirm Propellers are in case
- Load M3M case with M3M, RC_Pro controller, propellers and batteries


#### Mobile Device (iPad / Phone)
- Ensure planned GCP project is accessible in Emlid Flow
- Check battery charge level
- Place mobile devices iPad / Phone in backpack

#### Emlid Reach RS2 (RS2)
- Check battery charge level on Base unit
- Check battery charge level on Rover unit
- Confirm stable operation of quadpod and tripod for Base and Rover units

### Vehicle Loadout
- Load quadpod and tripod into vehicle
- Load both RS2 units into vehicle
- Load backpack into vehicle
- Load M3M case into vehicle

## Field Operations
### GCP Placement
#### Setup RS2 Base
- Turn on Base
- Connect to Wifi/Hotspot
- Activate Logging
- Activate incoming corrections and connect to CORS station
- Average base Fix for 5 minutes
- Deactivate incoming corrections

### Aerial Survey
- Assess obstacles in flight environment

## Post-flight Data Management
- Download to images from microSD on M3M to local machine
- rsync images and RTK files to cloud storage

## Data Processing
- Follow steps in ['odm_workflow' Notebook](odm_workflow.ipynb)
- GCP Editor Pro