# %%
# ! ################################################################################################
# ! # Title: Buckling Accident Verification with NCEI Buckling Data and HUC Polygons
# ! Purpose: Match railroad buckling accidents with NCEI flash/riverine buckling by date and location,
# !          check containment within HUC2-HUC12 polygons, output matched CSVs, and plot results.
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
        r"\2025\New_Journal\Verification\Buckling\buckling_accidents.csv"
)
accidents_df = pd.read_csv(accident_fp, encoding='ISO-8859-1')

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
    accidents_gdf[['Year', 'Accident Month', 'Day']].rename(columns={'Year': 'year', 'Accident Month': 'month', 'Day': 'day'})
)

# %%
# ! ###########################################################################################################
# ! # Title: Extract Date Fields for Heat and Extreme Heat Events (Parsing YYYYMM from BEGIN_YEAR & END_YEARMO)
# ! Purpose: Parse start and end dates from combined year-month fields (YYYYMM) and create datetime objects.
# ! Run Time: [~5 sec]
# ! ###########################################################################################################

# Load Heat and Extreme Heat shapefile
heat_fp = (
    r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU"
    r"\1_Rail_Project\5_Sunkink\Heat_EXtremeHeat_Combined"
    r"\Heat_EXtremeHeat_Combined.shp"
)
heat_gdf = gpd.read_file(heat_fp)

# Ensure BEGIN_YEAR and END_YEARMO are strings
heat_gdf['BEGIN_YEAR'] = heat_gdf['BEGIN_YEAR'].astype(str)
heat_gdf['END_YEARMO'] = heat_gdf['END_YEARMO'] \
    .fillna(heat_gdf['BEGIN_YEAR']) \
    .astype(str)

# Extract Begin Year and Month
heat_gdf['Begin_Year'] = heat_gdf['BEGIN_YEAR'].str[:4].astype(int)
heat_gdf['Begin_Month'] = heat_gdf['BEGIN_YEAR'].str[4:6].astype(int)

# Extract End Year and Month (fallback to Begin if missing)
heat_gdf['End_Year'] = heat_gdf['END_YEARMO'].str[:4].astype(int)
heat_gdf['End_Month'] = heat_gdf['END_YEARMO'].str[4:6].astype(int)

# Optional: Create datetime fields (default day=1)
heat_gdf['Begin_Date'] = pd.to_datetime({
    'year': heat_gdf['Begin_Year'],
    'month': heat_gdf['Begin_Month'],
    'day': heat_gdf['BEGIN_DAY']  # Uses BEGIN_DAY field here
}, errors='coerce')

heat_gdf['End_Date'] = pd.to_datetime({
    'year': heat_gdf['End_Year'],
    'month': heat_gdf['End_Month'],
    'day': heat_gdf['END_DAY']  # Uses END_DAY field here
}, errors='coerce')

# Check results
print(heat_gdf[['BEGIN_YEAR', 'Begin_Year', 'Begin_Month', 'Begin_Date',
                'END_YEARMO', 'End_Year', 'End_Month', 'End_Date']].head())

print("Heat event dates processed successfully!")

# %%
# ! ################################################################################################
# ! # Title: Merge Climate Division Shapefiles with Duplicate Column Handling
# ! Purpose: Combine AK, HI, and CONUS shapefiles while resolving duplicate attribute names.
# ! Run Time: [~5 sec]
# ! ################################################################################################

# Load shapefiles
ak_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
    r"\Verification\Buckling\climate_devisions\AK_climate_divisions"
    r"\AK_divisions_NAD83.shp"
)
hi_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
    r"\Verification\Buckling\climate_devisions\HI_climate_divisions"
    r"\ClimDiv12_polygon_clip.shp"
)
conus_path = (
    r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
    r"\Verification\Buckling\climate_devisions\CONUS_CLIMATE_DIVISIONS.shp"
    r"\GIS.OFFICIAL_CLIM_DIVISIONS.shp"
)

