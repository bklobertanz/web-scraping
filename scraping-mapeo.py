from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import re
from time import sleep

base_url = "https://sinca.mma.gob.cl/index.php/region/index/id/"

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
                estaciones_keys.append(station_key)

            # Get station id
            id_pattern = r"/id/(\d+)"
            id_match = re.search(id_pattern, link)
            if id_match:
                station_id = id_match.group(1)
                estaciones_ids.append(station_id)
            else:
                print("No match for station id pattern")  # Debug print

            # Get from and to dates with updated patterns
            from_pattern = (
                r"\&from=(\d{6})\&"  # Updated to handle URL parameters correctly
            )
            to_pattern = r"\&to=(\d{6})\&"  # Updated to handle URL parameters correctly

            from_match = re.search(from_pattern, link)
            to_match = re.search(to_pattern, link)

            if from_match and to_match:
                from_date = from_match.group(1)
                to_date = to_match.group(1)
                estaciones_from_date.append(from_date)
                estaciones_to_date.append(to_date)
            else:
                print("No match for date patterns")  # Debug print

        stations_by_region[region_code] = {
            "names": estaciones_list,
            "keys": estaciones_keys,
            "ids": estaciones_ids,
            "from_date": estaciones_from_date,
            "to_date": estaciones_to_date,
            "number": numberStations,
        }

    except Exception as e:
        print(f"An error occurred: {e}")


# for url in urls:
#     getRegionStations(url)

index = 0
region_code = "RXV"

getRegionStations(urls[index])

print(stations_by_region[region_code]["names"][index])
print(stations_by_region[region_code]["keys"][index])
print(stations_by_region[region_code]["ids"][index])
print(stations_by_region[region_code]["from_date"][index])
print(stations_by_region[region_code]["to_date"][index])
print(stations_by_region[region_code]["number"])

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
driver.quit()
