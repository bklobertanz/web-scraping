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
mapaRegionUrls = {
    f"R{regiones[0]}": f"{base_url}{regiones[0]}",
    f"R{regiones[1]}": f"{base_url}{regiones[1]}",
    f"R{regiones[2]}": f"{base_url}{regiones[2]}",
    f"R{regiones[3]}": f"{base_url}{regiones[3]}",
    f"R{regiones[4]}": f"{base_url}{regiones[4]}",
    f"R{regiones[5]}": f"{base_url}{regiones[5]}",
    f"R{regiones[6]}": f"{base_url}{regiones[6]}",
    f"R{regiones[7]}": f"{base_url}{regiones[7]}",
    f"R{regiones[8]}": f"{base_url}{regiones[8]}",
    f"R{regiones[9]}": f"{base_url}{regiones[9]}",
    f"R{regiones[10]}": f"{base_url}{regiones[10]}",
    f"R{regiones[11]}": f"{base_url}{regiones[11]}",
    f"R{regiones[12]}": f"{base_url}{regiones[12]}",
    f"R{regiones[13]}": f"{base_url}{regiones[13]}",
    f"R{regiones[14]}": f"{base_url}{regiones[14]}",
    f"R{regiones[15]}": f"{base_url}{regiones[15]}",
}

# Setup Firefox driver
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)
stations_by_region = {}
contaminants = {}


def getRegionStations(regionUrl):
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

            # Get station key with updated pattern
            station_pattern = r"/([IVXRM]+)/([^/]+)/Cal/"
            match = re.search(station_pattern, link)
            if match:
                current_region_code = match.group(1)
                station_key = match.group(2)
                if station_key not in estaciones_keys:
                    estaciones_keys.append(station_key)
                if station_key not in contaminants:
                    contaminants[station_key] = {}

            # Get contaminant code and dates
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
            stations_by_region[current_region_code] = {
                "names": estaciones_list,
                "keys": estaciones_keys,
                "ids": estaciones_ids,
                "number": numberStations,
                "contaminants": contaminants,
            }
            # Create graph URL for each contaminant
            for i, station_key in enumerate(estaciones_keys):
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

    except Exception as e:
        print(f"An error occurred: {e}")
        raise


# for url in urls:
#     getRegionStations(url)

region_code = "RVIII"
key = "830"
index = 32
try:
    getRegionStations(mapaRegionUrls[region_code])
    pprint(stations_by_region[region_code])
    sys.exit()
    # Print basic station information
    print("\nStation Information:")
    print(f"Name: {stations_by_region[region_code]['names'][index]}")
    print(f"Key: {stations_by_region[region_code]['keys'][index]}")
    print(f"ID: {stations_by_region[region_code]['ids'][index]}")
    print(f"Number of stations: {stations_by_region[region_code]['number']}")
    print(f"Contaminants: {contaminants[key]}")

    # Get and print contaminants for the current station
    station_key = stations_by_region[region_code]["keys"][index]
    print(f"Contaminants for station {station_key}:")
    if station_key in stations_by_region[region_code]["contaminants"]:
        print(stations_by_region[region_code]["contaminants"][station_key])
    else:
        print("No contaminants found for this station")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()
