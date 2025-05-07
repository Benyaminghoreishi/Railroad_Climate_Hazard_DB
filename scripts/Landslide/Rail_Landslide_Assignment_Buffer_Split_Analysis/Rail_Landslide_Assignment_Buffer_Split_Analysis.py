#%%
#! ################################################################################################
#! # Title: Import Required Libraries for Landslide Analysis
#! Purpose: Load essential Python libraries for geospatial and data visualization tasks
#! Run Time: [<5 seconds]
#! ################################################################################################

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import matplotlib.pyplot as plt
#%%
#! ################################################################################################
#! # Title: Create a Buffer Around U.S. Rail Lines
#! Purpose: Generate 100m buffers for landslide analysis
#! Run Time: [~5 minutes]
#! ################################################################################################
# Read the shapefile into a GeoDataFrame
rail_line_path = (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
    r"\Shapefiles\North_American_Rail_Network_Lines\North_American_Rail_Network_Lines.shp")
rail_line_gdf = gpd.read_file(rail_line_path)

# Buffer distances
distances = [100]

# Define buffer parameters to control shape aesthetics
buffer_kwargs = {
    'cap_style': 2,      # Cap style defines the shape of line ends in buffers.
                         # 2 = flat ends (good for roads, rail lines, etc.)
                         # (1 = round, 3 = square)

    'join_style': 2,     # Join style controls the appearance of corners where lines meet.
                         # 2 = miter (sharp corners, angular)
                         # (1 = round, 3 = bevel/flattened corners)

    'mitre_limit': 3     # Mitre limit restricts the length of pointed corners when join_style is miter.
                         # Lower values reduce sharp, spiky corners on narrow angles.
}

# Create buffers and save them as new shapefiles
for distance in distances:
    buffered_geom = rail_line_gdf.buffer(distance, **buffer_kwargs)
    buffered_gdf = gpd.GeoDataFrame(rail_line_gdf.copy(), geometry=buffered_geom, crs=rail_line_gdf.crs)
    
    output_path = os.path.join(
        "C:\\Users\\ghoreisb\\Box\\Oregon State University",
        "0000- Research_OSU\\1_Rail_Project\\7_Landslide",
        f"Code_Assigning_to_Railway\\Rail_line_buffer_{distance}m.shp"
    )
    
    buffered_gdf.to_file(output_path)
    print(f"Buffer of {distance} meters saved to {output_path}")

print("Done1 with buffering!")

#%% 
#! ################################################################################################
#! # Title: Assign Landslide Points to Railroad Buffer and Save Results to GeoPackage
#! Purpose: Spatially join filtered landslide points with 100-meter rail buffer zones,
#!          summarize counts and IDs, save buffer output and filtered points as GeoPackages.
#! Run Time: [~10 sec]
#! ################################################################################################

import geopandas as gpd

# Load railway buffer shapefile
gdf_list = {
    '100m': gpd.read_file(
        r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\\"
        r"1_Rail_Project\7_Landslide\Code_Assigning_to_Railway\\"
        r"Rail_line_buffer_100m.shp"
    )
}

# Load filtered landslide point GeoPackage
Landslide_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\\"
    r"1_Rail_Project\7_Landslide\Data\Ver.3.0.Feb2025\US_Landslide_v3_csv\\"
    r"us_ls_v3_point_with_dates_2000_2024.gpkg"
)
LandslidePoint_gdf = gpd.read_file(Landslide_path)

# Spatial join process
for key, gdf in gdf_list.items():
    # Ensure CRS alignment
    LandslidePoint_gdf = LandslidePoint_gdf.set_crs(LandslidePoint_gdf.crs, allow_override=True)
    LandslidePoint_gdf_reprojected = LandslidePoint_gdf.to_crs(gdf.crs)

    # Perform spatial join (within 100m buffer)
    point_in_poly = gpd.sjoin(LandslidePoint_gdf_reprojected, gdf, how='left', predicate='within')

    # Use 'USGS_ID' as the unique identifier for landslide points
    slide_id_col = 'USGS_ID'

    # Group by index of buffer polygons and aggregate
    polygon_event_ids = point_in_poly.groupby('index_right')[slide_id_col].apply(lambda x: ','.join(x.astype(str)))
    Num_Landslide = point_in_poly.groupby('index_right').size()

    # Assign aggregated data back to buffer GeoDataFrame
    gdf['Landslide_IDs'] = gdf.index.map(polygon_event_ids).fillna('')
    gdf['Num_Landslide'] = gdf.index.map(Num_Landslide).fillna(0).astype(int)

    # Save buffer with landslide attributes
    output_buffer_gpkg = (
        "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
        "1_Rail_Project\\7_Landslide\\Code_Assigning_to_Railway\\"
        f"Rail_{key}_Buffer_with_Slide_ObjectID.gpkg"
    )
    gdf.to_file(output_buffer_gpkg, layer='rail_landslide_join', driver='GPKG')
    print(f"✅ Buffer GeoPackage saved successfully for {key} buffer!")

    # Filter landslide points within buffer (index_right not null)
    landslide_within_buffer = point_in_poly[point_in_poly['index_right'].notnull()].copy()

    # Save filtered landslide points to GeoPackage
    output_points_gpkg = (
        "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
        "1_Rail_Project\\7_Landslide\\Code_Assigning_to_Railway\\"
        f"Landslide_Points_within_{key}_Buffer.gpkg"
    )
    landslide_within_buffer.to_file(output_points_gpkg, layer='landslide_points_buffer', driver='GPKG')
    print(f"✅ Landslide points within {key} buffer saved successfully!")

