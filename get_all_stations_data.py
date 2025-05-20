import os
import re
import json
import concurrent.futures
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
from common.web_scraping import (
    STATIONS_DIR,
    setup_driver,
    STATIONS_PATH,
    get_cached_driver_path,
)

base_url = "https://sinca.mma.gob.cl/index.php/region/index/id/"


def getMacroURL(current_region_code, station_key, contaminant_code, periodo_promedio):
    contaminantCodeUrlMap = {
        "discreto": f"&macro=./{current_region_code}/{station_key}/Cal/{contaminant_code}//{contaminant_code}.discreto.{periodo_promedio}.ic",
        "default": f"&macro=./{current_region_code}/{station_key}/Cal/{contaminant_code}//{contaminant_code}.diario.{periodo_promedio}.ic",
    }

    if contaminant_code == "PM1D" or contaminant_code == "PM2D":
        url = contaminantCodeUrlMap["discreto"]
    else:
        url = contaminantCodeUrlMap["default"]
    return url


# Check if there are more contaminants
tiposEstacion = {
    "estación pública": "estación pública",
    "estación meteorológica": "estación meteorológica",
    "en línea": "en línea",
}

periodosPromedio = {"diario": "diario", "trimestral": "trimestral", "anual": "anual"}

regiones = [
    "XV",
    "I",
    "II",
    "III",
    "IV",
    "V",
    "M",
    "VI",
    "VII",
    "XVI",
    "VIII",
    "IX",
    "XIV",
    "X",
    "XI",
    "XII",
]
mapaRegionUrls = {f"R{region}": f"{base_url}{region}" for region in regiones}


def get_tipo_estacion(estacion, nombre_tipo):

    try:
        estacion.find_element(
            By.CSS_SELECTOR, f"span[title='{tiposEstacion[nombre_tipo]}']"
        )
        return True
    except:
        return False


def extract_url_data(link):
    """Extract all relevant data from a station URL using regex patterns.

    Args:
        link (str): The URL to parse

    Returns:
        dict: Dictionary containing extracted data (region_code, station_key, station_id,
              contaminant_code, from_date, to_date)
    """
    # Define all regex patterns
    REGION_CODE_PATTERN = r"/([IVXRM]+)/"
    STATION_KEY_PATTERN = r"/[IVXRM]+/([^/]+)/Cal/"
    STATION_ID_PATTERN = r"/id/(\d+)"
    CONTAMINANT_PATTERN = r"macro=([^\.]+)\."
    FROM_DATE_PATTERN = r"\&from=(\d{6})\&"
    TO_DATE_PATTERN = r"\&to=(\d{6})\&"

    # Initialize result dictionary
    result = {
        "region_code": None,
        "station_key": None,
        "station_id": None,
        "contaminant_code": None,
        "from_date": None,
        "to_date": None,
    }

    # Extract data using regex patterns
    region_match = re.search(REGION_CODE_PATTERN, link)
    station_key_match = re.search(STATION_KEY_PATTERN, link)
    station_id_match = re.search(STATION_ID_PATTERN, link)
    contaminant_match = re.search(CONTAMINANT_PATTERN, link)
    from_match = re.search(FROM_DATE_PATTERN, link)
    to_match = re.search(TO_DATE_PATTERN, link)

    # Update result dictionary with matched groups
    if region_match:
        result["region_code"] = region_match.group(1)
    if station_key_match:
        result["station_key"] = station_key_match.group(1)
    if station_id_match:
        result["station_id"] = station_id_match.group(1)
    if contaminant_match:
        result["contaminant_code"] = contaminant_match.group(1)
    if from_match:
        result["from_date"] = from_match.group(1)
    if to_match:
        result["to_date"] = to_match.group(1)

    return result


