# 📦 Dataset Description for Hazard-to-Railroad Infrastructure Mapping (2000–2024)

This dataset provides a geospatial mapping of natural hazard exposures—including riverine floods, flash floods, extreme heat, and landslides—to U.S. railroad infrastructure from 2000 to 2024. It integrates multiple public datasets from federal agencies and applies spatial methods to assign hazard events to specific railroad segments.

---

## 👥 Contributors

- **Benyamin Ghoreishi** — Oregon State University  
  *Role: Dataset curator, lead analyst*

- **Brian M. Staes** — Oregon State University  
  *Role: Methodology, data verification*

- **Chenqiang Liu** — Oregon State University  
  *Role: Code review and technical support*

- **Haizhong Wang** — Oregon State University  
  *Role: Principal investigator*

---

## 🌐 Geographic Scope

- **Coverage**: Continental United States

---

## 📆 Temporal Coverage

- **Start Year**: 2000  
- **End Year**: 2024  
- **Justification**: Aligned with consistent hazard metadata availability and FRA accident reporting records

---

## 📂 Data Contents

- `raw_hazard_events/`:  
  Original hazard event records from NCEI and USGS, including floods, excessive heat, and landslides with associated geolocation and date metadata.

- `assigned_hazard_exposures/`:  
  Railroad segments assigned hazard exposure using spatial joins (e.g., HUC-12 boundaries, forecast zones, proximity buffers).

- `verification_outputs/`:  
  Spatial and temporal matches between FRA accident records and assigned hazard events to assess data validity and exposure plausibility.

---

## 🗃️ Formats

- **Geospatial**: ESRI Shapefile (.shp), GeoJSON (.geojson), GeoPackage (.gpkg)  
- **Tabular**: CSV (.csv)  
- **Metadata**: Markdown (.md), YAML (.yaml)

---

## 🧭 Coordinate Reference System

- **CRS**: EPSG:4326 (WGS 84)

---

## 🎯 Intended Use

This dataset is intended for researchers, transportation planners, and policymakers interested in:

- Infrastructure risk analysis  
- Climate resilience  
- Disaster impact modeling  
- Hazard vulnerability assessments

---

## 🔓 Access Rights

- Open upon reasonable request from the corresponding author.

---

## 📬 Contact

- **Name**: Benyamin Ghoreishi  
- **Email**: ghoreisb@oregonstate.edu  
- **Institution**: Oregon State University

---

## 💰 Funding

- **Agency**: Federal Railroad Administration (FRA)  
- **Program**: CRISI – Climate Change and Extreme Events Training and Research Program (CCEETR)
