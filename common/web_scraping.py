from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import os
import time
import platform
from requests.exceptions import ConnectionError

DATA_DIR = "./data"
STATIONS_DIR = f"{DATA_DIR}/stations"
CSV_CONTAMINANTS_DIR = f"{DATA_DIR}/contaminants"
DRIVER_CACHE_DIR = "./.driver_cache"  # Local cache directory for the driver

STATIONS_FILENAME = "stations_data.json"
STATIONS_PATH = f"{STATIONS_DIR}/{STATIONS_FILENAME}"


def get_cached_driver_path():
    """Get the path to the cached driver"""
    system = platform.system().lower()
    if system == "linux":
        driver_name = "geckodriver"
    elif system == "windows":
        driver_name = "geckodriver.exe"
    else:  # darwin (MacOS)
        driver_name = "geckodriver"

    return os.path.join(DRIVER_CACHE_DIR, driver_name)


def setup_driver(download_dir=None):
    """Setup and return a Firefox driver with proper options"""
    options = webdriver.FirefoxOptions()

    # Create cache directory if it doesn't exist
    os.makedirs(DRIVER_CACHE_DIR, exist_ok=True)

    cached_driver = get_cached_driver_path()

    # Basic preferences to prevent download dialogs
    options.set_preference("browser.download.panel.shown", False)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.manager.showAlertOnComplete", False)
    options.set_preference("browser.download.folderList", 2)  # Use custom location
    options.set_preference("browser.download.useDownloadDir", True)

    # Set up MIME types for automatic downloads
    options.set_preference(
        "browser.helperApps.neverAsk.saveToDisk",
        "text/csv,application/csv,application/vnd.ms-excel,text/comma-separated-values,text/xml,application/xml",
    )

    # Configure download behavior
    if download_dir:
        download_dir = os.path.abspath(download_dir)
        print(f"Setting download directory to: {download_dir}")
        options.set_preference("browser.download.dir", download_dir)

    options.set_preference("browser.download.manager.useWindow", False)
    options.set_preference("browser.download.manager.focusWhenStarting", False)
    options.set_preference("browser.download.alwaysOpenPanel", False)
    options.set_preference(
        "browser.download.always_ask_before_handling_new_types", False
    )

    # Add retry logic for driver installation
    max_retries = 5
    retry_delay = 30  # seconds
    last_exception = None

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(
                    f"Retry attempt {attempt + 1}/{max_retries} after {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

            if os.path.exists(cached_driver) and os.access(cached_driver, os.X_OK):
                print("Using cached GeckoDriver")
                service = Service(cached_driver)
            else:
                print("Downloading GeckoDriver...")
                # Download the driver
                driver_path = GeckoDriverManager().install()
                # Copy to our cache location
                import shutil

                shutil.copy2(driver_path, cached_driver)
                # Ensure the driver is executable
                os.chmod(cached_driver, 0o755)
                print(f"GeckoDriver cached at: {cached_driver}")
                service = Service(cached_driver)

            return webdriver.Firefox(service=service, options=options)

        except ConnectionError as e:
            print(f"Connection error while downloading driver: {e}")
            last_exception = e
        except Exception as e:
            print(f"Error downloading driver: {e}")
            last_exception = e

    raise Exception(
        f"Failed to install driver after {max_retries} attempts. Last error: {last_exception}"
    )
