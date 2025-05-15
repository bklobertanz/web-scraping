import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
import json
import os

# Create downloads directory if it doesn't exist
download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(download_dir, exist_ok=True)

# Setup Firefox options
options = Options()
options.set_preference("browser.download.folderList", 2)  # Custom location
options.set_preference("browser.download.dir", download_dir)
options.set_preference("browser.download.useDownloadDir", True)
options.set_preference(
    "browser.helperApps.neverAsk.saveToDisk",
    "text/csv,application/csv,application/vnd.ms-excel",
)

# Setup Firefox driver with options
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)


def download_csv(driver, url):
    driver.get(url)
    sleep(5)  # Esperar 5 segundos para que la página cargue completamente
    csvFileSel = "body > table > tbody > tr > td > table:nth-child(3) > tbody > tr:nth-child(1) > td > label > span.icon-file-excel > a"
    driver.find_element(By.CSS_SELECTOR, csvFileSel).click()
    sleep(10)  # Esperar 10 segundos para que el archivo se descargue


try:
    # Check if file exists
    json_path = "./stations/stations_data.json"
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"The file {json_path} does not exist. Please run scraping-mapeo.py first."
        )

    # read json file and validate it's a dictionary
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            # Explicitly load and convert JSON to dictionary
            json_str = f.read()
            stations_data = json.loads(json_str)

            # Validate that it's a dictionary
            if not isinstance(stations_data, dict):
                print(f"Current data type: {type(stations_data)}")
                raise TypeError("JSON data must be an object/dictionary at root level")

        except json.JSONDecodeError as je:
            print(f"Invalid JSON format: {je}")
            raise
except Exception as e:
    print(f"Error processing JSON file: {e}")
    raise

try:
    # download csv files from XV region
    # get stations then get all contaminants for each station
    xv_stations = stations_data.get("RI").get("stations")
    for station in xv_stations.values():
        # download csv for each contaminant
        for contaminant in station.get("contaminants").values():
            download_csv(driver, contaminant.get("graph_url"))

except FileNotFoundError as e:
    print(f"Error: {e}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    # Close the driver
    driver.quit()
