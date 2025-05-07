from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import re

base_url = "https://sinca.mma.gob.cl/index.php/region/index/id/"

periodosPromedio = [
    "diario",
    "trimestral",
    "anual",
]

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
    "VIII",
    "IX",
    "XIV",
    "X",
    "XI",
    "XII",
]
urls = [
    f"{base_url}{regiones[0]}",
    f"{base_url}{regiones[1]}",
    f"{base_url}{regiones[2]}",
    f"{base_url}{regiones[3]}",
    f"{base_url}{regiones[4]}",
    f"{base_url}{regiones[5]}",
    f"{base_url}{regiones[6]}",
    f"{base_url}{regiones[7]}",
    f"{base_url}{regiones[8]}",
    f"{base_url}{regiones[9]}",
    f"{base_url}{regiones[10]}",
    f"{base_url}{regiones[11]}",
    f"{base_url}{regiones[12]}",
    f"{base_url}{regiones[13]}",
    f"{base_url}{regiones[14]}",
]


# Setup Firefox driver
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)
stations_by_region = {}


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
            # Get station key
            station_pattern = r"/([IVXRM]+)/([^/]+)/Cal/"
            match = re.search(station_pattern, link)
            if match:
                region_code = match.group(1)
                station_key = match.group(2)
                estaciones_keys.append(station_key)
            # Get station id
            id_pattern = r"/id/(\d+)"
            id_match = re.search(id_pattern, link)
            if id_match:
                station_id = id_match.group(1)
                estaciones_ids.append(station_id)

        stations_by_region[region_code] = {
            "names": estaciones_list,
            "keys": estaciones_keys,
            "ids": estaciones_ids,
            "number": numberStations,
        }

    except Exception as e:
        print(f"An error occurred: {e}")


for url in urls:
    getRegionStations(url)

print(stations_by_region["RXV"]["names"][0])
print(stations_by_region["RXV"]["keys"][0])
print(stations_by_region["RXV"]["ids"][0])
print(stations_by_region["RXV"]["number"])

driver.quit()
