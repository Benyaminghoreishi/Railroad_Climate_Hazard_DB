# 🛠️ Methodology Summary for Hazard-to-Railroad Database (2000–2024)

This file summarizes the methodology used to assign natural hazard events—including flooding, heat, and landslides—to the U.S. railroad network using spatial analysis of federal datasets. The resulting dataset enables infrastructure vulnerability assessment and hazard exposure modeling for climate resilience applications.

---

## 🌊 Flooding

- **Sources**:  
  - NOAA NCEI Storm Events Database  
  - USGS High Water Marks (HWM)

- **Assignment Method**:  
  Events were geolocated and assigned to 12-digit Hydrologic Unit Code (HUC-12) subwatersheds. Railroad segments intersecting these HUC polygons were considered exposed. Duplicate episode IDs within each HUC were filtered out to prevent overcounting.

---

## 🔥 Heat and Excessive Heat

- **Sources**:  
  - NOAA NCEI Storm Events Database

- **Assignment Method**:  
  Events were geolocated via Federal Information Processing Standards (FIPS) codes and linked to National Weather Service (NWS) forecast zones. Railroad segments intersecting these forecast zones with heat events were considered exposed. Heat and excessive heat were analyzed as a combined category.

---

## 🪨 Landslides

- **Source**:  
  - USGS National Landslide Inventory (v3.0)

- **Assignment Method**:  
  Point-based landslides were assigned to railroad segments using a 100-meter spatial buffer. Polygon-based landslides were directly intersected with railroad lines. Only records with valid temporal metadata (Date_Min) between 2000 and 2024 were included in the final dataset.

---

## 🗺️ Temporal Coverage

- **Start Year**: 2000  
- **End Year**: 2024  
- **Rationale**: Consistent metadata availability across NCEI and USGS datasets, aligned with FRA accident records for verification.

---

## 🚆 Railroad Infrastructure Data

- **Source**: FRA North American Rail Network  
- **Format**: Shapefile (Line format)  
- **Purpose**: Used as the base layer for all spatial intersection operations with hazard events.

---

## ✅ Verification Method

- **Reference Dataset**: FRA Rail Equipment Accident/Incident Data (Form 54)

- **Method**:  
  Spatial and temporal matching was performed between assigned hazard events and accident records. Relevant records were filtered using FRA cause codes and keyword searches (e.g., “washout,” “sun kink,” “slide”). Verification checks occurred across multiple spatial scales (HUCs, forecast zones, counties) and temporal windows (exact day, full month).

---

## 🧾 Output Layers

- `hazard_event_points/`: Raw and geolocated hazard event records  
- `railroad_segments_with_hazard_assignments/`: Segments with assigned hazard exposures  
- `verification_matches/`: Records of accidents with spatial and/or temporal overlap with hazards

---

## 📦 Data Format

- **Types**:
  - GeoPackage (.gpkg)  
  - ESRI Shapefile (.shp)  
  - CSV (.csv)

- **Coordinate Reference System**: EPSG:4326 (WGS 84)

---

## 🎯 Intended Use

- Infrastructure risk analysis  
- Resilience planning  
- Climate hazard mapping  
- Exposure quantification  
- Academic research in transportation vulnerability

---

## ⚠️ Limitations

- Landslide data has limited temporal coverage due to sparse event dates.  
- Flood and heat assignments assume all railroad segments within a hazard zone (HUC or forecast zone) are exposed, which may overestimate localized impact.
