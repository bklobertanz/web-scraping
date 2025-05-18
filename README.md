# Air Quality Data Scraper for SINCA

A Python-based tool for downloading air quality data from Chile's National Air Quality System (SINCA). The tool supports parallel processing for efficient data collection across multiple monitoring stations.

## Features

### Station Data Collection

- Multi-region coverage (XV to XII, including Metropolitan Region)
- Parallel processing for faster data gathering
- Automatic caching of web driver
- Process-specific download management
- Custom file naming conventions

### Data Types

- Air quality measurements
- Station metadata
- Historical records
- Multiple averaging periods (daily, quarterly, annual)

## Supported Contaminants

| Code | Contaminant | Description               |
| ---- | ----------- | ------------------------- |
| PM10 | PM10        | Particulate Matter ≤10μm  |
| PM25 | PM2.5       | Particulate Matter ≤2.5μm |
| NO2  | NO2         | Nitrogen Dioxide          |
| SO2  | SO2         | Sulfur Dioxide            |
| O3   | O3          | Ozone                     |
| CO   | CO          | Carbon Monoxide           |
| NOX  | NOX         | Nitrogen Oxides           |
| NO   | NO          | Nitric Oxide              |
| CH4  | CH4         | Methane                   |
| HCNM | HCNM        | Non-Methane Hydrocarbons  |
| HCT  | HCT         | Total Hydrocarbons        |

## Setup

### Requirements

- Python 3.x
- Firefox Browser
- Internet connection

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### File Structure

```
project/
├── data/
│   ├── stations/
│   │   └── stations_data.json
│   └── contaminants/
│       └── process_{pid}/
├── common/
│   └── web_scraping.py
├── get_all_stations_data.py
└── download_csv.py
```

## Usage

1. Collect station information:

```bash
python get_all_stations_data.py
```

2. Download contaminant data:

```bash
python download_csv.py
```

When prompted, select period:

- 1: Daily
- 2: Quarterly
- 3: Annual

## TODO

Future improvements and features planned for this project:

### Data Collection

- [ ] Add support for meteorological parameters collection
- [x] Handle Github Gecko API rate limiting -> Cache gecko driver.
- [x] Add support for custom naming when downloading files
- [x] Add support for dynamically changing averaging periods
- [x] In downloaded file name use contaminant name and not its code.
- [x] Check problems with contaminant link that includes CONAMA: PM2D, PM1D, NMHC, 0CH4, 0NOX, 0003 - PM1D and PM2D builds urls differently from other contaminants: ./RII/225/Cal/PM1D&macro=PM1D.discreto.diario -> improve waiting on blocking element and appearing csv download button (a tag).

### Performance Improvements

- [x] Implement parallel downloading to improve performance:
      [X] Make sure that gecko driver is cached and then execute workers.
      [X] Get all stations data.
      [X] Download CSV files -> creation of a folder for each specific process.
- [ ] Optimize JSON file read/write operations
