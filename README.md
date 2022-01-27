# EnergyMonitor
The EnergyMonitor a data pipeline which collects the current energy production data as well as electricity spot price in Sweden and Finland.

## What Energy Monitor Does
The EnergyMonitor allows users to check the current electricity production composition, total electricity production, total electricity consumption and the electricity spot price of Sweden and Finland of the current day. In addition, weather condition of selected cities in the previously mentioned countries are displayed.

![EnergyMonitor1](/assets/images/EnergyMonitor_SWE.PNG)
![EnergyMonitor2](/assets/images/EnergyMonitor_FI.PNG)

## How Does It Work
The pipeline consists of an ingestion layer, storage layer, processing (data transformation) layer and front-end as shown in the diagram below:
![PipelineIMG](/assets/images/pipeline_structure.PNG)

### Data Ingestion
The data is pulled from various sources. For Finnish electricity data there is a great API developed by Fingrid which provides data with a real time (3 min) update frequency. Same goes for the weather data, the OpenWeather API provides real time weather data. Therefore, the Finnish electricity data and weather data was pulled from these APIs by using Python's requests library.

On the other hand, the real time Swedish data and electricity spot price data were harder to get since there isn't any energy data API that provides these kind of data, at least not that I know of. Therefore, the automation tool Selenium was used to scrape the Swedish electricity production data and electricity spot price data as a last resort.

The Python scripts which are used to pull weather data and Finnish electricity data from APIs can be run continuously by using the serverless function on Microsoft Azure, Function App, with an interval of 12 minutes. On the other hand, the webscraping scripts which are utilizing Selenium can not be set up in Function App without upgrading the service plan and pack the scripts and dependencies into a docker image, since Selenium is not an supported Python package in Azure Function App. The solution for this is pack these into docker images and let these images run as Container Instances on Azure instead. The Container Instances are run and stopped by a time-based trigger created in Azure Logic Apps with an interval of 60 minutes. The reason why the interval is not shorter is to lessen the loads on the websites. 

### Data Storage
The obtained data are then stored as json files on Azure blob storage and is considered as the source of truth.

### Data Transformation
Transformation is done with Python, mainly using pandas. Transformation was needed in order to facilitate visualization in plotly. All data was already partially pre-processed and restructured at the ingestion layer.

### Front-End
The website dashboard is run on a flask server with charts created with Python plotly and styling done with Bootstrap 5.

## Data Sources
#### [Fingrid API](https://data.fingrid.fi/en/pages/apis)
#### [OpenWeather API](https://openweathermap.org/api)
#### [Vattenfall SWE](https://www.vattenfall.se/elavtal/elpriser/timpris-pa-elborsen/)
#### [Vattenfall FI](https://www.vattenfall.fi/sahkosopimukset/porssisahko/tuntispot-hinnat-sahkoporssissa/)
#### [Svenska Kraftnät](https://www.svk.se/om-kraftsystemet/kontrollrummet/)
