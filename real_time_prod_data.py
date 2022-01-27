import requests, json, os
from datetime import datetime, timedelta, date
from azure.storage.blob import BlobServiceClient

class RealTimeData():


    def __init__(self):
        
        #Variable IDs for real time data
        self.VARIABLE_IDS = {
            #"total_prod": 192,
            "wind_prod": 181,
            "nuclear_prod": 188,
            "hydro_prod": 191,
            "small_scale_prod": 205,
            "CHP_prod": 202,
            "CHP_district_heating": 201,
        }
        self.time_shift_fi = 2
        self.time_zone = f"+0{self.time_shift_fi}00" # UTC+02 Finnish time zone (EET)
        self.start_time = (datetime.utcnow() + timedelta(hours=2)).replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S") + self.time_zone
        self.end_time = (datetime.utcnow() + timedelta(hours=3)).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S") + self.time_zone
        self.fingrid_params = {
            "start_time": self.start_time,
            "end_time": self.end_time,
        }
        

    def fetch_data_fi(self, api_key):

        #OBS: Output returned from the API call is in UTC+00

        fingrid_headers = {"x-api-key": api_key}
        prod_data = {}
        
        for i in self.VARIABLE_IDS:
            fingrid_url = f"https://api.fingrid.fi/v1/variable/{self.VARIABLE_IDS[i]}/events/json"
            fingrid_response = requests.get(url=fingrid_url, headers=fingrid_headers, params=self.fingrid_params)
            fingrid_response.raise_for_status()
            data = fingrid_response.json()

            prod_data[i] = data
        
        data_len = [len(prod_data[i]) for i in prod_data]

        #Check if the data length for each energy production source is the same, if not, call the api once more
        #This is to prevent api call just before its intended update-time, ie. if the call occurs at 17:02:59
        #The first source (wind) is going to have 99 timestamps, the rest is going to have 100 since it updates at 17:03:00 
        if len(set(data_len)) == 1:
            self.save_to_blob(prod_data, self.fetch_data_fi.__name__)

        else:
            self.fetch_data_fi(api_key)
    
    def fetch_data_swe(self):
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        self.SELENIUM_PATH = Service("chromedriver.exe")
        options = Options()
        options.headless = True
        svk_url = "https://www.svk.se/om-kraftsystemet/kontrollrummet/"
        driver = webdriver.Chrome(service=self.SELENIUM_PATH, options=options)
        driver.get(svk_url)
        table_element = driver.find_element_by_class_name("productiontablebutton")

        #Find the "Table" button and click
        driver.execute_script("arguments[0].click();", table_element)
        update_time = driver.find_element(By.XPATH, '//*[@id="production_table"]/div/time').text.replace("idag ", "")
        update_timestamp = f'{date.today().strftime("%Y-%m-%d")} {update_time}:00'

        swe_prod_data = {
            "nuclear_prod": None,
            "thermal_power_prod": None,
            "wind_prod": None,
            "unspecified": None,
            "hydro_prod": None,
        }

        #Getting the cell data by looping over XPATHs
        n = 2
        for i in swe_prod_data:
            prod_data_swe = int(driver.find_element(By.XPATH, f'//*[@id="Produktion"]/tbody/tr[{n}]/td[1]').text.replace(" ", ""))
            swe_prod_data[i] = prod_data_swe
            n += 1
        
        structured_swe_prod_data = {
            update_timestamp: swe_prod_data
        }

        self.save_to_blob(structured_swe_prod_data, self.fetch_data_swe.__name__)
        # try:
        #     with open(f"real_time_data/SWE_real_time_data_{date.today().strftime('%Y-%m-%d')}.json", mode="r") as swe_data_file:
        #         data = json.load(swe_data_file)
        #         data.update(structured_swe_prod_data)
                
        # except FileNotFoundError:
        #     with open(f"real_time_data/SWE_real_time_data_{date.today().strftime('%Y-%m-%d')}.json", mode="w") as swe_data_file:
        #         json.dump(structured_swe_prod_data, swe_data_file, indent=4)  

        # else: 
        #     with open(f"real_time_data/SWE_real_time_data_{date.today().strftime('%Y-%m-%d')}.json", mode="w") as swe_data_file:
        #         json.dump(structured_swe_prod_data, swe_data_file, indent=4) 



    def save_to_blob(self, data: dict, function_name):
        storage_token = os.getenv("SAS_TOKEN")
        storage_url = os.getenv("SAS_URL")
        container_name = "real-time-prod-data"

        if function_name == "fetch_data_fi":
            country_code = "fi"
        else:
            country_code = "swe"

        
        filename = f"{country_code}_real_time_data_{date.today().strftime('%Y-%m-%d')}.json"
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