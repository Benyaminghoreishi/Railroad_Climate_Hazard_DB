# %%
# # TODO: Flash Flash Flood (NCEI) Data Analysis
# ! ---------------------------------------------------------------
# ! 1_Importing the necessary libraries (1.2 seconds)
# ! ---------------------------------------------------------------
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import matplotlib.pyplot as plt
import numpy as np

# %%
# ! ---------------------------------------------------------------
# ! 2_Importing the HUC12 shapefile (40s)
# ! ---------------------------------------------------------------
# Move two levels up to reach "1_Rail_Project"
base_dir = os.path.abspath(os.path.join("..", ".."))

# Define the correct path for the HUC12 shapefile
Huc_path = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                        "WBD_HUC12.shp")

# Debugging: Print the constructed path
print("Checking Path:", Huc_path)

# Read the shapefile into a GeoDataFrame
HUC12 = gpd.read_file(Huc_path)

# # changing the crs to EPSG:20163
# HUC12 = HUC12.to_crs(epsg=2163)
HUC12.crs
# HUC12.head()
# HUC12.plot()
print("Done1!")

#%% 
# ! ---------------------------------------------------------------
# ! 3_Importing the FlashFlood_NCEI CSV file (0.8 seconds)
# ! ---------------------------------------------------------------

# Define the relative path to the Flash Flood CSV file
FlashFlood_NCEI_path = os.path.join(base_dir, "3_Flooding", "NCEI", "Event_Type", 
                                    "Flash Flood.csv")
# Read the CSV file into a DataFrame
FlashFlood_NCEI = pd.read_csv(FlashFlood_NCEI_path)
# %%
# ! ------------------------------------------------------------------------------------------------------------------------------
# ! 4_Spatial Join and Finding the Frequency of Flash Flood Events in each HUC12 Unit and Assigning the Event_IDs (18m 50s)
# ! ------------------------------------------------------------------------------------------------------------------------------
# Print original number of records
print(f"Original records: {len(FlashFlood_NCEI)}")

# Drop rows with missing latitude or longitude
FlashFlood_NCEI = FlashFlood_NCEI.dropna(subset=['BEGIN_LAT', 'BEGIN_LON'])

# Drop rows with zero latitude or longitude
FlashFlood_NCEI = FlashFlood_NCEI[
    (FlashFlood_NCEI['BEGIN_LAT'] != 0) & 
    (FlashFlood_NCEI['BEGIN_LON'] != 0)
]

# Print number of valid records after filtering
print(f"Records after removing NaN and zero coordinates: {len(FlashFlood_NCEI)}")

# Fix CRS (assuming NCEI points are in WGS84)
FlashFlood_NCEI_gdf = gpd.GeoDataFrame(
    FlashFlood_NCEI, 
    geometry=[Point(xy) for xy in zip(FlashFlood_NCEI['BEGIN_LON'], FlashFlood_NCEI['BEGIN_LAT'])],
    crs="EPSG:4269"
)

# Define the output path for saving the FlashFlood_NCEI with valid coordinates
output_shapefile_path = os.path.join(
    (
        "C:\\Users\\ghoreisb\\Box\\Oregon State University\\000- Papers\\Publish Purpose\\2025\\New_Journal\\"
        "Railroad_Hazard_Database\\data\\processed\\flood_assignment\\NCEI\\Flash_FLood\\shapefiles"
    ),
    "FlashFlood_NCEI_Valid_Coordinates.shp"
)

# Save the GeoDataFrame with valid coordinates to a shapefile
FlashFlood_NCEI_gdf.to_file(output_shapefile_path)

print("FlashFlood_NCEI with valid coordinates saved to:", output_shapefile_path)

FlashFlood_NCEI_gdf = FlashFlood_NCEI_gdf.to_crs(HUC12.crs)

# Ensure valid geometries
HUC12['geometry'] = HUC12['geometry'].buffer(0)

# Spatial join
point_in_poly = gpd.sjoin(FlashFlood_NCEI_gdf, HUC12, how='left', predicate='within')

# Drop rows with missing join or missing/empty EPISODE_ID
point_in_poly = point_in_poly.dropna(subset=['index_right', 'EPISODE_ID'])
point_in_poly = point_in_poly[point_in_poly['EPISODE_ID'] != ""]

# Drop duplicates per polygon per episode
point_in_poly = point_in_poly.drop_duplicates(subset=['index_right', 'EPISODE_ID'])

# ✅ Print the number of records after duplicate removal
print(f"Records after removing the duplicate episode IDs from the same HUC: {len(point_in_poly)}")

# Map EVENT_ID and EPISODE_ID per polygon
event_ids = point_in_poly.groupby('index_right')['EVENT_ID'].apply(lambda x: ','.join(x.dropna().astype(str)))
episode_ids = point_in_poly.groupby('index_right')['EPISODE_ID'].apply(lambda x: ','.join(x.dropna().astype(str)))