#%%
#! ################################################################################################
#! # Title: Plot Landslide Points (within Buffer) by Year (2000–2023) with Turbo Colormap by Year
#! Purpose: Create a bar chart of landslide events per year using Turbo colormap for the years.
#! Run Time: [~5 sec]
#! ################################################################################################

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load filtered landslide points within buffer
landslide_buffer_path = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Code_Assigning_to_Railway\\"
    "Landslide_Points_within_100m_Buffer.gpkg"
)
gdf_points = gpd.read_file(landslide_buffer_path)

# Convert Date_Min to datetime if not already
gdf_points['Date_Min'] = pd.to_datetime(gdf_points['Date_Min'], errors='coerce')

# Extract Year and filter for 2000–2023
gdf_points['Year'] = gdf_points['Date_Min'].dt.year
gdf_filtered = gdf_points[(gdf_points['Year'] >= 2000) & (gdf_points['Year'] <= 2023)]

# Count number of landslides per year
year_counts = gdf_filtered['Year'].value_counts().sort_index()

# Prepare Turbo colormap
cmap = plt.cm.turbo
norm = plt.Normalize(2000, 2023)  # Normalize between 2000 and 2023
colors = [cmap(norm(year)) for year in year_counts.index]

# Plot
plt.figure(figsize=(10, 5))
bars = plt.bar(year_counts.index, year_counts.values, color=colors)

# Labels
plt.xlabel('Year', fontsize=14)
plt.ylabel('Number of Landslides', fontsize=14)
plt.title('Landslide Points within 100m Buffer (2000–2023)', fontsize=16)
plt.xticks(np.arange(2000, 2024, 2), fontsize=12)
plt.yticks(fontsize=12)

# Add counts on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 1, f'{int(height)}', 
             ha='center', va='bottom', fontsize=10)

plt.tight_layout()

# Save the figure at 400 DPI
output_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\\"
    r"1_Rail_Project\7_Landslide\Landsllide_DataPaper\\"
    r"Landslide_Points_2000_2023_Turbo.png"
)
plt.savefig(output_path, dpi=400)
plt.close()

plt.show()

#%%
#! ################################################################################################
#! # Title: Reassign Landslide Attributes to Original Rail Lines (Reverse Buffer Join)
#! Purpose: Restore original rail polylines and attach landslide counts and IDs via spatial join
#! Run Time: [~10 sec]
#! ################################################################################################

import geopandas as gpd

# Load original rail lines
rail_lines_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU"
    r"\1_Rail_Project\Shapefiles\North_American_Rail_Network_Lines\North_American_Rail_Network_Lines.shp"
)
rail_lines_gdf = gpd.read_file(rail_lines_path)

# Load buffered rail segments with landslide attributes
buffer_with_landslide_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU"
    r"\1_Rail_Project\7_Landslide\Code_Assigning_to_Railway"
    r"\Rail_100m_Buffer_with_Slide_ObjectID.gpkg"
)
buffer_gdf = gpd.read_file(buffer_with_landslide_path)

# Ensure CRS match (for safety)
rail_lines_gdf = rail_lines_gdf.to_crs(buffer_gdf.crs)

# Join by OBJECTID (or other shared ID field)
if 'OBJECTID' not in buffer_gdf.columns:
    raise ValueError("Buffer GeoDataFrame must include 'OBJECTID' for attribute matching.")

# Merge on OBJECTID
rail_lines_gdf = rail_lines_gdf.merge(
    buffer_gdf[['OBJECTID', 'Num_Landslide', 'Landslide_IDs']],
    on='OBJECTID',
    how='left'
)

# Fill NA values with defaults
rail_lines_gdf['Num_Landslide'] = rail_lines_gdf['Num_Landslide'].fillna(0).astype(int)
rail_lines_gdf['Landslide_IDs'] = rail_lines_gdf['Landslide_IDs'].fillna('')

