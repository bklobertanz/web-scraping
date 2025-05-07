from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

base_url = "https://sinca.mma.gob.cl/index.php/region/index/id/"
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
        print(f"Number of stations: {numberStations}")

        selectorNombreEstaciones = "#tablaRegional > tbody > tr > th > a"

    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        # Create an empty list to store station names
        estaciones_list = []

        # Wait for the table rows to be present
        nombresEstaciones = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, selectorNombreEstaciones)
            )
        )

        # Method 1: Using list comprehension (most efficient)
        estaciones_list = [nombre.text.strip() for nombre in nombresEstaciones]

        # Method 2: Using append (if you need to add elements one by one)
        # for nombre in nombresEstaciones:
        #     estaciones_list.append(nombre.text.strip())

        # Print the list to verify
        print("List of stations:")
        for nombre in estaciones_list:
            print(nombre)

        # You can also add more elements later using:
        # estaciones_list.append("New Station")  # Adds one element
        # estaciones_list.extend(["Station 1", "Station 2"])  # Adds multiple elements

        print(f"Total number of stations: {len(estaciones_list)}")

    except Exception as e:
        print(f"An error occurred: {e}")


for url in urls:
    getRegionStations(url)

driver.quit()
