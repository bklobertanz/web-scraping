from time import sleep
import json
import os
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.web_scraping import (
    CSV_CONTAMINANTS_DIR,
    STATIONS_PATH,
    setup_driver,
)


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
    download_dir = CSV_CONTAMINANTS_DIR

    # Get list of files before download
    files_before = set(os.listdir(download_dir))

    # Perform the download
    driver.get(url)
    sleep(5)  # Wait for page to load completely
    csvFileSel = "body > table > tbody > tr > td > table:nth-child(3) > tbody > tr:nth-child(1) > td > label > span.icon-file-excel > a"
    driver.find_element(By.CSS_SELECTOR, csvFileSel).click()

    # Wait for new file to appear and rename it
    max_wait = 5  # Maximum seconds to wait for download
    while max_wait > 0:
        sleep(1)
        # Check for new files directly in the download directory
        files_after = set(os.listdir(download_dir))
        new_files = files_after - files_before

        if new_files:
            original_file = next(
                iter(new_files)
            )  # Get the first (and should be only) new file
            original_file_path = os.path.join(download_dir, original_file)

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


try:
    driver = setup_driver(CSV_CONTAMINANTS_DIR)

    # Check if file exists
    if not os.path.exists(STATIONS_PATH):
        raise FileNotFoundError(
            f"The file {STATIONS_PATH} does not exist. Please get all stations data first."
        )

    # read json file
    with open(STATIONS_PATH, "r", encoding="utf-8") as f:
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
    # Create downloads directory if it doesn't exist
    os.makedirs(CSV_CONTAMINANTS_DIR, exist_ok=True)

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
