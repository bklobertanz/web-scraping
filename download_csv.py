from time import sleep, time
from datetime import datetime
import json
import os
import re
import concurrent.futures
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.web_scraping import (
    CSV_CONTAMINANTS_DIR,
    STATIONS_PATH,
    setup_driver,
    get_cached_driver_path,
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
    base_download_dir = CSV_CONTAMINANTS_DIR
    process_id = os.getpid()
    # Get the process-specific download directory
    download_dir = os.path.join(base_download_dir, f"process_{process_id}")

    # Get list of files before download
    files_before = set(os.listdir(download_dir))  # Changed from base_download_dir

    # Perform the download
    driver.get(url)

    # Wait for any loading screen to disappear
    try:
        screen_overlay = WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "screen"))
        )
    except Exception as e:
        print(f"Warning: Loading screen handling error: {e}")

    # Wait for the download button and try different methods to click it
    csvFileSel = "body > table > tbody > tr > td > table:nth-child(3) > tbody > tr:nth-child(1) > td > label > span.icon-file-excel > a"
    try:
        download_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, csvFileSel))
        )

        # Try clicking with JavaScript if normal click doesn't work
        try:
            download_button.click()
        except Exception as e:
            print("Regular click failed, trying JavaScript click...")
            driver.execute_script("arguments[0].click();", download_button)

    except Exception as e:
        print(f"Error clicking download button: {e}")
        raise

    # Wait for new file to appear and rename it
    max_wait = 5  # Maximum seconds to wait for download
    while max_wait > 0:
        sleep(1)
        # Check for new files in the process-specific directory
        files_after = set(os.listdir(download_dir))  # Changed from base_download_dir
        new_files = files_after - files_before

        if new_files:
            original_file = next(iter(new_files))
            original_file_path = os.path.join(download_dir, original_file)

            # Get dates from contaminant data
            from_date = contaminant_data.get("from_date", "unknown")
            to_date = contaminant_data.get("to_date", "unknown")

            # Create new filename with all components
            clean_station = clean_filename(station_name)
            contaminant_name = mapaContaminanteCodigo.get(contaminant_code)
            new_filename = f"{region_code}_{clean_station}_{contaminant_name}_{from_date}_{to_date}_{period}.csv"
            # Place the final file in the base download directory
            new_file_path = os.path.join(base_download_dir, new_filename)

            # Rename the file
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
            os.rename(original_file_path, new_file_path)

            # Clean up process directory if empty
            if not os.listdir(download_dir):
                os.rmdir(download_dir)

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


def ensure_driver_cached():
    """Ensure GeckoDriver is downloaded and cached before parallel processing"""
    print("Ensuring GeckoDriver is cached...")
    driver = None
    try:
        driver = setup_driver()
        cached_path = get_cached_driver_path()
        if os.path.exists(cached_path):
            print(f"GeckoDriver successfully cached at: {cached_path}")
            return True
    except Exception as e:
        print(f"Error caching driver: {e}")
        return False
    finally:
        if driver:
            driver.quit()


def process_station_contaminant(
    region_code, station_name, station_data, contaminant_code, contaminant_data, period
):
    """Process a single station-contaminant combination with its own driver instance"""
    driver = None
    try:
        driver = setup_driver(CSV_CONTAMINANTS_DIR)
        return download_csv(
            driver,
            contaminant_data.get("graph_url"),
            region_code,
            station_name,
            contaminant_code,
            contaminant_data,
            period,
        )
    except Exception as e:
        print(
            f"Error processing {region_code} - {station_name} - {contaminant_code}: {e}"
        )
        return None
    finally:
        if driver:
            driver.quit()


def main():
    start_time = time()
    start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Starting downloads at: {start_datetime}")

    try:
        # First ensure driver is cached
        if not ensure_driver_cached():
            raise Exception("Failed to cache GeckoDriver")

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
                    raise TypeError(
                        "JSON data must be an object/dictionary at root level"
                    )
            except json.JSONDecodeError as je:
                print(f"Invalid JSON format: {je}")
                raise

        # Create downloads directory if it doesn't exist
        os.makedirs(CSV_CONTAMINANTS_DIR, exist_ok=True)

        # Create a list of all tasks to process
        tasks = []
        period = periodosPromedio["anual"]

        for region_code, region_data in stations_data.items():
            if not isinstance(region_data, dict) or "stations" not in region_data:
                continue

            for station_name, station_data in region_data["stations"].items():
                for contaminant_code, contaminant_data in station_data.get(
                    "contaminants", {}
                ).items():
                    tasks.append(
                        (
                            region_code,
                            station_name,
                            station_data,
                            contaminant_code,
                            contaminant_data,
                            period,
                        )
                    )

        print(f"Processing {len(tasks)} downloads...")

        # Maximum number of concurrent processes based on CPU cores (divided by 2 for resource management)
        max_workers = min(len(tasks), os.cpu_count() or 1) // 2
        print(f"Using {max_workers} concurrent workers")

        successful_downloads = 0
        failed_downloads = 0

        # Process tasks concurrently
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers
        ) as executor:
            futures = []
            for task in tasks:
                futures.append(executor.submit(process_station_contaminant, *task))

            # Process completed tasks as they finish
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        successful_downloads += 1
                        print(f"Successfully downloaded: {os.path.basename(result)}")
                    else:
                        failed_downloads += 1
                except Exception as e:
                    failed_downloads += 1
                    print(f"Task failed: {e}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    end_time = time()
    end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elapsed_time = end_time - start_time

    print("\nDownload Summary:")
    print(f"Start time: {start_datetime}")
    print(f"End time: {end_datetime}")
    print(
        f"Total elapsed time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)"
    )
    print(f"Successful downloads: {successful_downloads}")
    print(f"Failed downloads: {failed_downloads}")
    print(f"Total downloads attempted: {successful_downloads + failed_downloads}")


if __name__ == "__main__":
    main()
