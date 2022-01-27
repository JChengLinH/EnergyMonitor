from selenium import webdriver
from azure.storage.blob import BlobServiceClient
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import date
import json, os
from dotenv import load_dotenv

class ElPriceFetcher():


    def __init__(self):

        self.SELENIUM_PATH = Service("/usr/local/bin/chromedriver")
        self.SWE_PRICE_URL = "https://www.vattenfall.se/elavtal/elpriser/timpris-pa-elborsen/"
        self.FI_PRICE_URL = "https://www.vattenfall.fi/sahkosopimukset/porssisahko/tuntispot-hinnat-sahkoporssissa/"
        self.options = Options()
        #The following options are required in order for it to work in Docker.
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.headless = True
    

    def fetch_price_swe(self):
        driver = webdriver.Chrome(service=self.SELENIUM_PATH, options=self.options)
        driver.get(self.SWE_PRICE_URL)
        rows = driver.find_elements_by_class_name("ui-grid-row")
        date_today = date.today().strftime("%Y-%m-%d")

        swe_price_data = {}
        for row in rows:
            row_content = row.text.replace(",", ".").split("\n")
            time = row_content[0]
            price = row_content[1]
            time_stamp = f"{time}:00"
            swe_price_data[time_stamp] = float(price)
            structured_data = {
                date_today: swe_price_data
                }

        self.save_to_blob(structured_data, self.fetch_price_swe.__name__)
        # try:
        #     with open(f"price_data/swe_price_data_{date_today}.json", "r") as price_file:
        #         data = json.load(price_file)
        #         data.update(structured_data)

        # except FileNotFoundError:
        #     with open(f"price_data/swe_price_data_{date_today}.json", "w") as price_file:
        #         json.dump(structured_data, price_file, indent=4)
        
        # else:
        #     with open(f"price_data/swe_price_data_{date_today}.json", "w") as price_file:
        #         json.dump(structured_data, price_file, indent=4)


    def fetch_price_fi(self):
        driver = webdriver.Chrome(service=self.SELENIUM_PATH, options=self.options)
        driver.get(self.FI_PRICE_URL)

        #Click on the table button to show table.
        table_button_element = driver.find_element(By.XPATH, "/html/body/main/section/main/div/div[1]/div/price-spot-fi/div[1]/div/div/div[3]/div/div/button[1]")
        driver.execute_script("arguments[0].click();", table_button_element)

        rows = driver.find_elements(By.CSS_SELECTOR, ".table-simple tbody tr")
        date_today = date.today().strftime("%Y-%m-%d")
        fi_price_data = {}
        for row in rows:
            row_content = row.text.replace(",", ".").split(" ")
            time = row_content[0]
            price = row_content[1]
            time_stamp = f"{time}:00"
            fi_price_data[time_stamp] = float(price)
            structured_data = {
                date_today: fi_price_data
                }
        
        self.save_to_blob(structured_data, self.fetch_price_fi.__name__)

        # try:
        #     with open(f"price_data/fi_price_data_{date_today}.json", "r") as price_file:
        #         data = json.load(price_file)
        #         data.update(structured_data)

        # except FileNotFoundError:
        #     with open(f"price_data/fi_price_data_{date_today}.json", "w") as price_file:
        #         json.dump(structured_data, price_file, indent=4)

        # else:
        #     with open(f"price_data/fi_price_data_{date_today}.json", "w") as price_file:
        #         json.dump(structured_data, price_file, indent=4)


    def save_to_blob(self, data: dict, function_name):
        load_dotenv("creds.env")
        storage_token = os.getenv("SAS_TOKEN")
        storage_url = os.getenv("SAS_URL")
        container_name = "el-price"

        if function_name == "fetch_price_fi":
            country_code = "fi"
        else:
            country_code = "swe"

        filename = f"{country_code}_elprice_{date.today().strftime('%Y-%m-%d')}.json"
        blob_service_client = BlobServiceClient(account_url=storage_url, credential=storage_token)
        blob = blob_service_client.get_blob_client(container_name, filename)
        output_data = json.dumps(data, indent=4)
        blob.upload_blob(output_data, blob_type="BlockBlob")