# Save output as GeoPackage
output_gpkg = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\\"
    r"1_Rail_Project\7_Landslide\Code_Assigning_to_Railway\\"
    r"Rail_lines_with_Landslide_Attributes.gpkg"
)
rail_lines_gdf.to_file(output_gpkg, layer='rail_lines_landslide', driver='GPKG')

print("✅ Rail lines with landslide attributes saved successfully based on OBJECTID join.")

#%%
#! ################################################################################################
#! # Title: Plot Pie Chart of Rail Line Lengths by Landslide Frequency (GeoPackage)
#! Purpose: Categorize rail lines into segments with and without landslides, sum lengths, and plot.
#! Run Time: [~5 sec]
#! ################################################################################################


# Load the GeoPackage
geo_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\\"
    r"1_Rail_Project\7_Landslide\Code_Assigning_to_Railway\\"
    r"Rail_lines_with_Landslide_Attributes.gpkg"
)
gdf = gpd.read_file(geo_path)

# Step 1: Categorize Num_Landslide into two groups: zero and greater than zero
gdf['Landslide_Category'] = np.where(gdf['Num_Landslide'] == 0, 'No Landslide', 'At Least One Landslide')

# Step 2: Sum ShapeSTLen for each category
lengths_per_category = gdf.groupby('Landslide_Category')['ShapeSTLen'].sum()

# Step 3: Calculate total length
total_length = lengths_per_category.sum()

# Step 4: Plot the pie chart
labels = lengths_per_category.index
sizes = lengths_per_category.values
colors = ['lightgreen', 'orange']
explode = (0.1, 0)  # Explode 'No Landslide' slightly

plt.figure(figsize=(6, 6))
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)

# Add total length text (top right)
plt.text(1.1, 1.1, f'Total Length: {total_length:.0f} Miles', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

plt.axis('equal')  # Equal aspect ratio ensures a circular pie chart
plt.show()

print("Done plotting pie chart!")

#%% 
#! ################################################################################################
#! # Title: Assign Landslide Polygons to Railroad Lines (Split and Attribute Join)
#! Purpose: Split railroad lines at landslide polygon intersections, retain all rail segments
#!          and railroad attributes, and join landslide attributes (USGS_ID, Year_Min, etc.)
#! Run Time: [~20-30 sec depending on data size]
#! ################################################################################################

import geopandas as gpd
from shapely.geometry import LineString, MultiLineString

# Load rail lines
rail_lines_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU"
    r"\1_Rail_Project\Shapefiles\North_American_Rail_Network_Lines\North_American_Rail_Network_Lines.shp"
)
rail_gdf = gpd.read_file(rail_lines_path)

# Load landslide polygons
landslide_poly_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU"
    r"\1_Rail_Project\7_Landslide\Data\Ver.3.0.Feb2025\US_Landslide_v3_csv"
    r"\us_ls_v3_poly_with_dates_2000_2024.gpkg"
)
landslide_gdf = gpd.read_file(landslide_poly_path)

# Ensure same CRS
rail_gdf = rail_gdf.to_crs(landslide_gdf.crs)

# Initialize list for split segments and their attributes
split_segments = []

for idx, rail in rail_gdf.iterrows():
    intersecting_polygons = landslide_gdf[landslide_gdf.intersects(rail.geometry)]
    num_landslide = len(intersecting_polygons)

    if num_landslide == 0:
        # No intersection, keep original rail segment with its attributes
        rail_attrs = rail.to_dict()
        rail_attrs.update({'Num_Landslide': 0, 'USGS_ID': None, 'Year_Min': None, 'Month_Min': None, 'Day_Min': None})
        split_segments.append(rail_attrs)
    else:
        # Split rail segment by intersecting polygons
        for _, slide in intersecting_polygons.iterrows():
            intersection = rail.geometry.intersection(slide.geometry)
            if intersection.is_empty:
                continue
            if isinstance(intersection, LineString):
                segments = [intersection]
            elif isinstance(intersection, MultiLineString):
                segments = list(intersection.geoms)
            else:
                continue

            for seg in segments:
                rail_attrs = rail.to_dict()
                rail_attrs.update({
                    'geometry': seg,
                    'Num_Landslide': 1,
                    'USGS_ID': slide['USGS_ID'],
                    'Year_Min': slide['Year_Min'],
                    'Month_Min': slide['Month_Min'],
                    'Day_Min': slide['Day_Min']
                })
                split_segments.append(rail_attrs)

# Convert to GeoDataFrame
split_gdf = gpd.GeoDataFrame(split_segments, crs=rail_gdf.crs)

# Save as GeoPackage
output_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU"
    r"\1_Rail_Project\7_Landslide\Code_Assigning_to_Railway"
    r"\Rail_lines_split_with_Landslide_Attributes.gpkg"
)
split_gdf.to_file(output_path, layer='rail_lines_landslide_split', driver='GPKG')

print("Rail lines with landslide attributes saved successfully!")

# %%
