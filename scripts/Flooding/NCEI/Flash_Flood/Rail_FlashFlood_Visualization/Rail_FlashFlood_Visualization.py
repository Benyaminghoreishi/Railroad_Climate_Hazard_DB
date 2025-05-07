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
from shapely.geometry import Point
from pyproj import Transformer
# %%
# ===============================================================================================
# ! 1_Loading U.S. States, Railway, and Stations Sensors
# ===============================================================================================
# Set the base directory with the absolute path (Move up two levels from the current directory)
base_dir = os.path.abspath(os.path.join("..", ".."))  

# Load U.S. states shapefile
states_gdf = os.path.join(base_dir, "Shapefiles", "cb_2018_us_state_500k", 
                          "cb_2018_us_state_500k.shp")

# Load the intersected railway shapefile with flood frequency
railway_gdf = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                                 "Rail_Segments_SplitThenOverlayed_with_flashflood_Freq.shp")

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

# Step 1: Calculate the arithmetic mean of (Length_Mil_i * Flash_Fre_i) / (Length_Mil_i)
weighted_mean_Flash_Fred = (
    (adjusted_railways['Length_Mil'] * adjusted_railways['Flash_Fre']).sum() / adjusted_railways['Length_Mil'].sum()
)

# Step 2: Define bins
# Bin 1: Lengths with Flash_Fre == 0
bin_1_length = adjusted_railways.loc[adjusted_railways['Flash_Fre'] == 0, 'Length_Mil'].sum()

# Bin 2: Lengths where Flash_Fre is between 1 and the calculated weighted mean
bin_2_length = adjusted_railways.loc[
    (adjusted_railways['Flash_Fre'] > 0) & (adjusted_railways['Flash_Fre'] <= weighted_mean_Flash_Fred), 
    'Length_Mil'
].sum()

# Bin 3: Lengths where Flash_Fre is greater than the calculated weighted mean
bin_3_length = adjusted_railways.loc[
    adjusted_railways['Flash_Fre'] > weighted_mean_Flash_Fred, 
    'Length_Mil'
].sum()

# Step 3: Prepare data for the histogram
bins = ['0 (No Flood)', f'1 - {weighted_mean_Flash_Fred:.0f}', f'>{weighted_mean_Flash_Fred:.0f}']
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
plt.legend([f"Weighted Mean: {weighted_mean_Flash_Fred:.0f}"], loc='upper right')

# Add gridlines for y-axis
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

# %%
# ===============================================================================================
# ! 8_Generating Map of U.S. Railway Network by Flash Flood Exposure Levels (Custom Legend)
# ===============================================================================================

# Define the weighted mean
weighted_mean_Flash_Fred = (
    (adjusted_railways['Length_Mil'] * adjusted_railways['Flash_Fre']).sum() / adjusted_railways['Length_Mil'].sum()
)

# Define the custom ranges, colors, and corresponding percentages
custom_ranges = [
    {"range": f"No Flood ({bin_percentages[0]:.0f}%)", "color": "#ffba08"},   # No Flood
    {"range": f"1 - {weighted_mean_Flash_Fred:.0f} ({bin_percentages[1]:.0f}%)", "color": "#1E90FF"},   # Below Weighted Mean
    {"range": f">{weighted_mean_Flash_Fred:.0f} ({bin_percentages[2]:.0f}%)", "color": "#FF0000"},       # Above Weighted Mean
]

# Create legend patches (Default)
patches = [mpatches.Patch(color=item["color"], label=item["range"]) for item in custom_ranges]

# Define output directory and filenames
railway_dir = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit")
os.makedirs(railway_dir, exist_ok=True)

output_plot_with_basemap = os.path.join(railway_dir, "us_rail_network_by_flashflood_exposure_with_basemap.png")
output_plot_no_basemap = os.path.join(railway_dir, "us_rail_network_by_flashflood_exposure_no_basemap.png")

# Function to generate and save plots
def plot_flash_flood_exposure(save_path, add_basemap=False):
    fig, ax = plt.subplots(figsize=(17, 12.75))

    # **Assign color mapping based on basemap presence**
    if add_basemap:
        # **Use Dark Green for "No Flood" when basemap is enabled**
        adjusted_railways["custom_color"] = adjusted_railways["Flash_Fre"].apply(
            lambda x: "#ffba08" if x == 0 else "#1E90FF" if 1 <= x <= weighted_mean_Flash_Fred else "#FF0000"
        )
        patches[0] = mpatches.Patch(color="#ffba08", label="No Flood")  # Update legend
    else:
        # **Use Grey for "No Flood" when NO basemap**
        adjusted_railways["custom_color"] = adjusted_railways["Flash_Fre"].apply(
            lambda x: "#ffba08" if x == 0 else "#1E90FF" if 1 <= x <= weighted_mean_Flash_Fred else "#FF0000"
        )
        patches[0] = mpatches.Patch(color="#ffba08", label="No Flood")  # Update legend

    # **Plot the state boundaries**
    us_gdf.plot(ax=ax, color="none", edgecolor="black", linewidth=0.5, alpha=0.7, zorder=1)

    # **Plot the railway network with updated flood exposure colors**
    adjusted_railways.plot(ax=ax, color=adjusted_railways["custom_color"], linewidth=1.5, zorder=2)

    # **Add the custom legend**
    ax.legend(handles=patches, title="Flash Flood Events Frequency", loc="lower left", fontsize=12, title_fontsize=14, frameon=True)

    # **Add basemap if required**
    if add_basemap:
        ctx.add_basemap(
            ax, 
            source=ctx.providers.OpenStreetMap.Mapnik, 
            crs=adjusted_railways.crs.to_string(),
            zoom=8
        )

    # **Add title and remove axis**
    ax.set_title("U.S. Railway Network Categorized by Flash Flood Exposure", fontsize=12)
    plt.axis("off")

    # **Save the figure**
    plt.savefig(save_path, dpi=1200, bbox_inches='tight', pad_inches=0)
    plt.close()

    print(f"✅ Plot saved at: {save_path}")

