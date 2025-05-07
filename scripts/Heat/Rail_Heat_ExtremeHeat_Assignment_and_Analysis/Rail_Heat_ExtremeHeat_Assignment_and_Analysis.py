#%%
# TODO: Assigning the NCEI Heat Events to the US Railway Network  
########################################
# ! 1_Importing the necessary libraries
########################################
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import matplotlib.pyplot as plt
import numpy as np

# %%
# =================================================================================
# ! Generating the NWS Forecast Zone with Unique Heat Events and Frequency Counts
# =================================================================================

# Set base directory
base_dir = os.path.abspath(os.path.join("..", "..", ".."))

# File paths
nws_shapefile_path = os.path.join(base_dir, "5_Sunkink", "NWS Forecast Zone", "NWS_Forcat_Zone", "z_18mr25.shp")
heat_csv_path = os.path.join(base_dir, "5_Sunkink", "NWS Forecast Zone", "Heat_with_coords.csv")
exc_heat_csv_path = os.path.join(base_dir, "5_Sunkink", "NWS Forecast Zone", "Excessive Heat", "Excessive_heat_with_coords.csv")


# Load data
NWS = gpd.read_file(nws_shapefile_path)
Heat_NCEI = pd.read_csv(heat_csv_path)
Exc_Heat_NCEI = pd.read_csv(exc_heat_csv_path)

# combineing the two heat and excessive heat dataframes
Heat_NCEI = pd.concat([Heat_NCEI, Exc_Heat_NCEI], ignore_index=True)

# Filter out invalid coordinates
Heat_NCEI = Heat_NCEI.dropna(subset=['LON', 'LAT'])
Heat_NCEI = Heat_NCEI[(Heat_NCEI['LAT'] != 0) | (Heat_NCEI['LON'] != 0)]

# Convert to GeoDataFrame
geometry = [Point(xy) for xy in zip(Heat_NCEI['LON'], Heat_NCEI['LAT'])]
Heat_NCEI_gdf = gpd.GeoDataFrame(Heat_NCEI, geometry=geometry, crs="EPSG:4326")

# Save the heat points as shapefile
output_path = os.path.join(base_dir, "5_Sunkink", "Heat_EXtremeHeat_Combined", "Heat_EXtremeHeat_Combined.shp")
Heat_NCEI_gdf.to_file(output_path)

# Ensure matching CRS
NWS = NWS.to_crs(epsg=2163)
Heat_NCEI_gdf = Heat_NCEI_gdf.to_crs(epsg=2163)

# Spatial join
point_in_poly = gpd.sjoin(Heat_NCEI_gdf, NWS, how='left', predicate='within')

# Drop rows missing IDs
point_in_poly = point_in_poly.dropna(subset=['EVENT_ID', 'EPISODE_ID'])
point_in_poly = point_in_poly[(point_in_poly['EVENT_ID'] != "") & (point_in_poly['EPISODE_ID'] != "")]

# Convert IDs to consistent string format
point_in_poly['EVENT_ID'] = point_in_poly['EVENT_ID'].astype(str).str.strip()
point_in_poly['EPISODE_ID'] = point_in_poly['EPISODE_ID'].astype(str).str.strip()

# Drop duplicate EPISODE_IDs within the same zone
point_in_poly = point_in_poly.drop_duplicates(subset=['index_right', 'EPISODE_ID'])

# drop any remaining duplicate EVENT_IDs (in case of multiple events per episode)
point_in_poly = point_in_poly.drop_duplicates(subset=['index_right', 'EVENT_ID'])

# Frequency of unique episodes per polygon
flash_fre = point_in_poly.groupby('index_right').size()

# Group and count
grouped_event_ids = point_in_poly.groupby('index_right')['EVENT_ID'].apply(lambda x: ','.join(sorted(set(x))))
grouped_episode_ids = point_in_poly.groupby('index_right')['EPISODE_ID'].apply(lambda x: ','.join(sorted(set(x))))
Heat_Fre = point_in_poly.groupby('index_right').size()

NWS = NWS.reset_index(drop=True)

# Assign to NWS (do NOT reset index)
NWS['Event_ID'] = NWS.index.map(grouped_event_ids).fillna('')
NWS['Episode_ID'] = NWS.index.map(grouped_episode_ids).fillna('')
NWS['Heat_Fre'] = NWS.index.map(Heat_Fre).fillna(0)

# Save updated shapefile
output_path = os.path.join(base_dir, "5_Sunkink", "Heat_EXtremeHeat_Combined", "NWS_Forcat_Zone_with_Heat_Excessive_Heat_counts.shp")
NWS.to_file(output_path)

print("✅ Final shapefile with unique EVENT_IDs and EPISODE_IDs saved at:", output_path)

# %%
########################################################################################
# ! 2_Assigning the NCEI Heat Events to the US Railway Network and Saving the Results
########################################################################################

# Define the reLATive path to the Rail Line shapefile
rail_line = os.path.join(base_dir, "Shapefiles", "North_American_Rail_Network_Lines", 
                         "North_American_Rail_Network_Lines.shp")

# Load the file
rail_line = gpd.read_file(rail_line)

# Ensure that both GeoDataFrames are using the same coordinate reference system
if rail_line.crs != NWS.crs:
    rail_line = rail_line.to_crs(NWS.crs)

# Perform the intersection
intersection_Heat = gpd.overlay(rail_line, NWS, how='intersection')

# CalcuLATe the length of each line in meters
intersection_Heat['Length_Meters'] = intersection_Heat.geometry.length

# Convert the length from meters to feet (1 meter = 3.28084 feet)
intersection_Heat['Length_Feet'] = intersection_Heat['Length_Meters'] * 3.28084

