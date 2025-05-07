# 🧾 Variable Definitions

This file defines all key variables used in the hazard-to-railroad exposure dataset.

| **Field Name**           | **Description**                                                                 | **Units/Format**                  |
|--------------------------|---------------------------------------------------------------------------------|-----------------------------------|
| `Segment_ID`             | Unique identifier for each railroad segment                                     | Text                              |
| `HUC12_ID`               | Hydrologic Unit Code (12-digit) used in flood exposure assignment               | Text                              |
| `Boundary_Name`          | Name of the assigned boundary zone (e.g., NWS Forecast Zone, Climate Division) | Text                              |
| `Episode_ID`             | NOAA/NCEI Episode ID grouping multiple related hazard events                    | Text                              |
| `Event_Count`            | Number of hazard events (flood/heat) assigned to the railroad segment           | Integer                           |
| `Exposure_Score`         | Weighted exposure score (event count × segment length normalized)              | Float                             |
| `Latitude`               | Latitude of the railroad segment centroid or hazard point                      | Decimal degrees                   |
| `Longitude`              | Longitude of the railroad segment centroid or hazard point                     | Decimal degrees                   |
| `Confidence_Level`       | USGS landslide event confidence rating                                          | Categorical (Level 1–8)           |
| `Distance_to_Landslide`  | Distance from railroad segment to nearest landslide point (if available)       | Meters                            |
| `Event_Date`             | Date the hazard event occurred (if recorded)                                    | YYYY-MM-DD                        |
| `Hazard_Type`            | Type of hazard assigned (Flood, Heat, Landslide)                                | Text                              |
| `Geometry_Length`        | Length of the railroad segment                                                  | Mile                              |