# **Generate both plots**
plot_flash_flood_exposure(output_plot_with_basemap, add_basemap=True)  # With basemap
plot_flash_flood_exposure(output_plot_no_basemap, add_basemap=False)  # No basemap

print("✅ Both plots have been generated and saved successfully!")

# %%
#################################################################################
# ! 9_Generating Zoomed-In City Maps with OpenStreetMap HOT Basemap
#################################################################################
# Define the base directory and output directory for city maps
city_maps_dir = os.path.join(base_dir, "3_Flooding", "HUC&Watershed", "HUCs", "12_Unit", 
                                 "City_FlashFlood_Maps")
os.makedirs(city_maps_dir, exist_ok=True)

# Define the 10 most important cities with their latitude and longitude
cities = {
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "Houston": (29.7604, -95.3698),
    "Phoenix": (33.4484, -112.0740),
    "Philadelphia": (39.9526, -75.1652),
    "San Antonio": (29.4241, -98.4936),
    "San Diego": (32.7157, -117.1611),
    "Dallas": (32.7767, -96.7970),
    "San Jose": (37.3382, -121.8863),
}

# Convert city coordinates to CRS EPSG:2163
transformer = Transformer.from_crs("EPSG:4326", "EPSG:2163", always_xy=True)
city_points = {city: transformer.transform(lon, lat) for city, (lat, lon) in cities.items()}

# Define optimized colors for OpenStreetMap HOT
adjusted_railways["custom_color"] = adjusted_railways["Flash_Fre"].apply(
    lambda x: "#ffba08" if x == 0 else "#1E90FF" if 1 <= x <= 3 else "#FF0000"
)

# Define legend colors to match the new railway colors
custom_ranges_no_percentage = [
    {"range": "No Flood", "color": "#ffba08"},  # Teal (Neutral but visible)
    {"range": "1 - 3 Flash Floods", "color": "#1E90FF"},  # Medium Blue (Clearer than dark blue)
    {"range": ">3 Flash Floods", "color": "#FF0000"},  # Deep Red (Danger, but not overwhelming)
]

# Generate color legend without percentages
legend_patches_no_percentage = [
    mpatches.Patch(color=item["color"], label=item["range"]) for item in custom_ranges_no_percentage
]

# Function to plot zoomed-in maps with Esri World Imagery basemap and no percentage in the legend
def plot_zoomed_city_no_percentage(city_name, city_coords, buffer_size=250000, left_expansion=150000):
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot the railway data within the zoomed-in region
    adjusted_railways.plot(ax=ax, color=adjusted_railways["custom_color"], linewidth=1.5)

    # Set zoom extent around the city
    x, y = city_coords
    # Adjust x-limits: expand only the left side
    ax.set_xlim([x - buffer_size, x + buffer_size])
    ax.set_ylim([y - buffer_size, y + buffer_size])

    # Add high-quality Esri World Imagery basemap
    ctx.add_basemap(
        ax, 
        source=ctx.providers.OpenStreetMap.Mapnik, 
        crs=adjusted_railways.crs.to_string(), 
        zoom=10)

        
    # Add title
    ax.set_title(f"Flash Flood Exposure in {city_name}", fontsize=14)
    plt.axis("off")

    # Add the custom legend without percentages
    ax.legend(handles=legend_patches_no_percentage, title="Flash Flood Events Frequency", 
              loc="lower left", fontsize="small", frameon=True)

    # Define output path for the city map
    city_map_path = os.path.join(city_maps_dir, f"{city_name.replace(' ', '_')}_FlashFlood_No_Percentage.png")

    # Save the plot
    plt.savefig(city_map_path, dpi=600, bbox_inches='tight', pad_inches=0)
    plt.close()

    print(f"✅ Map saved for {city_name}: {city_map_path}")

# Loop through each city and generate a zoomed-in map without percentage in the legend
for city, coords in city_points.items():
    plot_zoomed_city_no_percentage(city, coords)

print("✅ All city maps have been generated successfully without percentages in the legend!")


# %%
