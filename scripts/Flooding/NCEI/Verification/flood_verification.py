#%%
#! ################################################################################################
#! # Title: Flood Accident Verification with NCEI Flood Data and HUC Polygons
#! Purpose: Match railroad flood accidents with NCEI flash/riverine floods by date and location,
#!          check containment within HUC2-HUC12 polygons, output matched CSVs, and plot results.
#! Run Time: [Depends on data size, est. few minutes]
#! ################################################################################################

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from datetime import datetime

#%% Load flood accident points
accident_fp = (r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose"
               r"\2025\New_Journal\Verification\Flood\flood_accidents.csv")
accidents_df = pd.read_csv(accident_fp, encoding='ISO-8859-1')

# Extract lat/lon from 'Location' WKT
accidents_df['Longitude'] = accidents_df['Location'].str.extract(r'POINT \((-?\d+\.\d+)')[0].astype(float)
accidents_df['Latitude'] = accidents_df['Location'].str.extract(r'POINT \(-?\d+\.\d+ (\d+\.\d+)\)')[0].astype(float)

# Create GeoDataFrame
accidents_gdf = gpd.GeoDataFrame(
    accidents_df,
    geometry=gpd.points_from_xy(accidents_df['Longitude'], accidents_df['Latitude']),
    crs="EPSG:4326"
)

# Add accident date
accidents_gdf['Accident_Date'] = pd.to_datetime(
    accidents_gdf[['Year', 'Accident Month', 'Day']].rename(columns={'Year': 'year', 'Accident Month': 'month', 'Day': 'day'})
)

#%% Load NCEI Flash Flood and Riverine Flood data
flash_fp = (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
            r"\3_Flooding\NCEI\NCEI_FlashFlood_Shapefile\NCEI_FlashFlood_Shapefile.shp")

riverine_fp = (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
               r"\3_Flooding\NCEI\NCEI_Flood_Shapefile\NCEI_Flood_Shapefile.shp")

flash_gdf = gpd.read_file(flash_fp, encoding='ISO-8859-1')
riverine_gdf = gpd.read_file(riverine_fp, encoding='ISO-8859-1')

# Preprocess flood dates
for gdf, label in zip([flash_gdf, riverine_gdf], ['Flash', 'Riverine']):
    # Ensure BEGIN_YEAR and END_YEARMO are strings
    gdf['BEGIN_YEAR'] = gdf['BEGIN_YEAR'].astype(str)
    gdf['END_YEARMO'] = gdf['END_YEARMO'].fillna(gdf['BEGIN_YEAR']).astype(str)
    
    # Extract year and month for Begin
    gdf['Begin_Year'] = gdf['BEGIN_YEAR'].str[:4].astype(int)
    gdf['Begin_Month'] = gdf['BEGIN_YEAR'].str[4:6].astype(int)
    
    # Extract year and month for End (copied from BEGIN if missing)
    gdf['End_Year'] = gdf['END_YEARMO'].str[:4].astype(int)
    gdf['End_Month'] = gdf['END_YEARMO'].str[4:6].astype(int)
    
    # Build datetime objects (no defaults)
    gdf['Begin_Date'] = pd.to_datetime(
        {'year': gdf['Begin_Year'], 'month': gdf['Begin_Month'], 'day': gdf['BEGIN_DAY']},
        errors='coerce'
    )
    gdf['End_Date'] = pd.to_datetime(
        {'year': gdf['End_Year'], 'month': gdf['End_Month'], 'day': gdf['END_DAY']},
        errors='coerce'
    )
    
    gdf['Flood_Type'] = label

# Ensure both flood datasets use the same CRS (WGS 84)
flash_gdf = flash_gdf.to_crs("EPSG:4326")
riverine_gdf = riverine_gdf.to_crs("EPSG:4326")

# Merge flood datasets
floods_gdf = pd.concat([flash_gdf, riverine_gdf], ignore_index=True)

#%% Load HUC Polygons
huc_files = {
    'HUC2': (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
             r"\3_Flooding\HUC&Watershed\HUCs\2_Unit\WBD_HUC2.shp"),
    'HUC4': (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
             r"\3_Flooding\HUC&Watershed\HUCs\4_Unit\WBD_HUC4.shp"),
    'HUC6': (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
             r"\3_Flooding\HUC&Watershed\HUCs\6_Unit\WBD_HUC6.shp"),
    'HUC8': (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
             r"\3_Flooding\HUC&Watershed\HUCs\8_Unit\WBD_HUC8.shp"),
    'HUC10': (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
              r"\3_Flooding\HUC&Watershed\HUCs\10_Unit\WBD_HUC10.shp"),
    'HUC12': (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
              r"\3_Flooding\HUC&Watershed\HUCs\12_Unit\WBD_HUC12.shp")
}


hucs = {name: gpd.read_file(path) for name, path in huc_files.items()}

# Check the number of rows in each HUC shapefile
for name, gdf in hucs.items():
    print(f"{name}: {len(gdf)} rows")

# Reproject all HUC files to EPSG:4326
hucs = {name: gdf.to_crs("EPSG:4326") for name, gdf in hucs.items()}

#%%
results_summary = []  # Will hold final accident rows with HUC event IDs