gdf_ak = gpd.read_file(ak_path)
gdf_hi = gpd.read_file(hi_path)
gdf_conus = gpd.read_file(conus_path)

# Resolve duplicate columns by renaming non-essential fields


def rename_columns(gdf, prefix):
    cols = {
        col: f"{prefix}_{col}"
        for col in gdf.columns
        if col not in ['geometry']
    }
    return gdf.rename(columns=cols)


gdf_ak = rename_columns(gdf_ak, 'AK')
gdf_hi = rename_columns(gdf_hi, 'HI')
gdf_conus = rename_columns(gdf_conus, 'CONUS')

# Ensure CRS consistency
target_crs = gdf_conus.crs
gdf_ak = gdf_ak.to_crs(target_crs)
gdf_hi = gdf_hi.to_crs(target_crs)

# Merge
combined_gdf = pd.concat([gdf_ak, gdf_hi, gdf_conus], ignore_index=True)

# Save as GeoPackage
output_gpkg = (
    r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
    r"\Verification\Buckling\climate_devisions\Combined_Climate_Divisions.gpkg"
)
combined_gdf.to_file(output_gpkg, layer='climate_divisions', driver='GPKG')

print("Combined climate divisions saved successfully!")

# %%
# ! ################################################################################################
# ! # Title: Dissolve Climate Regions by 'ClimateReg' Attribute 
# ! Purpose: Merge polygons in the Climate Regions shapefile based on 'ClimateReg' attribute.
# ! Run Time: [~5 sec]
# ! ################################################################################################

# Load the Climate Regions shapefile
climate_fp = (
    r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
    r"\Verification\Buckling\climate_regions\climate_regions.shp"
)
climate_gdf = gpd.read_file(climate_fp)

# Dissolve polygons based on 'ClimateReg' column (merge by region)
dissolved_gdf = climate_gdf.dissolve(by='ClimateReg')

# Optional: Reset index so 'ClimateReg' becomes a column again
dissolved_gdf = dissolved_gdf.reset_index()

# Save the new shapefile
output_fp = (
    r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
    r"\Verification\Buckling\climate_regions\Dissolved_Climate_Regions.shp"
)
dissolved_gdf.to_file(output_fp)

print("Dissolved climate regions saved successfully!")

# %%
# ! ################################################################################################
# ! # Title: Load and Reproject Forecast, Climate, and State Shapefiles
# ! Purpose: Read NWS zones, county warning areas, climate divisions/regions, and states shapefiles,
# !          reproject to EPSG:4326, and report row counts.
# ! Run Time: [~5 sec]
# ! ################################################################################################

# Define file paths
shapefiles = {
    'NWS_Forecast_Zones': (
        r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
        r"\Verification\Buckling\NWS Public Forecast Zones\z_18mr25.shp"
    ),
    'Climate_Divisions': (
        r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
        r"\Verification\Buckling\climate_devisions\Combined_Climate_Divisions.gpkg"
    ),
    'County_Warning_Areas': (
        r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
        r"\Verification\Buckling\County Warning Area Boundaries\w_18mr25.shp"
    ),
    'States': (
        r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
        r"\Verification\Buckling\cb_2018_us_state_500k\cb_2018_us_state_500k.shp"
    )
    # ,
    # 'Climate_Regions': (
    #     r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
    #     r"\Verification\Buckling\climate_regions\climate_regions.shp"
    # )
}

# Load shapefiles into GeoDataFrames
gdfs = {name: gpd.read_file(path) for name, path in shapefiles.items()}

# Check row counts
for name, gdf in gdfs.items():
    print(f"{name}: {len(gdf)} rows")

# Reproject all shapefiles to EPSG:4326
gdfs = {name: gdf.to_crs("EPSG:4326") for name, gdf in gdfs.items()}

