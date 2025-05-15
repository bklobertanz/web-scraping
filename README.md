# Air Quality Data Scraper for SINCA (Sistema de Información Nacional de Calidad del Aire)

This project contains scripts to collect and download air quality data from the Chilean National Air Quality Information System (SINCA).

## Scripts Description

### scraping-mapeo.py

This script maps and collects metadata about air quality monitoring stations across different regions in Chile. It:

- Scrapes data from all regions (XV to XII, including Metropolitan Region)
- Collects information about each station including:
  - Station name
  - Station ID
  - Station key
  - Available contaminants
  - Time ranges for measurements
- Generates URLs for accessing the data graphs
- Saves all collected information in `stations/stations_data.json`

### download_csv.py

This script downloads the actual measurement data in CSV format. It:

- Uses the station information collected by scraping-mapeo.py
- Downloads CSV files for each station and contaminant
- Saves all files in the `downloads/` directory

## Supported Contaminants

The system tracks the following contaminants:

- PM10 (Particulate Matter ≤10μm)
- PM2.5 (Particulate Matter ≤2.5μm)
- NO2 (Nitrogen Dioxide)
- SO2 (Sulfur Dioxide)
- O3 (Ozone)
- CO (Carbon Monoxide)
- NOX (Nitrogen Oxides)
- NO (Nitric Oxide)
- CH4 (Methane)
- HCNM (Non-Methane Hydrocarbons)
- HCT (Total Hydrocarbons)

## Data Averaging Periods

The data can be retrieved in different averaging periods:

- Daily averages
- Quarterly averages
- Annual averages

## Usage

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
2. First run the mapping script to collect station information:
   ```
   python scraping-mapeo.py
   ```
3. Then download the data using:
   ```
   python download_csv.py
   ```

## Requirements

- Python 3.x
- Selenium WebDriver
- Firefox Browser
- Required Python packages are listed in requirements.txt

Note: The script uses Firefox WebDriver. Make sure Firefox is installed on your system.

## TODO

Future improvements and features planned for this project:

### Data Collection

- [ ] Add support for meteorological parameters collection
- [ ] Add support for custom naming when downloading files
- [ ] Add support for dynamically changing averaging periods

### Performance Improvements

- [ ] Implement parallel downloading to improve performance
- [ ] Optimize JSON file read/write operations
