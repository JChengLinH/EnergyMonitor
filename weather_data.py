from azure.storage.blob import BlobServiceClient
from datetime import date
from dotenv import load_dotenv
import os, json

class GetWeatherData():


    def __init__(self) -> None:
        load_dotenv("creds.env")
        self.storage_url = os.getenv("SAS_URL")
        self.storage_token = os.getenv("SAS_TOKEN")
        
        
    def get_data(self, city):
        city_name = city
        container_name = "weather-data"
        filename = f"weather_{city_name}_{date.today().strftime('%Y-%m-%d')}.json"
        blob_service_client = BlobServiceClient(account_url=self.storage_url, credential=self.storage_token)
        blob = blob_service_client.get_blob_client(container_name, filename)

        weather_data = dict(json.loads(blob.download_blob().readall()))
        last_key = list(weather_data)[-1]
        return weather_data[last_key]