print("All shapefiles loaded and reprojected to EPSG:4326 successfully!")

# %%
# ! ################################################################################################
# ! # Title: Match Buckling Accidents with Heat Events and NWS Forecast Zones
# ! Purpose: Match buckling accidents with heat events by date and location, check containment within
# !          NWS forecast zones, and output matched CSV.
# ! Run Time: [Depends on data size, est. few minutes]
# ! ################################################################################################
# Add unique zone ID to the forecast zones GeoDataFrame
forecast_zones_gdf = gdfs['NWS_Forecast_Zones']
forecast_zones_gdf['ZONE_UNIQUE_ID'] = forecast_zones_gdf.index + 1  # Just adds 1, 2, 3...

results_summary = []

for idx, accident in accidents_gdf.iterrows():
    accident_result = accident.copy()

    # Filter heat events by accident date
    matched_heat_events = heat_gdf[
        (heat_gdf['Begin_Date'] <= accident['Accident_Date']) &
        (heat_gdf['End_Date'] >= accident['Accident_Date'])
    ]

    if not matched_heat_events.empty:
        # Check if accident is within a forecast zone
        accident_in_zone = gpd.sjoin(
            gpd.GeoDataFrame([accident], crs=accidents_gdf.crs),
            forecast_zones_gdf,
            predicate='within',
            how='inner'
        )

        if not accident_in_zone.empty:
            zone_id = accident_in_zone.iloc[0]['ZONE_UNIQUE_ID']

            # Filter heat events that are in the same zone
            heat_in_zone = gpd.sjoin(
                matched_heat_events,
                forecast_zones_gdf,
                predicate='within',
                how='inner'
            )
            heat_in_same_zone = heat_in_zone[
                heat_in_zone['ZONE_UNIQUE_ID'] == zone_id
            ]

            if not heat_in_same_zone.empty:
                EPISODE_IDs = heat_in_same_zone['EPISODE_ID'] \
                    .astype(str).tolist()
                accident_result[
                    'Matched_Heat_EPISODE_IDs_NWS_Forecast_Zones'
                ] = ", ".join(EPISODE_IDs)
            else:
                accident_result[
                    'Matched_Heat_EPISODE_IDs_NWS_Forecast_Zones'
                ] = ""
        else:
            accident_result['Matched_Heat_EPISODE_IDs_NWS_Forecast_Zones'] = ""
    else:
        accident_result['Matched_Heat_EPISODE_IDs_NWS_Forecast_Zones'] = ""

    results_summary.append(accident_result)

# Save final output
final_df = pd.DataFrame(results_summary)
final_df.to_csv(
    r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
    r"\Verification\Buckling\Accidents_With_Heat_EventIDs_ForecastZones.csv",
    index=False
)

# %%
# ! ################################################################################################
# ! Day # Title: Buckling Accident Verification with Heat/Extreme Heat Events Across Multiple Boundaries
# ! Purpose: Match railroad buckling accidents with heat/extreme heat events by date and location,
# !          verify spatial containment within multiple boundaries (NWS Forecast Zones, Climate Divisions,
# !          County Warning Areas, States, Climate Regions), and output matched CSV with EPISODE_IDs.
# ! Run Time: [Depends on data size, est. few minutes]
# ! ################################################################################################
# Add unique IDs for all boundary shapefiles
for boundary_name, boundary_gdf in gdfs.items():
    gdfs[boundary_name]['ZONE_UNIQUE_ID'] = gdfs[boundary_name].index + 1  # Adds 1,2,3...

results_summary = []

