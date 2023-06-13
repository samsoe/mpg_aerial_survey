library(leaflet)
library(sf)
library(tidyverse)

select <- dplyr::select

poly_path <- '~/mpg_aerial_survey/surveys/230601_spurgepoly/flightplan.kml'

get_centroid <- function(poly){
  return(st_centroid(poly %>% st_transform(26911)) %>%
    st_transform(4326) %>% 
    st_coordinates())
}

view_survey <- function(survey, roi=NULL) {
  if(!is.null(roi)){
    poly <- st_read(roi)
    centriod <- get_centroid(poly)
  }
  
  url <- 'https://storage.googleapis.com/mpg-aerial-survey/surveys/SURVEYNAME/post_process/webmap_tiles/{z}/{x}/{y}.png'
  url <- url %>% str_replace('SURVEYNAME', survey)
  
  tms = TRUE
  
  m <- leaflet() %>%
    setView(lng = centriod[1],
            lat = centriod[2],
            zoom = 13) %>%
    leaflet::addProviderTiles(provider = providers$Esri.WorldImagery) %>% 
    leaflet::addTiles(urlTemplate = url, options = tileOptions(maxZoom = 22, tms = tms)) %>% 
    leaflet::addControl(html = paste(survey), position = 'topright')
  
  if(!is.null(roi)){
    m %>% addPolygons(data=poly, fill=FALSE, weight=2.5,color='cyan')
  }
  
}
