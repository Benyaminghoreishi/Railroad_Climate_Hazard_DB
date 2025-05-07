# %%
# # TODO: Plotting the U.S. Railway Network by Flood Exposure
########################################
# ! Importing the necessary libraries
########################################
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.affinity import translate, scale
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import contextily as ctx
import numpy as np
import os

# %%
# ===============================================================================================
# ! 1_Loading U.S. States, Railway, and Stations Sensors
# ===============================================================================================
# Set the base directory with the absolute path
base_dir = os.path.abspath(os.path.join("..", ".."))

# Load U.S. states shapefile
states_gdf = os.path.join(base_dir, "Shapefiles", "cb_2018_us_state_500k", "cb_2018_us_state_500k.shp")

# Load the intersected railway shapefile with flood frequency
railway_gdf = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                                 "Rail_Segments_SplitThenOverlayed_with_Flood_freq.shp")

# Load shapefiles
states_gdf = gpd.read_file(states_gdf)
railway_gdf = gpd.read_file(railway_gdf)
# %% 
# ===============================================================================================
# ! 2_Reprojecting and Filtering Shapefiles to Include Only 50 U.S. States
# ===============================================================================================

states_gdf = states_gdf.to_crs(epsg=2163)
railway_gdf = railway_gdf.to_crs(epsg=2163)

# Filter to include only the 50 states in the states shapefile
states_gdf = states_gdf[states_gdf['STUSPS'].isin([
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL',
    'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT',
    'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
    'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
])]

# %% 
# ===============================================================================================
# ! 3_Separating Contiguous U.S., Alaska, and Hawaii into Individual GeoDataFrames
# ===============================================================================================

# Separate the contiguous U.S., Alaska, and Hawaii into individual GeoDataFrames
contiguous_gdf = states_gdf[~states_gdf['STUSPS'].isin(['AK', 'HI'])]
alaska_gdf = states_gdf[states_gdf['STUSPS'] == 'AK']
hawaii_gdf = states_gdf[states_gdf['STUSPS'] == 'HI']

# Separate railways in Alaska and Hawaii based on their spatial extent
alaska_railways = railway_gdf[railway_gdf.intersects(alaska_gdf.unary_union)]
hawaii_railways = railway_gdf[railway_gdf.intersects(hawaii_gdf.unary_union)]

# Exclude Alaska and Hawaii railways from the contiguous railways
contiguous_railways = railway_gdf[
    ~railway_gdf.intersects(alaska_gdf.unary_union) & ~railway_gdf.intersects(hawaii_gdf.unary_union)
]

# %% A
# ===============================================================================================
# ! 4_Adjusting Geometries for Alaska and Hawaii to Fit Contiguous U.S. Map
# ===============================================================================================

# Adjust Alaska: Move further to the right
alaska_gdf['geometry'] = alaska_gdf['geometry'].apply(lambda geom: scale(geom, xfact=0.35, yfact=0.35, origin=(0, 0)))
alaska_gdf['geometry'] = alaska_gdf['geometry'].apply(lambda geom: translate(geom, xoff=-700000, yoff=-2650000))

# Adjust Hawaii: Make smaller and move further to the right
hawaii_gdf['geometry'] = hawaii_gdf['geometry'].apply(lambda geom: scale(geom, xfact=1, yfact=1, origin=(0, 0)))  # Keep scale at 1
hawaii_gdf['geometry'] = hawaii_gdf['geometry'].apply(lambda geom: translate(geom, xoff=5000000, yoff=-1300000))

# %% 
# ===============================================================================================
# ! 5_Applying Adjustments to Railway Geometries for Alaska and Hawaii
# ===============================================================================================

# Apply the same transformations to the railways in Alaska
alaska_railways['geometry'] = alaska_railways['geometry'].apply(lambda geom: scale(geom, xfact=0.35, yfact=0.35, origin=(0, 0)))
alaska_railways['geometry'] = alaska_railways['geometry'].apply(lambda geom: translate(geom, xoff=-700000, yoff=-2650000))

# Apply the same transformations to the railways in Hawaii
hawaii_railways['geometry'] = hawaii_railways['geometry'].apply(lambda geom: scale(geom, xfact=1, yfact=1, origin=(0, 0)))  # Keep scale at 1
hawaii_railways['geometry'] = hawaii_railways['geometry'].apply(lambda geom: translate(geom, xoff=5000000, yoff=-1300000))

# Combine the adjusted railways with the main railway GeoDataFrame
adjusted_railways = pd.concat([contiguous_railways, alaska_railways, hawaii_railways])

# ===============================================================================================
# ! 6_Combining Adjusted Railways and States into Unified GeoDataFrames
# ===============================================================================================
# Combine the contiguous U.S., Alaska, and Hawaii into a single GeoDataFrame
us_gdf = pd.concat([contiguous_gdf, alaska_gdf, hawaii_gdf])


#%%
# ===============================================================================================
# ! 7_Plotting Histogram of Total Railway Length Exposed to Flood Frequencies
# ===============================================================================================

# Step 1: Calculate the arithmetic mean of (Length_Mil_i * Flood_fre_i) / (Length_Mil_i)
weighted_mean_Flood_fred = (
    (adjusted_railways['Length_Mil'] * adjusted_railways['Flood_fre']).sum() / adjusted_railways['Length_Mil'].sum()
)

