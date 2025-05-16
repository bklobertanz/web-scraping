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
import glob
import re

mapaContaminanteCodigo = {
    "PM10": "PM10",
    "PM25": "PM25",
    "0003": "NO2",
    "PM1D": "PM10-Discreto",
    "PM2D": "PM25-Discreto",
    "0001": "SO2",
    "0008": "O3",
    "0004": "CO",
    "0NOX": "NOX",
    "0002": "NO",
    "0CH4": "CH4",
    "NMHC": "HCNM",
    "THCM": "HCT",
}

periodosPromedio = {"diario": "diario", "trimestral": "trimestral", "anual": "anual"}
# Create downloads directory if it doesn't exist
download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(download_dir, exist_ok=True)


def clean_filename(text):
    """Remove or replace invalid filename characters"""
    # Replace invalid characters with underscore
    text = re.sub(r'[<>:"/\\|?*]', "_", text)
    # Remove multiple underscores
    text = re.sub(r"_+", "_", text)
    # Remove leading/trailing underscores
    return text.strip("_")


def download_csv(
    driver, url, region_code, station_name, contaminant_code, contaminant_data, period
):
    """Download CSV file and rename it with station and contaminant information"""
    # Get list of files before download
    files_before = set(glob.glob(os.path.join(download_dir, "*")))

    # Perform the download
    driver.get(url)
    sleep(5)  # Wait for page to load completely
    csvFileSel = "body > table > tbody > tr > td > table:nth-child(3) > tbody > tr:nth-child(1) > td > label > span.icon-file-excel > a"
    driver.find_element(By.CSS_SELECTOR, csvFileSel).click()

    # Wait for new file to appear and rename it
    max_wait = 30  # Maximum seconds to wait for download
    while max_wait > 0:
        sleep(1)
        files_after = set(glob.glob(os.path.join(download_dir, "*")))
        new_files = files_after - files_before
        if new_files:
            original_file_path = new_files.pop()

            # Get dates from contaminant data
            from_date = contaminant_data.get("from_date", "unknown")
            to_date = contaminant_data.get("to_date", "unknown")

            # Create new filename with all components
            clean_station = clean_filename(station_name)
            contaminant_name = mapaContaminanteCodigo.get(contaminant_code)
            new_filename = f"{region_code}_{clean_station}_{contaminant_name}_{from_date}_{to_date}_{period}.csv"
            new_file_path = os.path.join(download_dir, new_filename)

            # Rename the file
            if os.path.exists(new_file_path):
                os.remove(new_file_path)  # Remove existing file if it exists
            os.rename(original_file_path, new_file_path)

            print(f"Downloaded and renamed:")
            print(f"Region: {region_code}")
            print(f"Station: {station_name}")
            print(f"Contaminant: {contaminant_name}")
            print(f"Date range: {from_date} to {to_date}")
            print(f"New filename: {new_filename}")
            print(f"Full path: {new_file_path}")

            return new_file_path
        max_wait -= 1

    print("No new file detected after download attempt")
    return None


# Setup Firefox options
options = Options()
options.set_preference("browser.download.folderList", 2)  # Custom location
options.set_preference("browser.download.dir", download_dir)
options.set_preference("browser.download.useDownloadDir", True)
options.set_preference(
    "browser.download.manager.showWhenStarting", False
)  # Hide download manager
options.set_preference(
    "browser.download.manager.focusWhenStarting", False
)  # Don't focus download manager
options.set_preference(
    "browser.download.manager.closeWhenDone", True
)  # Close download manager when done
options.set_preference(
    "browser.helperApps.neverAsk.saveToDisk",
    "text/csv,application/csv,application/vnd.ms-excel",
)

# Setup Firefox driver with options
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

try:
    # Check if file exists
    json_path = "./stations/stations_data.json"
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"The file {json_path} does not exist. Please get all stations data first."
        )

    # read json file
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            stations_data = json.loads(f.read())
            if not isinstance(stations_data, dict):
                raise TypeError("JSON data must be an object/dictionary at root level")
        except json.JSONDecodeError as je:
            print(f"Invalid JSON format: {je}")
            raise

    # Download CSV files for each region, station, and contaminant
    # Manually set the period to "anual" for all downloads
    period = periodosPromedio["anual"]

    for region_code, region_data in stations_data.items():
        if not isinstance(region_data, dict) or "stations" not in region_data:
            continue

        for station_name, station_data in region_data["stations"].items():
            for contaminant_code, contaminant_data in station_data.get(
                "contaminants", {}
            ).items():
                file_path = download_csv(
                    driver,
                    contaminant_data.get("graph_url"),
                    region_code,
                    station_name,
                    contaminant_code,
                    contaminant_data,
                    period,
                )

except FileNotFoundError as e:
    print(f"Error: {e}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    driver.quit()