def getRegionStations(driver, regionUrl):
    stations_by_region = {}
    contaminants = {}
    if not regionUrl:
        print("Invalid region URL")
        return

    try:
        # Navigate to the page
        driver.get(regionUrl)
        # Wait for the caption element to be present
        caption = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "caption#tableRows"))
        )

        # Get the caption text and extract just the number
        caption_text = caption.text
        numberStations = caption_text.split(":")[1].strip()

        selector_estacion = "#tablaRegional > tbody > tr"
        selector_tags_link_estaciones = "#tablaRegional > tbody > tr > td > a"

    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        # Create empty lists to store station data
        estaciones_info_basica = []
        estaciones_ids = []
        estaciones_keys = []
        current_region_code = None

        # Wait for the table rows to be present
        estaciones = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector_estacion))
        )
        tags_link_estaciones = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, selector_tags_link_estaciones)
            )
        )
        # Get station basic data
        for estacion in estaciones:
            # Get the name of the station
            nombre = estacion.find_element(By.CSS_SELECTOR, "a")
            ficha_url = nombre.get_attribute("href")

            # Get types of station by checking element existence
            estaciones_info_basica.append(
                {
                    "nombre": nombre.text.strip(),
                    "ficha_url": ficha_url,
                    "en_linea": get_tipo_estacion(estacion, tiposEstacion["en línea"]),
                    "estacion_meteorologica": get_tipo_estacion(
                        estacion, tiposEstacion["estación meteorológica"]
                    ),
                    "estacion_publica": get_tipo_estacion(
                        estacion, tiposEstacion["estación pública"]
                    ),
                }
            )

        urls_estaciones = [link.get_attribute("href") for link in tags_link_estaciones]

        for url in urls_estaciones:
            print(f"\nAnalyzing url: {url}")

            # Extract all URL data using the new function
            url_data = extract_url_data(url)

            if url_data["region_code"] and url_data["station_key"]:
                current_region_code = url_data["region_code"]
                station_key = url_data["station_key"]
                if station_key not in estaciones_keys:
                    estaciones_keys.append(station_key)
                if station_key not in contaminants:
                    contaminants[station_key] = {}

            if url_data["contaminant_code"] and station_key:
                contaminant_code = url_data["contaminant_code"]
                if contaminant_code not in contaminants[station_key]:
                    contaminants[station_key][contaminant_code] = {
                        "from_date": url_data["from_date"],
                        "to_date": url_data["to_date"],
                    }

            if url_data["station_id"]:
                estaciones_ids.append(url_data["station_id"])

        if current_region_code:
            # Add numberStations to the dictionary
            stations_by_region["number_stations"] = numberStations
            stations_by_region["stations"] = {}

            # Add stations under the stations field
            for i, station_key in enumerate(estaciones_keys):
                station_info = estaciones_info_basica[i]
                stations_by_region["stations"][station_info["nombre"]] = {
                    "name": station_info["nombre"],
                    "en_linea": station_info["en_linea"],
                    "estacion_meteorologica": station_info["estacion_meteorologica"],
                    "estacion_publica": station_info["estacion_publica"],
                    "ficha_url": station_info["ficha_url"],
                    "key": station_key,
                    "id": estaciones_ids[i],
                    "contaminants": contaminants[station_key],
                }
                # Create graph URL for each contaminant

                if station_key in contaminants:
                    for contaminant_code, dates in contaminants[station_key].items():
                        from_date = dates["from_date"]
                        to_date = dates["to_date"]
                        encoded_station_name = quote(station_info["nombre"])
                        macroURL = getMacroURL(
                            current_region_code,
                            station_key,
                            contaminant_code,
                            periodosPromedio["anual"],
                        )
                        contaminant_graph_url = (
                            f"https://sinca.mma.gob.cl/cgi-bin/APUB-MMA/apub.htmlindico2.cgi"
                            f"?page=pageRight"
                            f"&header={encoded_station_name}"
                            f"&gsize=1495x708"
                            f"&period=specified"
                            f"&from={from_date}"
                            f"&to={to_date}"
                            f"{macroURL}"
                            f"&limgfrom=&limgto=&limdfrom=&limdto=&rsrc=&stnkey="
                        )
                        contaminants[station_key][contaminant_code][
                            "graph_url"
                        ] = contaminant_graph_url
        else:
            print("No region code found in the analyzed links")
        return stations_by_region

    except Exception as e:
        print(f"An error occurred: {e}")
        raise


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


def process_region(region_code, region_url):
    """Process a single region with its own driver instance"""
    driver = None
    try:
        driver = setup_driver()
        result = getRegionStations(driver, region_url)
        return region_code, result
    except Exception as e:
        print(f"Error processing region {region_code}: {e}")
        return region_code, None
    finally:
        if driver:
            driver.quit()


def main():
    try:
        # First ensure driver is cached
        if not ensure_driver_cached():
            raise Exception("Failed to cache GeckoDriver")

        stations = {}
        # Maximum number of concurrent processes based on CPU cores
        max_workers = min(len(mapaRegionUrls), os.cpu_count() or 1)

        print(f"Processing {len(mapaRegionUrls)} regions with {max_workers} workers")

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers
        ) as executor:
            # Create future tasks for each region
            future_to_region = {
                executor.submit(process_region, region_code, region_url): region_code
                for region_code, region_url in mapaRegionUrls.items()
            }

            # Process completed tasks as they finish
            for future in concurrent.futures.as_completed(future_to_region):
                region_code = future_to_region[future]
                result = future.result()[1]  # Get the second element of the tuple
                if result:
                    stations[region_code] = result
                    print(f"Completed processing region: {region_code}")

        # Save results to JSON
        os.makedirs(STATIONS_DIR, exist_ok=True)
        with open(STATIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(stations, f, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {STATIONS_PATH}")

    except Exception as e:
        print(f"An error occurred in main: {e}")


if __name__ == "__main__":
    main()