for idx, accident in accidents_gdf.iterrows():
    accident_result = accident.copy()

    # Filter heat events by accident date
    matched_heat_events = heat_gdf[
        (heat_gdf['Begin_Date'] <= accident['Accident_Date']) &
        (heat_gdf['End_Date'] >= accident['Accident_Date'])
    ]

    if not matched_heat_events.empty:
        for boundary_name, boundary_gdf in gdfs.items():
            # Check if accident is within this boundary
            accident_in_zone = gpd.sjoin(
                gpd.GeoDataFrame([accident], crs=accidents_gdf.crs),
                boundary_gdf,
                predicate='within',
                how='inner'
            )

            if not accident_in_zone.empty:
                zone_id = accident_in_zone.iloc[0]['ZONE_UNIQUE_ID']

                # Filter heat events within the same boundary zone
                heat_in_zone = gpd.sjoin(
                    matched_heat_events, 
                    boundary_gdf, 
                    predicate='within', 
                    how='inner'
                )
                heat_in_same_zone = heat_in_zone[
                    heat_in_zone['ZONE_UNIQUE_ID'] == zone_id
                ]

                if not heat_in_same_zone.empty:
                    episode_ids = heat_in_same_zone['EPISODE_ID'] \
                        .astype(str).tolist()
                    accident_result[
                        f'Matched_Heat_EPISODE_IDs_{boundary_name}'
                    ] = ", ".join(episode_ids)
                else:
                    accident_result[
                        f'Matched_Heat_EPISODE_IDs_{boundary_name}'
                    ] = ""
            else:
                accident_result[
                    f'Matched_Heat_EPISODE_IDs_{boundary_name}'
                ] = ""
    else:
        for boundary_name in gdfs.keys():
            accident_result[
                f'Matched_Heat_EPISODE_IDs_{boundary_name}'
            ] = ""

    results_summary.append(accident_result)

# Save final output
final_df = pd.DataFrame(results_summary)
final_df.to_csv(
    r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
    r"\Verification\Buckling\Accidents_With_Heat_EventIDs_AllBoundaries.csv",
    index=False
)

# %%
# ! ################################################################################################
# ! Month # Title: Buckling Accident Verification with Heat/Extreme Heat Events Across Multiple Boundaries
# ! Purpose: Match railroad buckling accidents with heat/extreme heat events by date and location,
# !          verify spatial containment within multiple boundaries (NWS Forecast Zones, Climate Divisions,
# !          County Warning Areas, States, Climate Regions), and output matched CSV with EPISODE_IDs.
# ! Run Time: [Depends on data size, est. few minutes]
# ! ################################################################################################
# Add unique IDs for all boundary shapefiles
for boundary_name, boundary_gdf in gdfs.items():
    gdfs[boundary_name]['ZONE_UNIQUE_ID'] = gdfs[boundary_name].index + 1  # Adds 1,2,3...

results_summary = []

for idx, accident in accidents_gdf.iterrows():
    accident_result = accident.copy()

    # Extract accident year and month
    accident_year = accident['Accident_Date'].year
    accident_month = accident['Accident_Date'].month

    # Filter heat events where accident year-month falls between event's start and end year-month
    matched_heat_events = heat_gdf[
        ((heat_gdf['Begin_Date'].dt.year < accident_year) |
            (
                (heat_gdf['Begin_Date'].dt.year == accident_year) &
                (heat_gdf['Begin_Date'].dt.month <= accident_month)
            ))
        &
        ((heat_gdf['End_Date'].dt.year > accident_year) |
            (
                (heat_gdf['End_Date'].dt.year == accident_year) &
                (heat_gdf['End_Date'].dt.month >= accident_month)
            )
        )
    ]

    if not matched_heat_events.empty:
        for boundary_name, boundary_gdf in gdfs.items():
            # Check if accident is within this boundary
            accident_in_zone = gpd.sjoin(
                gpd.GeoDataFrame([accident], crs=accidents_gdf.crs),
                boundary_gdf,
                predicate='within',
                how='inner'
            )

            if not accident_in_zone.empty:
                zone_id = accident_in_zone.iloc[0]['ZONE_UNIQUE_ID']

                # Filter heat events within the same boundary zone
                heat_in_zone = gpd.sjoin(
                    matched_heat_events, 
                    boundary_gdf, 
                    predicate='within', 
                    how='inner'
                )
                heat_in_same_zone = heat_in_zone[
                    heat_in_zone['ZONE_UNIQUE_ID'] == zone_id
                ]

                if not heat_in_same_zone.empty:
                    episode_ids = heat_in_same_zone['EPISODE_ID'] \
                        .astype(str).tolist()
                    accident_result[
                        f'Matched_Heat_EPISODE_IDs_{boundary_name}'
                    ] = ", ".join(episode_ids)
                else:
                    accident_result[f'Matched_Heat_EPISODE_IDs_{boundary_name}'] = ""
            else:
                accident_result[f'Matched_Heat_EPISODE_IDs_{boundary_name}'] = ""
    else:
        for boundary_name in gdfs.keys():
            accident_result[f'Matched_Heat_EPISODE_IDs_{boundary_name}'] = ""

    results_summary.append(accident_result)

