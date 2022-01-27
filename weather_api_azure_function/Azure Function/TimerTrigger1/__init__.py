import requests
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import os
import json
from datetime import datetime, date, timedelta


def main(mytimer: func.TimerRequest) -> None:
    API_KEY = os.getenv("WEATHER_API_KEY")
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    city_names = ["lulea", "sundsvall", "stockholm", "malmo", "helsinki"]

    for city_name in city_names:
        if city_name == "helsinki":
            time_shift = 2 #EET
        
        else:
            time_shift = 1 #UTC+1

        params = {
            "q": city_name,
            "appid": API_KEY,
            }

        storage_url = os.getenv("SAS_URL")
        storage_token = os.getenv("SAS_TOKEN")
        response = requests.get(url=weather_url, params=params)
        response.raise_for_status()
        data = response.json()

        temp = float(data["main"]["temp"]) - 273.15
        wind = float(data["wind"]["speed"])
        weather_data = {
            "temp": temp,
            "wind_speed": wind,
        }

        timestamp = (datetime.utcnow() + timedelta(hours=time_shift)).strftime("%Y-%m-%d %H:%M:%S")

        data = {
            timestamp: weather_data
        }

        
        container_name = "weather-data"
        filename = f"weather_{params['q']}_{date.today().strftime('%Y-%m-%d')}.json"
        blob_service_client = BlobServiceClient(account_url=storage_url, credential=storage_token)
        blob = blob_service_client.get_blob_client(container_name, filename)

        try:
            output_data = json.dumps(data, indent=4)
            blob.upload_blob(output_data, blob_type="BlockBlob")

        except:
            blob_data = dict(json.loads(blob.download_blob().readall()))
            blob_data.update(data)
            output_data = json.dumps(blob_data, indent=4)
            blob.upload_blob(output_data, blob_type="BlockBlob", overwrite=True)
