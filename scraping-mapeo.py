from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import re
from time import sleep
from pprint import pprint
import sys  # Adding sys for exit() functionality

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
    "RXV": f"{base_url}{regiones[0]}",
    "RI": f"{base_url}{regiones[1]}",
    "RII": f"{base_url}{regiones[2]}",
    "RIII": f"{base_url}{regiones[3]}",
    "RIV": f"{base_url}{regiones[4]}",
    "RV": f"{base_url}{regiones[5]}",
    "RM": f"{base_url}{regiones[6]}",
    "RVI": f"{base_url}{regiones[7]}",
    "RVII": f"{base_url}{regiones[8]}",
    "RXVI": f"{base_url}{regiones[9]}",
    "RVIII": f"{base_url}{regiones[10]}",
    "RIX": f"{base_url}{regiones[11]}",
    "RXIV": f"{base_url}{regiones[12]}",
    "RX": f"{base_url}{regiones[13]}",
    "RXI": f"{base_url}{regiones[14]}",
    "RXII": f"{base_url}{regiones[15]}",
}

# Setup Firefox driver
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)
stations_by_region = {}
contaminants = {}


def getRegionStations(regionUrl):

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
        # Create an empty list to store station names
        estaciones_list = []
        estaciones_ids = []
        estaciones_keys = []
        estaciones_from_date = []
        estaciones_to_date = []

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
            print(f"\nAnalyzing link: {link}")  # Debug print

            # Get station key with updated pattern
            station_pattern = r"/([IVXRM]+)/([^/]+)/Cal/"
            match = re.search(station_pattern, link)
            if match:
                region_code = match.group(1)
                station_key = match.group(2)
                if station_key not in estaciones_keys:
                    estaciones_keys.append(station_key)
                if station_key not in contaminants:
                    contaminants[station_key] = []

                # Get contaminant code
            contaminant_pattern = r"macro=([^\.]+)\."
            contaminant_match = re.search(contaminant_pattern, link)
            if contaminant_match:
                contaminant_code = contaminant_match.group(1)
                contaminants[station_key].append(contaminant_code)

            # Get station id
            id_pattern = r"/id/(\d+)"
            id_match = re.search(id_pattern, link)
            if id_match:
                station_id = id_match.group(1)
                estaciones_ids.append(station_id)
            else:
                print("No match for station id pattern")  # Debug print

            # TO-DO: there are from and to dates for each contaminant
            # Get from and to dates:
            # from_pattern = (
            #     r"\&from=(\d{6})\&"  # Updated to handle URL parameters correctly
            # )
            # to_pattern = r"\&to=(\d{6})\&"  # Updated to handle URL parameters correctly

            # from_match = re.search(from_pattern, link)
            # to_match = re.search(to_pattern, link)

            # if from_match and to_match:
            #     from_date = from_match.group(1)
            #     to_date = to_match.group(1)
            #     if from_date not in estaciones_from_date:
            #         estaciones_from_date.append(from_date)
            #     if to_date not in estaciones_to_date:
            #         estaciones_to_date.append(to_date)
            # else:
            #     print("No match for date patterns")  # Debug print

        stations_by_region[region_code] = {
            "names": estaciones_list,
            "keys": estaciones_keys,
            "ids": estaciones_ids,
            "number": numberStations,
            "contaminants": contaminants,
        }

    except Exception as e:
        print(f"An error occurred: {e}")


# for url in urls:
#     getRegionStations(url)

region_code = "RVIII"
key = "830"
index = 32
try:
    getRegionStations(mapaRegionUrls[region_code])

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


def testBuildUrls():
    ## Ejemplo para un parámetro contaminante: build graphs url
    param = "PM25"
    url = (
        f"https://sinca.mma.gob.cl/cgi-bin/APUB-MMA/apub.htmlindico2.cgi"
        f"?page=pageRight"
        f'&header={stations_by_region[region_code]["names"][index]}'
        f"&gsize=1495x708"
        f"&period=specified"
        f"&from={stations_by_region[region_code]['from_date'][index]}"
        f"&to={stations_by_region[region_code]['to_date'][index]}"
        f'&macro=./{region_code}/{stations_by_region[region_code]["keys"][index]}/Cal/{param}//{param}.diario.{periodosPromedio["anual"]}.ic'
        f"&limgfrom=&limgto=&limdfrom=&limdto=&rsrc=&stnkey="
    )
    print(f"Navegando a: {url}")
    driver.get(url)
    sleep(10)
