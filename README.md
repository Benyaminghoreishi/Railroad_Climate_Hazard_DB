# 🚆 Railroad Hazard Database 🌍
**Mapping Climate Extremes and Infrastructure Vulnerability: A New Database for U.S. Railroads**

# 📑 Table of Contents

1. [Overview](#-overview)  
2. [Motivation](#-motivation)  
3. [Key Contributions](#-key-contributions)  
4. [Data Sources](#-data-sources)  
5. [Methodology](#-methodology)  
6. [Folder Structure](#-folder-structure)  
   - [Raw Data (`/data/raw/`)](#-raw-data-dataraw)  
   - [Processed Data (`/data/processed/`)](#-processed-data-dataprocessed)  
   - [Scripts (`/scripts/`)](#-scripts-scripts)  
   - [Metadata (`/metadata/`)](#-metadata-metadata)  
7. [About the Data](#-about-the-data)  
8. [How to Use](#-how-to-use)  
9. [Citation and Acknowledgements](#-citation-and-acknowledgements)  
10. [Contact](#-contact)  

## 📌 Overview  
This repository curates **natural hazard datasets** and **geospatial analysis workflows** to evaluate how **flooding, extreme heat, and landslides** affect **U.S. railroad infrastructure**.  

It provides a **first-of-its-kind national database** linking natural hazard events with railroad exposure, accident records, and spatial verification.  

---

## 🎯 Motivation  
Natural hazards—flash floods, riverine floods, extreme heat (sun kinks), and landslides—pose growing risks to U.S. railroads. While derailment datasets exist, a comprehensive hazard-to-rail mapping system has been missing.  

This repository bridges that gap by:  
- Integrating datasets from **FRA, NCEI, USGS, NWS, and HUC**.  
- Building geospatial workflows to assign hazards to rail corridors.  
- Providing **verification against FRA accident records**.  

---

## 🚀 Key Contributions  
✅ **Nationwide hazard–railroad database** (2000–2024)  
✅ **Analysis of flooding, extreme heat, and landslides** on U.S. rail segments  
✅ **Advanced GIS mapping & assignments** using HUC12, NWS forecast zones, and buffers/splits  
✅ **Verification framework** cross-referencing FRA derailments with hazard events  

---

## 📂 Data Sources  
- 🛤 **Federal Railroad Administration (FRA)** – Rail accidents/incidents (Form 54)  
- 🌊 **NOAA/NCEI** – Flash floods, riverine floods, heat, and excessive heat events  
- 🏔 **USGS** – Landslide points and polygons (2000–2024) + High Water Marks (HWM)  
- 🌎 **Hydrologic Unit Code (HUC2–HUC12)** – Flood-prone watershed mapping  
- 🔥 **National Weather Service (NWS)** – Forecast zones for heat mapping  

---

## 🔍 Methodology  
1️⃣ **Data Collection & Preprocessing** – Harmonizing FRA, NCEI, USGS, and HUC datasets  
2️⃣ **Hazard Assignment** – Linking hazards to rail corridors:  
   - Floods → HUC12 → Rail  
   - Heat → NWS forecast zones → Rail  
   - Landslides → Buffers & polygon splits → Rail  
3️⃣ **Verification** – Cross-referencing hazard-exposed segments with FRA accidents  
4️⃣ **Visualization** – GIS-based hazard exposure and hotspot mapping

---

## 📁 Folder Structure

### `/data/raw/`
Contains raw input datasets from official sources:

- `RAIL_NETWORK_SHAPEFILE/`: National railroad shapefiles (lines, CSV, GeoJSON, KML formats).
- `HUC_BOUNDARIES/`: Hydrologic Unit Code (HUC2–HUC12) shapefiles for flood mapping.
- `NWS_FORECAST_ZONES/`: Forecast zone shapefiles for heat event mapping.
- `CLIMATE_DIVISIONS/`: Shapefiles for climate division boundaries.
- `COUNTY_WARNING_AREAS/`: County warning area shapefiles for heat verification.
- `STATES/`: U.S. state boundary shapefiles.
- `FLOOD/`
  - `NCEI/`: Flash flood and riverine flood event records from NCEI.
  - `USGS_HWM/`: High Water Mark flood observations from USGS.
- `HEAT/NCEI/`: Excessive heat and heat event records from NCEI.
- `LANDSLIDE/USGS/`: USGS landslide point and polygon shapefiles.
- `FRA_ACCIDENTS/`: FRA Rail Equipment Accident/Incident dataset (Form 54).

### `/data/processed/`
Processed outputs assigning hazard events to railroad infrastructure:

- `flood_assignment/`
  - `NCEI/`
    - `Flash_Flood/`
      - `Events_with_Valid_Coordinates/`: Flash flood events with valid geographic coordinates extracted from NCEI.
      - `Assigning_Outputs/`: Processed outputs assigning flash flood events to railroad infrastructure.
        - `Assigning_NCEI_to_HUC12/`: Assignment of flash flood events to HUC12 hydrologic units.
        - `Assigning_HUC12_to_Railroad/`: Assignment of flash flood events from HUC12 units to intersecting railroad segments.
    - `Riverine_Flood/`
      - `Events_with_Valid_Coordinates/`: Riverine flood events with valid geographic coordinates extracted from NCEI.
      - `Assigning_Outputs/`: Processed outputs assigning riverine flood events to railroad infrastructure.
        - `Assigning_NCEI_to_HUC12/`: Assignment of riverine flood events to HUC12 hydrologic units.
        - `Assigning_HUC12_to_Railroad/`: Assignment of riverine flood events from HUC12 units to intersecting railroad segments.
  - `USGS/`: High Water Mark (HWM) flood observations from USGS, stored in GeoPackage format.

  
- `heat_assignment/`
  - `NCEI/`
    - `Combined_Heat_ExcessiveHeat/`
      - `Events_with_Valid_Coordinates/`: Heat and excessive heat events with valid geographic coordinates extracted from NCEI.
      - `Assigning_Outputs/`: Processed outputs assigning heat and excessive heat events to railroad infrastructure.
        - `Assigning_NCEI_to_NWS_Zones/`: Assignment of heat and excessive heat events to National Weather Service (NWS) forecast zones.
        - `Assigning_NWS_Zones_to_Railroad/`: Assignment of hazard-exposed NWS forecast zones to intersecting railroad segments.
    - `Excessive_Heat/`
      - `Events_with_Valid_Coordinates/`: Excessive heat events with valid geographic coordinates extracted from NCEI.
    - `Heat/`
      - `Events_with_Valid_Coordinates/`: Heat events with valid geographic coordinates extracted from NCEI.


- `landslide_assignment/`
  - `USGS/`
    - `points/`
      - `2000-2024-points/`: Landslide point events (2000–2024) from the USGS inventory with valid date metadata.
      - `Landslide_Points_within_100m_Buffer/`: Landslide point events located within a 100-meter buffer of railroad segments.
      - `Rail_lines_with_Landslide_Attributes/`: Railroad segments assigned with attributes from nearby landslide point events.
    - `polygons/`
      - `2000-2024-polygons/`: Landslide polygon events (2000–2024) from the USGS inventory with valid date metadata.
      - `Rail_lines_split_with_Landslide_Attributes/`: Railroad segments split and assigned with attributes from intersecting landslide polygons.


### `/scripts/`
Python scripts for data processing, hazard event assignment, spatial analysis, visualization, and verification.

- `Flooding/`
  - `NCEI/`
    - `Flash_Flood/`
      - `Rail_FlashFlood_Assessment/`: Scripts for assigning flash flood events to railroad segments.
      - `Rail_FlashFlood_Visualization/`: Visualization of flash flood event frequencies and railroad exposure.
    - `Riverine_Flood/`
      - `Rail_FlashFlood_Assessment/`: Scripts for assigning riverine flood events to railroad segments.
      - `Rail_FlashFlood_Visualization/`: Visualization of riverine flood event frequencies and railroad exposure.
    - `Verification/`: Scripts for verifying flood-related train accidents against assigned flood events.
  - `USGS/`
    - `Code_USGS_Flood.py`: Script for processing USGS High Water Mark (HWM) flood data.

- `Heat/`
  - `Excessive_Heat/`
    - `Rail_ExcessiveHeat_Events_Coordinate_Assignment/`: Scripts for assigning geographic coordinates to excessive heat events.
  - `Heat/`
    - `Rail_Heat_Events_Coordinate_Assignment/`: Scripts for assigning geographic coordinates to heat events.
  - `Rail_Heat_ExtremeHeat_Assignment_and_Analysis/`: Assignment of combined heat and excessive heat events to railroad infrastructure.
  - `Verification/`: Scripts for verifying train accidents against heat and excessive heat event assignments.

- `Landslide/`
  - `Rail_Landslide_Assignment_Buffer_Split_Analysis/`: Scripts for splitting railroad lines and assigning attributes from nearby landslide points.
  - `Rail_Landslide_Buffering_and_Assignment/`: Buffering railroad segments and assigning exposure to landslide events.
  - `FilterConfidence/`: Scripts for filtering landslide events based on date and confidence level.
  - `Verification/`: Scripts for verifying railroad accidents with assigned landslide events.


### `/metadata/`
Supporting documentation:

- `dataset_description.md`: Overview of the dataset's purpose and scope.
- `variable_definitions.md`: Definitions of variables and fields.
- `methodology_summary.md`: Short summary of the processing and assignment methods.

---

## 📋 About the Data

- **Flooding Data**: Flash flood and riverine flood events from NOAA/NCEI and USGS.
- **Heat Data**: Heat and excessive heat events from NOAA/NCEI.
- **Landslide Data**: Landslide points and polygons from USGS National Landslide Inventory.
- **Railroad Network**: North American Rail Network shapefiles.

---

## 🔖 How to Use

1. **Raw data** (`/data/raw/`) contains original datasets from trusted federal sources.
2. **Processed data** (`/data/processed/`) assigns hazard exposure to railroad segments.
3. **Scripts** (`/scripts/`) enable reproduction of assignment, analysis, and verification workflows.
4. **Metadata** (`/metadata/`) documents assumptions, methods, and data fields.

---

## 🧾 Citation and Acknowledgements

If using this dataset, please cite:

> Ghoreishi, B., Staes, B.M., Liu, C., Wang, H. (2025). *Mapping Climate Extremes and Infrastructure Vulnerability: A New Database for U.S. Railroads*. Nature Scientific Data.
> DOI: (https://zenodo.org/records/15360650)

Data Sources:
- NOAA/NCEI
- USGS
- FRA (Federal Railroad Administration)

---

## 📩 Contact

For any questions, please contact:

**Benyamin Ghoreishi**  
Email: `ghoreisb@oregonstate.edu`

---
