library(tidyverse)
library(leaflet.opacity)

view_path <- 'https://raw.githubusercontent.com/samsoe/mpg_aerial_survey/main/view_survey.R'
source(view_path)
poly_path <- '~/mpg_aerial_survey/surveys/230612_spurgepoly/flightplan.kml'
# tags <- st_read('~/Downloads/spurge_ground_truth_2023.shp/point.shp') %>% 
#   as.data.frame() %>% 
#   select(Longitude,Latitude)

# preds <- rast('~/2023_provision_spurge_classifier/data/raster/predictions/output_stacked.vrt') %>% 
#   project('EPSG:3857', method = 'near') %>% 
#   raster::raster()

view_survey('230612_spurgepoly', poly_path)#  %>% 
  #addMarkers(lng=as.numeric(tags$Longitude), lat=as.numeric(tags$Latitude)) %>% 
#  addRasterImage(preds, colors=c('transparent', 'red'), opacity=0.8, layerId = 'ras', project = FALSE) %>% 
#  addOpacitySlider(layerId = 'ras')


library(leaflet)
library(leaflet.extras2)

view_survey_swipe <- function(survey_1, survey_2, labels=NULL, roi=NULL) {
  if(!is.null(roi)){
    poly <- st_read(roi)
    centriod <- get_centroid(poly)
  }
  
  url <- 'https://storage.googleapis.com/mpg-aerial-survey/surveys/SURVEYNAME/post_process/webmap_tiles/{z}/{x}/{y}.png'
  url_1 <- url %>% str_replace('SURVEYNAME', survey_1)
  url_2 <- url %>% str_replace('SURVEYNAME', survey_2)
  base_2022 <- 'https://storage.googleapis.com/spurge_vision/2022_fixed_wing_rgb_tiles/{z}/{x}/{y}.png'
  
  tms = TRUE
  
  label_1 <- survey_1
  label_2 <- survey_2
  
  if(!is.null(labels)){
    label_1 <- labels[1]
    label_2 <- labels[2]
  }
  
  m <- leaflet(options = leafletOptions(attributionControl=FALSE)) %>%
    addMapPane("bottom", zIndex = 0) %>%
    addMapPane("left", zIndex = 1) %>%
    addMapPane("right", zIndex = 1) %>%
    setView(lng = centriod[1],
            lat = centriod[2],
            zoom = 15) %>%
    leaflet::addProviderTiles(provider = providers$Esri.WorldImagery,
                              options = pathOptions(pane='bottom')) %>% 
    leaflet::addTiles(urlTemplate = base_2022, 
                      options = c(tileOptions(maxZoom = 22, tms = tms), pathOptions(pane='bottom')))%>% 
    leaflet::addTiles(urlTemplate = url_1, layerId = 'survey_1',
                      options = c(tileOptions(maxZoom = 22, tms = tms), pathOptions(pane='left'))) %>% 
    leaflet::addTiles(urlTemplate = url_2, layerId = 'survey_2',
                      options = c(tileOptions(maxZoom = 22, tms = tms), pathOptions(pane='right'))) %>% 
    leaflet::addControl(html = paste0(label_1), position = 'bottomleft') %>% 
    leaflet::addControl(html = paste0(label_2), position = 'bottomright') %>% 
    addSidebyside(layerId = "sidecontrols",
                  leftId = "survey_1",
                  rightId = "survey_2")
  
  if(!is.null(roi)){
    m %>% addPolygons(data=poly, fill=FALSE, weight=2.5,color='cyan', opacity = 1)
  }
  
}

d <- read.csv('~/Downloads/spurge_ground_truth_2023.csv')

labs <- c('June 1, 2023', 'June 12, 2023')

library(raster)
library(terra)
msk <- rast('/Volumes/mpgcloud/Shared/Workspace/Teams/herbicide_vision/data/clustered_pred_summaries.tif')[[1]] > 0
msk <- subst(msk, 0, NA)

patch <- rast('/Volumes/mpgcloud/Shared/Workspace/Teams/herbicide_vision/data/clustered_pred_summaries.tif')[[2]] 
patch <-mask(patch, msk)

area <- rast('/Volumes/mpgcloud/Shared/Workspace/Teams/herbicide_vision/data/clustered_pred_summaries.tif')[[1]] 
area <-mask(area, msk)

plot_mod <- \(mod, title){
  pal <- colorNumeric(palette = viridis::viridis(100), domain = values(mod), na.color = 'transparent')
  
  view_survey('230612_spurgepoly', poly_path)%>% 
    addRasterImage(mod %>% raster(),
                   colors=pal,
                   layerId = title, opacity=0.8) %>% 
    #addOpacitySlider(layerId = title) %>% 
    addLegend(pal = pal, values = values(mod), title = title)
}

area_map <- plot_mod(area, 'Spurge area (m)')
patch_map <- plot_mod(patch, 'Mean patch size (m)')

library(leafsync)

sync(area_map, patch_map,  view_survey('230612_spurgepoly', poly_path), ncol=1)