for idx, accident in accidents_gdf.iterrows():
    accident_result = accident.copy()  # Always copy accident attributes

    # Filter floods by accident date
    matched_floods = floods_gdf[
        (floods_gdf['Begin_Date'] <= accident['Accident_Date']) &
        (floods_gdf['End_Date'] >= accident['Accident_Date'])
    ]
    
    # For each HUC level (2-12)
    for huc_name, huc_gdf in hucs.items():
        if not matched_floods.empty:
            # Check if accident is within this HUC
            accident_in_huc = gpd.sjoin(
                gpd.GeoDataFrame([accident], crs=accidents_gdf.crs),
                huc_gdf,
                predicate='within',
                how='inner'
            )
            
            if not accident_in_huc.empty:
                # Get the HUC polygon's unique identifier ('tnmid')
                huc_polygon_id = accident_in_huc.iloc[0]['tnmid']
                
                # Filter floods within the same HUC polygon (matching 'tnmid')
                floods_in_huc = gpd.sjoin(matched_floods, huc_gdf, predicate='within', how='inner')
                floods_in_same_polygon = floods_in_huc[floods_in_huc['tnmid'] == huc_polygon_id]
                
                if not floods_in_same_polygon.empty:
                    EPISODE_IDs = floods_in_same_polygon['EPISODE_ID'].astype(str).tolist()
                    accident_result[huc_name] = ", ".join(EPISODE_IDs)
                else:
                    accident_result[huc_name] = ""  # No floods in the same polygon
            else:
                accident_result[huc_name] = ""  # Accident not in this HUC
        else:
            accident_result[huc_name] = ""  # No floods matching date

    results_summary.append(accident_result)

# Save final output
final_df = pd.DataFrame(results_summary)
final_df.to_csv("Accidents_With_HUC_EventIDs.csv", index=False)

#%% Plotting the results
# Load the CSV
csv_fp = (r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose"
          r"\2025\New_Journal\Verification\Flood\Accidents_With_HUC_EventIDs.csv")
df = pd.read_csv(csv_fp)

# Define HUC columns
huc_cols = ['HUC12', 'HUC10', 'HUC8', 'HUC6', 'HUC4', 'HUC2']

# Count non-empty cells (matched accidents) for each HUC column
matched_counts = df[huc_cols].apply(lambda col: col.notna() & (col != ""), axis=0).sum()

# Total number of accidents
total_accidents = len(df)

# Calculate percentages
percentages = (matched_counts / total_accidents * 100).round(1)

# Plot
plt.figure(figsize=(8,6))
bars = plt.bar(huc_cols, matched_counts)

# Add frequency and percentage labels above bars
for bar, count, pct in zip(bars, matched_counts, percentages):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
             f"{count} ({pct}%)", ha='center', va='bottom')

plt.ylabel("Number of Matched Accidents")
plt.xlabel("HUC Level")
plt.title("Matched Accidents per HUC Level (Same Day Matching)")  
plt.legend([f"Total Train Accidents Caused by Flooding: {total_accidents}"], loc='upper left', fontsize=10)
plt.tight_layout()
plt.show()

#%%
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# Data
sizes = (matched_counts[::-1] / total_accidents * 100).round(1)  # Convert to percentages
labels = huc_cols[::-1]

# Colors
colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(sizes)))

# Plot
fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
theta = np.radians(np.arange(0, 360, 60))  # Angles: 0°, 60°, 120°, ..., 300°

# Bars (scale with percentages)
bars = ax.bar(theta, sizes, width=0.5, bottom=0, align='center', alpha=0.9, color=colors)

# Set radial gridlines at 0, 20, 40, 60, 80, 100
tick_values = [0, 20, 40, 60, 80, 100]
ax.set_ylim(0, 100)
ax.set_yticks(tick_values)
ax.set_yticklabels([])
ax.set_xticklabels([])

# Style gridlines (solid for 100%, dashed for others)
ax.yaxis.grid(True, linestyle='--', linewidth=0.2, alpha=0.5)
ax.spines['polar'].set_visible(False)

# Set radial ticks at every 60°, but hide labels
ax.set_xticks(theta)
ax.set_xticklabels([])

# Style the radial (angular) lines as dashed and transparent
for line in ax.xaxis.get_gridlines():
    line.set_linestyle('--')
    line.set_linewidth(0.5)
    line.set_alpha(0.8)


# Custom radial gridlines
for tick in tick_values:
    if tick == 100:
        ax.plot(np.linspace(0, 2*np.pi, 500), [tick]*500, color='black', linewidth=1)
    else:
        ax.plot(np.linspace(0, 2*np.pi, 500), [tick]*500, linestyle='--', linewidth=0.2, color='gray', alpha=0.7)

# Annotate inside bars (count + percentage)
original_counts = matched_counts[::-1]
percentages = sizes
for angle, size, count, pct in zip(theta, sizes, original_counts, percentages):
    ax.text(angle, size/2, f"{count}\n({pct}%)", 
            ha='center', va='center', fontsize=8, color='black')

# Add HUC labels outside bars (positioned just beyond each bar based on percentage)
for angle, size, label in zip(theta, sizes, labels):
    ax.text(angle, size + 10, label, ha='center', va='center', fontsize=8)

legend_elements = [Patch(facecolor=colors[i], label=labels[i]) for i in range(len(labels))]
ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(0.6, 0.021), fontsize=8, title="HUC Levels", title_fontsize='10', frameon=True)

# Save and show
plt.tight_layout()
save_fp = (r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose"
           r"\2025\New_Journal\Verification\Flood\flood_verification.png")
plt.savefig(save_fp, dpi=400, bbox_inches='tight', transparent=False)
plt.show()


# %%