# Frequency of unique episodes per polygon
flash_fre = point_in_poly.groupby('index_right').size()

# ✅ Save validated flash flood records to shapefile
validated_output_path = os.path.join(base_dir, "3_Flooding", "NCEI", "NCEI_FlashFlood_Shapefile", 
                                     "NCEI_FlashFlood_Shapefile_Unique_Ep_ID.shp")
point_in_poly.to_file(validated_output_path)

print("Validated Flash Flood shapefile saved to:", validated_output_path)

# Reset index of HUC12 to match index_right
HUC12 = HUC12.reset_index(drop=True)

# Reset index of HUC12 to match index_right
HUC12 = HUC12.reset_index(drop=True)

# Assign to HUC12
HUC12['Event_ID'] = HUC12.index.map(event_ids).fillna('')
HUC12['Episode_ID'] = HUC12.index.map(episode_ids).fillna('')
HUC12['Flash_Fre'] = HUC12.index.map(flash_fre).fillna(0)

# Save updated shapefile
output_path = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                           "Merged_HUC12_with_unique_episodeid.shp")
HUC12.to_file(output_path)

print("Shapefile with unique EPISODE_IDs saved successfully at:", output_path)

# %%
############################################################################################################
# ! 5_Creating a New Shapefile with Flash Flood Frequency and Event IDs and Saving it as a CSV file as well 
############################################################################################################

import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
from pyproj import Geod
import os

# Move two levels up to reach "1_Rail_Project"
base_dir = os.path.abspath(os.path.join("..", ".."))

# Define file paths
rail_line_path = os.path.join(base_dir, "Shapefiles", "North_American_Rail_Network_Lines", 
                              "North_American_Rail_Network_Lines.shp")
huc12_path = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                          "Merged_HUC12_with_unique_episodeid.shp")

# Load files
rail_line = gpd.read_file(rail_line_path)
HUC12 = gpd.read_file(huc12_path)

# Reproject both layers to EPSG:4269 (NAD83 Geographic CRS)
# ⚠️ NOTE: EPSG:4269 is in degrees. Geometry length must be calculated using geodesic methods (see below)
rail_line = rail_line.to_crs(epsg=4269)
HUC12 = HUC12.to_crs(epsg=4269)

# Perform spatial overlay (split rail lines at HUC12 boundaries)
split_with_huc = gpd.overlay(rail_line, HUC12, how='intersection')

# ---------------------------------------------------------------------------------
# 📏 Accurate Length Calculation in EPSG:4269 Using Geodesic Method
# ---------------------------------------------------------------------------------
# In geographic CRS, .length returns degrees, not meters.
# Instead, we use pyproj.Geod to compute geodesic (real-world) distances.

# Define the ellipsoid based on NAD83 (used in EPSG:4269)
geod = Geod(ellps="GRS80")

def geodesic_length_miles(geom):
    """
    Calculate geodesic length in miles for LineString or MultiLineString geometry.
    
    Equations:
        - L_meters = geod.line_length(lon_coords, lat_coords)
        - L_miles = L_meters * 0.000621371
    """
    if geom.is_empty:
        return 0
    if geom.geom_type == 'LineString':
        length_meters = geod.line_length(geom.xy[0], geom.xy[1])
    elif geom.geom_type == 'MultiLineString':
        length_meters = sum(geod.line_length(line.xy[0], line.xy[1]) for line in geom.geoms)
    else:
        return 0
    return length_meters * 0.000621371

# Apply geodesic length calculation
split_with_huc["Length_Miles"] = split_with_huc.geometry.apply(geodesic_length_miles)
split_with_huc["Length_Meters"] = split_with_huc["Length_Miles"] / 0.000621371
split_with_huc["Length_Feet"] = split_with_huc["Length_Meters"] * 3.28084

# ---------------------------------------------------------------------------------
# 💧 Flash Flood Attribute Assignment
# ---------------------------------------------------------------------------------
# Clean and fill attributes related to flash flood frequency
split_with_huc["Event_ID"] = split_with_huc.get("Event_ID", "").fillna("")
split_with_huc["Episode_ID"] = split_with_huc.get("Episode_ID", "").fillna("")
split_with_huc["Flash_Fre"] = split_with_huc.get("Flash_Fre", 0).fillna(0).astype(int)

# ---------------------------------------------------------------------------------
# 💾 Save the Output as Shapefile and CSV
# ---------------------------------------------------------------------------------

# Define output paths
output_shapefile = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                                "Rail_Segments_SplitThenOverlayed_with_flashflood_Freq.shp")
output_csv = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                          "Rail_Segments_SplitThenOverlayed_with_flashflood_Freq.csv")

# Optional: ensure output directory exists
# os.makedirs(os.path.dirname(output_shapefile), exist_ok=True)

# Save to file
split_with_huc.to_file(output_shapefile)
split_with_huc.to_csv(output_csv, index=False)

