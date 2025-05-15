from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import re
from time import sleep
from pprint import pprint
import sys
from urllib.parse import quote  # Adding URL encoding functionality

base_url = "https://sinca.mma.gob.cl/index.php/region/index/id/"

# Check if there are more contaminants

mapaContaminanteCodigo = {
    "PM10": "PM10",
    "PM25": "PM25",
    "NO2": "0003",
    "SO2": "0001",
    "O3": "0008",
    "CO": "0004",
    "NOX": "0NOX",
    "NO": "0002",
    "CH4": "0CH4",
    "HCNM": "NMHC",
    "HCT": "THCM",
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

# Setup Firefox driver
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)


def getRegionStations(regionUrl):
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

            stations_by_region[current_region_code] = {"numberStations": numberStations}
            for i, station_key in enumerate(estaciones_keys):
                stations_by_region[current_region_code][estaciones_list[i]] = {
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
                        contaminant_graph_url = (
                            f"https://sinca.mma.gob.cl/cgi-bin/APUB-MMA/apub.htmlindico2.cgi"
                            f"?page=pageRight"
                            f"&header={encoded_station_name}"
                            f"&gsize=1495x708"
                            f"&period=specified"
                            f"&from={from_date}"
                            f"&to={to_date}"
                            f'&macro=./{current_region_code}/{station_key}/Cal/{contaminant_code}//{contaminant_code}.diario.{periodosPromedio["anual"]}.ic'
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


stations = {}
for region_code, region_url in mapaRegionUrls.items():
    stations[region_code] = getRegionStations(region_url)

try:
    pprint(stations)
    sys.exit()

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()