# Save final output
final_df = pd.DataFrame(results_summary)
final_df.to_csv(
    r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal"
    r"\Verification\Buckling\Accidents_With_Heat_EventIDs_AllBoundaries_month.csv",
    index=False
)

# %% Plotting the results

# File paths for day-based and month-based matching
day_fp = (r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose"
          r"\2025\New_Journal\Verification\Buckling"
          r"\Accidents_With_Heat_EventIDs_AllBoundaries.csv")
month_fp = (r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose"
            r"\2025\New_Journal\Verification\Buckling"
            r"\Accidents_With_Heat_EventIDs_AllBoundaries_month.csv")

# Load both datasets
df_day = pd.read_csv(day_fp)
df_month = pd.read_csv(month_fp)

# Boundary columns
boundary_cols = [
    col for col in df_day.columns
    if 'Matched_Heat_EPISODE_IDs_' in col
]

# Count matches for day and month
day_counts = df_day[boundary_cols].apply(
    lambda col: col.notna() & (col != ""), axis=0
).sum()
month_counts = df_month[boundary_cols].apply(
    lambda col: col.notna() & (col != ""), axis=0
).sum()

# Total accidents
total_accidents = len(df_day)

# Calculate percentages
day_percentages = (day_counts / total_accidents * 100).round(1)
month_percentages = (month_counts / total_accidents * 100).round(1)

# Plot
x = np.arange(len(boundary_cols))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
bars_day = ax.bar(
    x - width / 2, day_counts, width, label='Day Matching', color='skyblue'
)
bars_month = ax.bar(
    x + width / 2,
    month_counts,
    width,
    label='Month Matching',
    color='salmon'
)

# Increasing the top of the frame 10 percent of the maximum value of the y axis
ymax = max(day_counts.max(), month_counts.max()) * 1.1
# Set y-axis limit
ax.set_ylim(0, ymax)

# Labels & Title
ax.set_ylabel('Number of Matched Accidents')
ax.set_xlabel('Spatial Boundaries')
ax.set_title(
    ('Buckling Accident Matches Across Boundaries\n'
     '(Day Matching vs. Month Matching)')
)
ax.set_xticks(x)
xtick_labels = [
    col.replace('Matched_Heat_EPISODE_IDs_', '') for col in boundary_cols
]
ax.set_xticklabels(xtick_labels, rotation=45)
ax.legend()