# ✅ Status Output
print("✅ Rail segments split and attributed successfully!")
print("📍 Shapefile saved at:", output_shapefile)
print("📄 CSV file saved at:", output_csv)


# %% 
############################################################################################################
# ! 6_Plotting the Flash Flood Frequency and Length of Railway Lines by Flash Flood Frequency Events
############################################################################################################
# TODO Plotting_Pichart

# Define the relative path for the CSV file using base_dir
shp_path = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                        "Rail_Segments_SplitThenOverlayed_with_flashflood_Freq.shp")

# Read the CSV file into a DataFrame
df = gpd.read_file(shp_path)

# Step 1: Categorize the Flash_Fre values into two groups: zero and greater than zero
df['Flash_Flood_Category'] = np.where(df['Flash_Fre'] == 0, 'No Flood', 'At Least One Flood')
# df["Flood_Category"].describe()

# Step 2: Accumulate the Length_Mile column for each category
lengths_per_Flash_Freq = df.groupby('Flash_Flood_Category')['Length_Mil'].sum()

# Step 3: Calculate the total length
total_length = lengths_per_Flash_Freq.sum()

# Step 4: Plot the pie chart
labels = lengths_per_Flash_Freq.index
sizes = lengths_per_Flash_Freq.values
colors = ['lightblue', 'lightcoral']
explode = (0.1, 0)  # explode the 'Zero' slice slightly

plt.figure(figsize=(5, 5))
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
# plt.title('Length of Railway Lines by Flash Flood Frequency')

# Add total length text to the top right
# plt.text(1.1, 1.1, f'Total Length: {total_length:.0f} Miles', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()

print("Done4!")

# %% # TODO Plotting_Barchart1
############################################################################################################
# ! 7_Plotting the Sum of Railway Length by Flash Flood Frequency Events
############################################################################################################
# Define the bins and labels
bins = [-10, 1, 10, 20, 30, 40, 50, 60, 70, 80]
labels = ['0', '0 - 10', '10 - 20', '20 - 30', '30 - 40', '40 - 50', '50 - 60', '60 - 70', '70 - 76']

# Categorize the Flash_Fre into bins
df['Flash_Flood_Bins'] = pd.cut(df['Flash_Fre'], bins=bins, labels=labels, right=False)

# Group by Flood_Bins and sum the Length_Miles for each group
grouped_data = df.groupby('Flash_Flood_Bins')['Length_Mil'].sum().reset_index()

# Calculate the total length for percentage calculation
total_length = grouped_data['Length_Mil'].sum()

# Plotting the bar chart
plt.figure(figsize=(12, 8))
bars = plt.bar(grouped_data['Flash_Flood_Bins'], grouped_data['Length_Mil'], color='blue', edgecolor='black')
plt.xlabel('Flash Flood Frequency')
plt.ylabel('Sum of Length in Miles')
plt.title('Sum of Railway Length by Flash Flood Frequency Events')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.2)

# Increase the frame from the top by 10%
plt.ylim(0, grouped_data['Length_Mil'].max() * 1.075)

# Add frequency and percentage above each bar
for bar in bars:
    height = bar.get_height()
    percentage = (height / total_length) * 100
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}\n({percentage:.1f}%)', ha='center', va='bottom')

plt.show()

# Unique number in the Flash_Fre column and sort them
print("Sorted Unique Flash Flood Frequencies:", np.sort(df['Flash_Fre'].unique()))

print("Done5!")
# %% # TODO Plotting_Barchart2
############################################################################################################
# ! 8_Plotting the Sum of Railway Length by Flash Flood Frequency Events Between 1 to 10 Events
############################################################################################################
# Define the bins and labels
bins = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

# Categorize the Flash_Fre into bins
df['Flash_Flood_Bins'] = pd.cut(df['Flash_Fre'], bins=bins, labels=labels, right=False)

# Group by Flash_Flood_Bins and sum the Length_Miles for each group
grouped_data = df.groupby('Flash_Flood_Bins')['Length_Mil'].sum().reset_index()

# Calculate the total length for percentage calculation
total_length = grouped_data['Length_Mil'].sum()

# Plotting the bar chart
plt.figure(figsize=(12, 8))
bars = plt.bar(grouped_data['Flash_Flood_Bins'], grouped_data['Length_Mil'], color='blue', edgecolor='black')
plt.xlabel('Flash Flood Frequency')
plt.ylabel('Sum of Length in Miles')
plt.title('Sum of Railway Length by Flash Flood Frequency Between 1 to 10 Events')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.2)

# Increase the frame from the top by 10%
plt.ylim(0, grouped_data['Length_Mil'].max() * 1.075)

# Add frequency and percentage above each bar
for bar in bars:
    height = bar.get_height()
    percentage = (height / total_length) * 100
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}\n({percentage:.1f}%)', ha='center', va='bottom')

plt.show()

print("Done6!")



# %%