# Step 2: Define bins
# Bin 1: Lengths with Flood_fre == 0
bin_1_length = adjusted_railways.loc[adjusted_railways['Flood_fre'] == 0, 'Length_Mil'].sum()

# Bin 2: Lengths where Flood_fre is between 1 and the calculated weighted mean
bin_2_length = adjusted_railways.loc[
    (adjusted_railways['Flood_fre'] > 0) & (adjusted_railways['Flood_fre'] <= weighted_mean_Flood_fred), 
    'Length_Mil'
].sum()

# Bin 3: Lengths where Flood_fre is greater than the calculated weighted mean
bin_3_length = adjusted_railways.loc[
    adjusted_railways['Flood_fre'] > weighted_mean_Flood_fred, 
    'Length_Mil'
].sum()

# Step 3: Prepare data for the histogram
bins = ['0 (No Flood)', f'1 - {weighted_mean_Flood_fred:.0f}', f'>{weighted_mean_Flood_fred:.0f}']
bin_totals = [bin_1_length, bin_2_length, bin_3_length]

# Calculate percentages for the y-axis
total_mileage = adjusted_railways['Length_Mil'].sum()
bin_percentages = [(bin_total / total_mileage) * 100 for bin_total in bin_totals]

# Step 4: Plot the histogram
plt.figure(figsize=(12, 6))
plt.bar(bins, bin_percentages, color=['gray', 'lightblue', 'darkblue'], edgecolor='black')
plt.title('Percentage of Total Railway Length Exposed to Flood', fontsize=14)
plt.xlabel('Flood Frequency Categories', fontsize=12)
plt.ylabel('Percentage of Total Railway Length (%)', fontsize=12)

# Add percentage labels on top of the bars
for i, percentage in enumerate(bin_percentages):
    plt.text(i, percentage + 1, f"{percentage:.1f}%", ha='center', fontsize=10)

# Add a legend for the weighted mean
plt.legend([f"Weighted Mean: {weighted_mean_Flood_fred:.0f}"], loc='upper right')

# Add gridlines for y-axis
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

# %%
# ===============================================================================================
# ! 8_Defining Custom Color Ranges and Plotting Railway Network by Categorized Flood Exposure
# ===============================================================================================

# Define the weighted mean
weighted_mean_Flood_fred = (
    (adjusted_railways['Length_Mil'] * adjusted_railways['Flood_fre']).sum() / adjusted_railways['Length_Mil'].sum()
)

# Define the custom ranges, colors, and corresponding percentages
custom_ranges = [
    {"range": f"No Flood ({bin_percentages[0]:.0f}%)", "color": "gray"},   # No Flood
    {"range": f"1 - {weighted_mean_Flood_fred:.0f} ({bin_percentages[1]:.0f}%)", "color": "blue"},   # Below Weighted Mean
    {"range": f">{weighted_mean_Flood_fred:.0f} ({bin_percentages[2]:.0f}%)", "color": "red"},       # Above Weighted Mean
]

# Create color patches for the custom legend
patches = [
    mpatches.Patch(color=item["color"], label=item["range"]) for item in custom_ranges
]

# Function to assign colors based on the new ranges
def assign_color(value):
    if value == 0:
        return "gray"       # No Flood
    elif 1 <= value <= weighted_mean_Flood_fred:
        return "blue"       # Below Weighted Mean
    elif value > weighted_mean_Flood_fred:
        return "red"        # Above Weighted Mean
    return "gray"           # Default for out-of-range values

# Apply the colors to the column
adjusted_railways["custom_color"] = adjusted_railways["Flood_fre"].apply(assign_color)

# Plot the map
fig, ax = plt.subplots(figsize=(17, 12.75))

adjusted_railways.plot(
    ax=ax,
    color=adjusted_railways["custom_color"],  # Use custom colors
    linewidth=1.5
)

us_gdf.plot(ax=ax, color="white", edgecolor="black", linewidth=0.2)

# Add the custom legend
ax.legend(
    handles=patches,
    title="Flood Events (Range)",
    loc="lower left",
    fontsize="small",
    title_fontsize="medium",
    frameon=True
)

# Add title and clean up
ax.set_title("U.S. Railway Network Categorized by Flood Exposure", fontsize=12)
plt.axis("off")  # Turn off axis for a clean map

# Load the intersected railway shapefile with flood frequency
railway_gdf = os.path.join("..", "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                                 "New_Intersected_Railway_with_Flood_freq.shp")

# Extract the directory where the railway shapefile is located
railway_dir = os.path.dirname(railway_gdf)

# Define the output file path for the plot
output_plot_path = os.path.join(railway_dir, "us_rail_network_by_flood_exposure.png")

# Save the plot with reduced white space
plt.savefig(output_plot_path, dpi=1200, bbox_inches='tight', pad_inches=0.05)

# Optional: Save as SVG for vector format
# plt.savefig(os.path.join(railway_dir, "us_rail_network_by_flood_exposure.svg"), format='svg')

plt.show()

print(f"✅ Plot saved at: {output_plot_path}")
