# %%
# ! ################################################################################################
# ! # Title: Landslide Verification with USGS Data
# ! Purpose: Match railroad landslide incidents with USGS landslide data by date and location,
# !          and calculate the distance between incidents and landslide events.
# ! Run Time: [Depends on data size, est. few minutes]
# ! ################################################################################################

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# %% Load buckling accident points
accident_fp = (
        r"C:\Users\ghoreisb\Box\Oregon State University"
        r"\000- Papers\Publish Purpose"
        r"\2025\New_Journal\Verification\Landslide\landslide_accidents.csv"
)
accidents_df = pd.read_csv(accident_fp, encoding='ISO-8859-1')

# Load Landslide GeoPackage file
landslide_fp = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU"
    r"\1_Rail_Project\7_Landslide\Data\Ver.3.0.Feb2025"
    r"\US_Landslide_v3_csv\us_ls_v3_point_with_dates_2000_2024.gpkg"
)
landslide_gdf = gpd.read_file(landslide_fp)

# Extract lat/lon from 'Location' WKT
accidents_df['Longitude'] = accidents_df['Location'] \
    .str.extract(r'POINT \((-?\d+\.\d+)')[0] \
    .astype(float)
accidents_df['Latitude'] = accidents_df['Location'].str.extract(
    r'POINT \(-?\d+\.\d+ (\d+\.\d+)\)'
)[0].astype(float)

# Create GeoDataFrame
accidents_gdf = gpd.GeoDataFrame(
    accidents_df,
    geometry=gpd.points_from_xy(
        accidents_df['Longitude'], accidents_df['Latitude']
    ),
    crs="EPSG:4326"
)

# Add accident date
accidents_gdf['Accident_Date'] = pd.to_datetime(
    accidents_gdf[['Year', 'Accident Month', 'Day']].rename(
        columns={
            'Year': 'year',
            'Accident Month': 'month',
            'Day': 'day'
        }
    )
)

# %%
# ! ################################################################################################
# ! # Title: Landslide Points Verification with Distance Buffers Only
# ! Purpose: For each accident point, create buffers (50m and 100m), check intersecting landslide points,
# !          and record counts in new columns.
# ! Run Time: [Depends on data size, est. few minutes]
# ! ################################################################################################

# Reproject both datasets to a metric CRS for accurate buffering (EPSG:5070 - Albers Equal Area)
accidents_gdf_proj = accidents_gdf.to_crs("EPSG:5070")
landslide_gdf_proj = landslide_gdf.to_crs("EPSG:5070")

# Initialize buffer distances (in meters)
buffer_distances = [50, 100]

# Prepare new columns for buffer results (initialize with NaN)
for dist in buffer_distances:
    accidents_gdf_proj[str(dist)] = np.nan

# Iterate through each accident point
for idx, accident in accidents_gdf_proj.iterrows():
    for dist in buffer_distances:
        buffer_geom = accident.geometry.buffer(dist)
        # Check how many landslides fall within the buffer
        within_buffer = landslide_gdf_proj[landslide_gdf_proj.intersects(buffer_geom)]
        if not within_buffer.empty:
            accidents_gdf_proj.at[idx, str(dist)] = len(within_buffer)

# Reproject accidents back to EPSG:4326
accidents_gdf_final = accidents_gdf_proj.to_crs("EPSG:4326")

# Save the result to CSV
output_csv = (
    r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose"
    r"\2025\New_Journal\Verification\Landslide\Accidents_Verified_With_Landslides.csv"
)
accidents_gdf_final.to_csv(output_csv, index=False)

# Print total matches for each buffer distance
for dist in buffer_distances:
    total_matches = accidents_gdf_final[str(dist)].notna().sum()
    print(f"Total accidents with at least one landslide match within {dist} meters: {total_matches}")

print("Verification completed successfully!")