# Convert the length from meters to miles (1 meter = 0.000621371 miles)
intersection_Heat['Length_Miles'] = intersection_Heat['Length_Meters'] * 0.000621371

# Define the reLATive path to the Rail Line shapefile
intersection_Heat_path = os.path.join(base_dir, "5_Sunkink", "Heat_EXtremeHeat_Combined", 
                                 "New_Intersected_Railway_with_Heat_ExtremeHeat_freq.shp")

# Save the result to a new shapefile
intersection_Heat.to_file(intersection_Heat_path)

# Define the reLATive path to the Rail Line shapefile
output_csv_path = os.path.join(base_dir, "5_Sunkink", "Heat_EXtremeHeat_Combined",  
                                 "New_Intersected_Railway_with_Heat_ExtremeHeat_freq.csv")

# Save the result to a CSV file
intersection_Heat.to_csv(output_csv_path, index=False)

print("Done3!")

# %% 
# ===============================================================
# ! 3_Plotting the Pie Chart
# ===============================================================
# TODO Plotting_Pichart
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Path to your CSV file
csv_path =  os.path.join(base_dir, "5_Sunkink", "Heat_EXtremeHeat_Combined",  
                                 "New_Intersected_Railway_with_Heat_ExtremeHeat_freq.csv")
 
# Read the CSV file into a DataFrame
df = pd.read_csv(csv_path)

# Step 1: Categorize the Heat_Fre values into two groups: zero and greater than zero
df['Heat_Category'] = np.where(df['Heat_Fre'] == 0, 'No Heat Event', 'At Least One Heat Event')

# Step 2: AccumuLATe the Length_Mile column for each category
lengths_per_Heat_freq = df.groupby('Heat_Category')['Length_Miles'].sum()

# Step 3: CalcuLATe the total length
total_length = lengths_per_Heat_freq.sum()

# Step 4: Plot the pie chart
labels = lengths_per_Heat_freq.index
sizes = lengths_per_Heat_freq.values
colors = ['lightblue', 'lightcoral']
explode = (0.1, 0)  # explode the 'Zero' slice slightly

plt.figure(figsize=(8, 8))
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
# plt.title('Length of Railway Lines by Heat Frequency')

# Add total length text to the top right
# plt.text(1.1, 1.1, f'Total Length: {total_length:.0f} Miles', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()

print("Done4!")

#%% 
# ===============================================================
# ! 3_Calculating the Weighted Mean of Heat Frequency
# ===============================================================
# Step 1: Calculate the arithmetic mean of (Length_Mil_i * Heat_Fre_i) / (Length_Mil_i)
weighted_mean_Heat_Fred = (df['Length_Miles'] * df['Heat_Fre']).sum() / df['Length_Miles'].sum()
print(f"Weighted Mean of Heat Frequency: {weighted_mean_Heat_Fred:.2f}")

# %% # TODO Plotting_Barchart1
########################################################################################
# ! 4_Plotting the Bar Chart
########################################################################################

# Define the bins and labels
bins = [-10, 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 190]
labels = ['0', '0 - 10', '10 - 20', '20 - 30', '30 - 40', '40 - 50', '50 - 60', '60 - 70', '70 - 80', '80 - 90', '90 - 100', '100 - 186']

# Categorize the Heat_Fre into bins
df['Heat_Bins'] = pd.cut(df['Heat_Fre'], bins=bins, labels=labels, right=False)

# Group by Heat_Bins and sum the Length_Miles for each group
grouped_data = df.groupby('Heat_Bins')['Length_Miles'].sum().reset_index()

# CalcuLATe the total length for percentage calcuLATion
total_length = grouped_data['Length_Miles'].sum()

# Plotting the bar chart
plt.figure(figsize=(12, 8))
bars = plt.bar(grouped_data['Heat_Bins'], grouped_data['Length_Miles'], color='blue', edgecolor='black')
plt.xlabel('Heat Frequency')
plt.ylabel('Sum of Length in Miles')
plt.title('Sum of Railway Length by Heat Frequency Events')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.2)

# Increase the frame from the top by 10%
plt.ylim(0, grouped_data['Length_Miles'].max() * 1.075)

# Add frequency and percentage above each bar
for bar in bars:
    height = bar.get_height()
    percentage = (height / total_length) * 100
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}\n({percentage:.1f}%)', ha='center', va='bottom')

plt.show()

print("Done5!")
# %% # TODO Plotting_Barchart2
########################################################################################
# ! 5_Plotting the Bar Chart
########################################################################################

# Define the bins and labels
bins = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

# Categorize the Heat_Fre into bins
df['Heat_Bins'] = pd.cut(df['Heat_Fre'], bins=bins, labels=labels, right=False)

# Group by Heat_Bins and sum the Length_Miles for each group
grouped_data = df.groupby('Heat_Bins')['Length_Miles'].sum().reset_index()

# CalcuLATe the total length for percentage calcuLATion
total_length = grouped_data['Length_Miles'].sum()

# Plotting the bar chart
plt.figure(figsize=(12, 8))
bars = plt.bar(grouped_data['Heat_Bins'], grouped_data['Length_Miles'], color='blue', edgecolor='black')
plt.xlabel('Heat Frequency')
plt.ylabel('Sum of Length in Miles')
plt.title('Sum of Railway Length by Heat Frequency Between 1 to 10 Events')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.2)

# Increase the frame from the top by 10%
plt.ylim(0, grouped_data['Length_Miles'].max() * 1.075)

# Add frequency and percentage above each bar
for bar in bars:
    height = bar.get_height()
    percentage = (height / total_length) * 100
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}\n({percentage:.1f}%)', ha='center', va='bottom')

plt.show()

print("Done6!")

# %%
