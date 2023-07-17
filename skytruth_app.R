library(shiny)
library(leaflet)
library(sf)

skytruth_survey <- function(survey){
  
  flight_file = tempfile(fileext = '.kml')
  flight_url = 'https://raw.githubusercontent.com/samsoe/mpg_aerial_survey/main/surveys/SURVEYNAME/flightplan.kml' %>% 
    str_replace('SURVEYNAME', survey)
  download.file(flight_url, flight_file)
  
  poly <- st_read(flight_file)
  centriod <- get_centroid(poly)
  
  url <- 'https://storage.googleapis.com/mpg-aerial-survey/surveys/SURVEYNAME/post_process/webmap_tiles/{z}/{x}/{y}.png' %>% 
    str_replace('SURVEYNAME', survey)
  
  ui <- 
    fillPage(
      leafletOutput("map", height = "100%"),
      absolutePanel(
        downloadButton("downloadData", "Download"),
        textOutput("countDisplay"),
        top = 10,
        right = 10
        )
      
    )
  
  server <- function(input, output, session) {
    # Initialize data frame to store clicks
    clicks <- reactiveVal(data.frame(id = integer(), x = numeric(), y = numeric(), lat = numeric(), lng = numeric()))
    
    # Render the leaflet map
    output$map <- renderLeaflet({
      leaflet() %>%
        leaflet::addTiles(urlTemplate = url,
                          options = c(tileOptions(maxZoom = 22, tms = TRUE))) %>% 
        setView(lng = centriod[1],
                lat = centriod[2],
                zoom = 15) %>% 
        addPolygons(data=poly, fill=FALSE, weight=2.5,color='cyan', opacity = 1)
        
    })
    
    rowCount <- reactive({
      nrow(clicks())
    })
    
    # Display the count of rows
    output$countDisplay <- renderText({
      paste("Count of Markers:", rowCount())
    })
    
    
    # Observe map clicks and add markers
    observeEvent(input$map_click, {
      # Do nothing if there was a marker click recently
      if (!is.null(input$map_marker_click) && input$map_marker_click$time > input$map_click$time)
        return()
      
      click <- input$map_click
      # Transform coordinates to EPSG:32611
      coordinates <- st_transform(st_sfc(st_point(c(click$lng, click$lat)), crs = 4326), 32611)
      coord_array <- st_coordinates(coordinates)
      
      # Add marker
      new_click <- data.frame(id = nrow(clicks()) + 1, x = coord_array[1], y = coord_array[2], lat = click$lat, lng = click$lng)
      clicks(rbind(clicks(), new_click))
      
      # Update markers on the map
      leafletProxy("map") %>%
        clearMarkers() %>%
        addMarkers(data = clicks(), lng = ~lng, lat = ~lat, layerId = ~id)
    })
    
    # Observe marker clicks to delete markers
    observeEvent(input$map_marker_click, {
      clickId <- input$map_marker_click
      
      # Remove marker and data
      clicks(clicks()[clicks()$id != clickId$id, ])
      
      # Update markers on the map
      leafletProxy("map") %>%
        clearMarkers() %>%
        addMarkers(data = clicks(), lng = ~lng, lat = ~lat, layerId = ~id)
    })
    
    # Allow user to download data as a CSV (only x and y columns in EPSG:32611)
    output$downloadData <- downloadHandler(
      filename = function() {
        paste("click-coordinates-", Sys.Date(), ".csv", sep = "")
      },
      content = function(file) {
        write.csv(clicks()[, c("id", "x", "y")], file, row.names = FALSE)
      }
    )
  }
  
  # Run the application
  shinyApp(ui = ui, server = server)
}

skytruth_survey('230612_spurgepoly')