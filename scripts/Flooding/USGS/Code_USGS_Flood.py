#%%
# ! ---------------------------------------------------------------
# ! 1_Importing the necessary libraries (1.2 seconds)
# ! ---------------------------------------------------------------
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

# %%
# ! ---------------------------------------------------------------
# ! 2_Importing the HUC12 shapefile (40s)
# ! ---------------------------------------------------------------
# Move two levels up to reach "1_Rail_Project"
base_dir = os.path.abspath(os.path.join("..", "..", "..", "..", ".."))

# Define the correct path for the HUC12 shapefile
Huc_path = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                        "WBD_HUC12.shp")

# Read the shapefile into a GeoDataFrame
HUC12 = gpd.read_file(Huc_path)
print("Done1!")

# Provide the code to update the geopandas version if needed

#%% 
# Paths to your Flood_USGS CSV file 
Flood_USGS_path = os.path.join(base_dir, "3_Flooding", "FloodEventUSGS", "FloodEventUSGS",
                        "Unique_Events", "2000-2024", "Merged_Events_2000_2024.csv")
# Read the CSV file into a DataFrame
Flood_USGS = pd.read_csv(Flood_USGS_path)

# Filter out rows without coordinates
Flood_USGS = Flood_USGS.dropna(subset=['longitude', 'latitude'])

# Convert the DataFrame to a GeoDataFrame
geometry = [Point(xy) for xy in zip(Flood_USGS['longitude'], Flood_USGS['latitude'])]
Flood_USGS_gdf = gpd.GeoDataFrame(Flood_USGS, geometry=geometry)

# Ensure both GeoDataFrames use the same coordinate reference system (CRS)
Flood_USGS_gdf = Flood_USGS_gdf.set_crs(HUC12.crs, allow_override=True)

# Perform a spatial join to retain all attributes
point_in_poly = gpd.sjoin(Flood_USGS_gdf, HUC12, how='left', predicate='within')

# Drop rows with missing join or missing/empty event_id
point_in_poly = point_in_poly.dropna(subset=['index_right', 'event_id'])
point_in_poly = point_in_poly[point_in_poly['event_id'] != ""]

# Drop duplicates per polygon per event
point_in_poly = point_in_poly.drop_duplicates(subset=['index_right', 'event_id'])

# Group unique event IDs by polygon
event_ids_by_polygon = point_in_poly.groupby('index_right')['event_id'].apply(lambda x: ','.join(sorted(set(map(str, x)))))

# Count the number of unique events per polygon
Flood_fre = point_in_poly.groupby('index_right').size()

# Assign to HUC12
HUC12 = HUC12.reset_index(drop=True)
HUC12['Event_ID'] = HUC12.index.map(event_ids_by_polygon).fillna('')
HUC12['Flood_fre'] = HUC12.index.map(Flood_fre).fillna(0).astype(int)

# Save final output
output_path = os.path.join(base_dir, "3_Flooding", "FloodEventUSGS", "FloodEventUSGS",
                        "Unique_Events", "2000-2024", "Merged_HUC12_with_USGS_unique_eventid_Flood.shp")

HUC12.to_file(output_path)

print("Shapefile with unique event IDs and Flood_fre saved successfully at:", output_path)


# %%
# Load the polyline and polygon shapefiles
Rail_line_path = os.path.join(base_dir, "Shapefiles", "North_American_Rail_Network_Lines",
                        "North_American_Rail_Network_Lines.shp")
Rail_line = gpd.read_file(Rail_line_path)

huc_path = os.path.join(base_dir, "3_Flooding", "FloodEventUSGS", "FloodEventUSGS",
                        "Unique_Events", "2000-2024", "Merged_HUC12_with_USGS_unique_eventid_Flood.shp")
HUC12 = gpd.read_file(huc_path)

# Ensure that both GeoDataFrames are using the same coordinate reference system
if Rail_line.crs != HUC12.crs:
    Rail_line = Rail_line.to_crs(HUC12.crs)

# Perform the intersection
intersection_flood = gpd.overlay(Rail_line, HUC12, how='intersection')

# Reproject to a projection suitable for measuring distances in the USA (e.g., Albers Equal Area)
albers_crs = "EPSG:5070"  # Albers Equal Area for the contiguous United States
intersection_flood_albers = intersection_flood.to_crs(albers_crs)

# Calculate the length of each line in meters
intersection_flood_albers['Length_Meters'] = intersection_flood_albers.geometry.length

# Convert the length from meters to feet (1 meter = 3.28084 feet)
intersection_flood_albers['Length_Feet'] = intersection_flood_albers['Length_Meters'] * 3.28084

# Convert the length from meters to miles (1 meter = 0.000621371 miles)
intersection_flood_albers['Length_Miles'] = intersection_flood_albers['Length_Meters'] * 0.000621371

# Ensure all columns are compatible with shapefile format
# Convert any lists to strings, if needed
for col in intersection_flood_albers.columns:
    if intersection_flood_albers[col].apply(lambda x: isinstance(x, list)).any():
        intersection_flood_albers[col] = intersection_flood_albers[col].apply(lambda x: ','.join(map(str, x)) if isinstance(x, list) else x)

# Save the result back to a new shapefile
intersection_flood_albers.to_file(r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\3_Flooding"
                         r"\FloodEventUSGS\FloodEventUSGS\Unique_Events\2000-2024\New_Intersected_Railway_with_USGS_flood_freq.shp")

# Save the result to a CSV file
output_csv = (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
              r"\3_Flooding\FloodEventUSGS\FloodEventUSGS\Unique_Events\2000-2024\New_Intersected_Railway_with_USGS_flood_freq.csv")
intersection_flood_albers.to_csv(output_csv, index=False)

print("Done3!")

# %% 
# TODO Plotting_Pichart
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Path to your CSV file
csv_path = (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
            r"\3_Flooding\FloodEventUSGS\FloodEventUSGS\Unique_Events\2000-2024\New_Intersected_Railway_with_USGS_flood_freq.csv")


# Read the CSV file into a DataFrame
df = pd.read_csv(csv_path)

df['event_fl_id'] = df['event_fl_id'].fillna(0)

# Step 1: Categorize the event_fl_id values into two groups: zero and greater than zero
df['Flood_Category'] = np.where(df['event_fl_id'] == 0, 'No Flood', 'At Least One Flood')

# Step 2: Accumulate the Length_Mile column for each category
lengths_per_flood_freq = df.groupby('Flood_Category')['Length_Miles'].sum()

# Step 3: Calculate the total length
total_length = lengths_per_flood_freq.sum()

# Step 4: Plot the pie chart
labels = lengths_per_flood_freq.index
sizes = lengths_per_flood_freq.values
colors = ['lightblue', 'lightcoral']
explode = (0.1, 0)  # explode the 'Zero' slice slightly

plt.figure(figsize=(5, 5))
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
# plt.title('Length of Railway Lines by Flood Frequency')

# Add total length text to the top right
# plt.text(1.1, 1.1, f'Total Length: {total_length:.0f} Miles', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()

print("Done4!")

# %%
