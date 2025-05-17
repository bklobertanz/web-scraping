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
        "discreto": f'&macro=./{current_region_code}/{station_key}/Cal/{contaminant_code}//{contaminant_code}.discreto.{periodosPromedio["anual"]}.ic',
        "default": f"&macro=./{current_region_code}/{station_key}/Cal/{contaminant_code}//{contaminant_code}.diario.{periodo_promedio}.ic",
    }

    if contaminant_code == "PM1D" or contaminant_code == "PM2D":
        url = contaminantCodeUrlMap["discreto"]
    else:
        url = contaminantCodeUrlMap["default"]
    return url


# Check if there are more contaminants

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

        selectorNombreEstaciones = "#tablaRegional > tbody > tr > th > a"
        selectorGraficoEstaciones = "#tablaRegional > tbody > tr > td > a"

    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        # Create empty lists to store station data
        estaciones_list = []
        estaciones_ids = []
        estaciones_keys = []
        current_region_code = None

        # Wait for the table rows to be present
        nombresEstaciones = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, selectorNombreEstaciones)
            )
        )
        linksGraficos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, selectorGraficoEstaciones)
            )
        )

        estaciones_list = [nombre.text.strip() for nombre in nombresEstaciones]

        for links in linksGraficos:
            link = links.get_attribute("href")
            print(f"\nAnalyzing link: {link}")

            # Get station key
            station_pattern = r"/([IVXRM]+)/([^/]+)/Cal/"
            match = re.search(station_pattern, link)
            if match:
                current_region_code = match.group(1)
                station_key = match.group(2)
                if station_key not in estaciones_keys:
                    estaciones_keys.append(station_key)
                if station_key not in contaminants:
                    contaminants[station_key] = {}

            # Get contaminant code and contaminant graph dates
            contaminant_pattern = r"macro=([^\.]+)\."
            from_pattern = r"\&from=(\d{6})\&"
            to_pattern = r"\&to=(\d{6})\&"

            contaminant_match = re.search(contaminant_pattern, link)
            from_match = re.search(from_pattern, link)
            to_match = re.search(to_pattern, link)

            if contaminant_match and station_key:
                contaminant_code = contaminant_match.group(1)
                from_date = from_match.group(1) if from_match else None
                to_date = to_match.group(1) if to_match else None

                # Create nested structure for contaminant data
                if contaminant_code not in contaminants[station_key]:
                    contaminants[station_key][contaminant_code] = {
                        "from_date": from_date,
                        "to_date": to_date,
                    }

            # Get station id
            id_pattern = r"/id/(\d+)"
            id_match = re.search(id_pattern, link)
            if id_match:
                station_id = id_match.group(1)
                estaciones_ids.append(station_id)
            else:
                print("No match for station id pattern")

        if current_region_code:
            # Add numberStations to the dictionary
            stations_by_region["numberStations"] = numberStations
            stations_by_region["stations"] = {}

            # Add stations under the stations field
            for i, station_key in enumerate(estaciones_keys):
                stations_by_region["stations"][estaciones_list[i]] = {
                    "name": estaciones_list[i],
                    "key": station_key,
                    "id": estaciones_ids[i],
                    "contaminants": contaminants[station_key],
                }
                # Create graph URL for each contaminant
                if station_key in contaminants:
                    for contaminant_code, dates in contaminants[station_key].items():
                        from_date = dates["from_date"]
                        to_date = dates["to_date"]
                        # URL encode the station name
                        encoded_station_name = quote(estaciones_list[i])
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