# Add counts and percentages on bars
for bars, percentages in zip(
    [bars_day, bars_month],
    [day_percentages, month_percentages]
):
    for bar, pct in zip(bars, percentages):
        height = bar.get_height()
        ax.annotate(f'{int(height)} \n({pct}%)',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()


# %%
# ! ################################################################################################
# ! # Title: Buckling Accident Verification with NCEI Buckling Data and HUC Polygons 
# ! Purpose: Match railroad buckling accidents with NCEI flash/riverine buckling by date and location,
# !          check containment within HUC2-HUC12 polygons, output matched CSVs, and plot results.
# ! Run Time: [Depends on data size, est. few minutes]
# ! ################################################################################################

# Sample data for demonstration (since file access isn't possible here)
labels = ['NWS Forecast Zones', 'Climate Divisions', 'Warning Zones', 'States']
day_counts = np.array([15, 20, 21, 34])
month_counts = np.array([26, 34, 37, 66])
total_accidents = 131

day_percentages = (day_counts / total_accidents * 100).round(1)
month_percentages = (month_counts / total_accidents * 100).round(1)

# Circular plot
fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
theta = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)

width = 0.5

# Use the same one color for all bars
day_color = plt.cm.Blues(0.6)
month_color = plt.cm.Reds(0.6)

# Bars
bars_day = ax.bar(
    theta - width / 2,
    day_percentages,
    width=width,
    bottom=0,
    color=day_color,
    alpha=1,
    label='Day Matching'
)
bars_month = ax.bar(
    theta + width / 2,
    month_percentages,
    width=width,
    bottom=0,
    color=month_color,
    alpha=1,
    label='Month Matching'
)

# Radial gridlines
tick_values = [
    0, 20, 40, 60, 70
]
ax.set_ylim(0, 70)
ax.set_yticks(tick_values)
ax.set_yticklabels([])

# Style gridlines and outer circle
ax.yaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax.spines['polar'].set_visible(False)
outer_circle = plt.Circle(
    (0, 0), 70, transform=ax.transData._b, fill=False,
    linewidth=1, color='black'
)
ax.add_artist(outer_circle)

# Degree labels (0°, 60°, 120°, etc.)
degree_angles = np.round(np.degrees(theta)).astype(int)
# Set radial ticks at every 60°, but hide labels
# Set radial ticks at every bar center (theta), but hide labels
ax.set_xticks(theta)
ax.set_xticklabels([])

# Style the radial lines (spokes) as dashed and transparent
for line in ax.xaxis.get_gridlines():
    line.set_linestyle('--')     # Dashed line
    line.set_linewidth(0.5)      # Thinner line
    line.set_alpha(0.5)          # Transparency


# Annotate bars (counts and percentages)
for bar, count, pct in zip(bars_day, day_counts, day_percentages):
    angle = bar.get_x() + bar.get_width()/2
    radius = bar.get_height() + 5
    ax.text(
        angle, radius, f"{count}\n({pct}%)", 
        ha='center', va='center', fontsize=8, color='black'
    )

for bar, count, pct in zip(bars_month, month_counts, month_percentages):
    angle = bar.get_x() + bar.get_width()/2
    radius = bar.get_height() + 5
    ax.text(
        angle, radius, f"{count}\n({pct}%)", 
        ha='center', va='center', fontsize=8, color='black'
    )

# Example radial positions (fill these in based on your input)
label_radial_positions = [40, 37, 45, 55]  # This comes from you!

# Add category names inside the circle with lines
for angle, label, radial_pos in zip(theta, labels, label_radial_positions):
    ax.text(
        angle, radial_pos, label,
        ha='center', va='center',
        fontsize=9, color='black'
    )
    ax.plot(
        [angle, angle],
        [0, radial_pos - 5],
        color='gray',
        linewidth=0.8,
        linestyle='-'  # Line length just below label
    )

# make the title of the legend bold
ax.legend(
    title='Matching Method',
    title_fontsize='12',
    loc='upper right',
    bbox_to_anchor=(0.65, 0.97),
    fontsize=9,
    frameon=True,
    ncol=1
)

plt.tight_layout()

# saving the 400 dpi image in the same directory as the script
save_fp = (r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose"
           r"\2025\New_Journal\Verification\Buckling"
           r"\buckling_verification.png")
plt.savefig(save_fp, dpi=400, bbox_inches='tight', transparent=False)

plt.show()

# %%
