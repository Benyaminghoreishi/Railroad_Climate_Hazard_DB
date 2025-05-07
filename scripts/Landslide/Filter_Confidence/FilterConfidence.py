# %%
# ! ################################################################################################
# ! # Title: Filter and Extract Date Information for Point-Based U.S. Landslide Records (2000–2024)
# ! Purpose: Convert `Date_Min` into year, month, day columns and filter records from 2000 onward.
# ! Run Time: [~5 sec]
# ! ################################################################################################

# import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import matplotlib.pyplot as plt
import os

# %%
# Load the CSV
point_path = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_csv\\"
    "us_ls_v3_point.csv"
)
df_point = pd.read_csv(point_path)

# Convert Date_Min to datetime
df_point['Date_Min'] = pd.to_datetime(df_point['Date_Min'], errors='coerce')

# Total rows
total_point = len(df_point)

# Rows with valid dates
valid_date_point = df_point['Date_Min'].notna().sum()

# Filter for dates from 2000 to 2024
filtered_point = df_point[(df_point['Date_Min'].dt.year >= 2000) & (df_point['Date_Min'].dt.year <= 2024)]
count_filtered_point = len(filtered_point)

# Extract year, month, day
filtered_point['Year_Min'] = filtered_point['Date_Min'].dt.year
filtered_point['Month_Min'] = filtered_point['Date_Min'].dt.month
filtered_point['Day_Min'] = filtered_point['Date_Min'].dt.day

# Print summary
print(f"Point File Summary:")
print(f"Total rows: {total_point}")
print(f"Rows with valid dates: {valid_date_point}")
print(f"Rows with dates from 2000 to 2024: {count_filtered_point}")

# Save to CSV
output_path = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_csv\\"
    "us_ls_v3_point_with_dates_2000_2024.csv"
)
filtered_point.to_csv(output_path, index=False)

print("Year, month, and day columns added and file saved successfully!")

df_point = pd.read_csv(output_path)

# Convert to GeoDataFrame using Lon_W and Lat_N
geometry = [Point(xy) for xy in zip(df_point['Lon_W'], df_point['Lat_N'])]
gdf_point = gpd.GeoDataFrame(df_point, geometry=geometry, crs="EPSG:4326")

# Save as GeoPackage
output_gpkg_point = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_csv\\"
    "us_ls_v3_point_with_dates_2000_2024.gpkg"
)
gdf_point.to_file(output_gpkg_point, layer='point_landslides', driver='GPKG')
print("Point-based GeoPackage saved successfully!")
# %%
# ! ################################################################################################
# ! # Title: Filter and Extract Date Information for Polygon-Based U.S. Landslide Records (2000–2024)
# ! Purpose: Convert `Date_Min` into year, month, day columns and filter records from 2000 onward.
# ! Run Time: [~5 sec]
# ! ################################################################################################


# Load the CSV
poly_path = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_csv\\"
    "us_ls_v3_poly.csv"
)
df_poly = pd.read_csv(poly_path)

# Convert Date_Min to datetime
df_poly['Date_Min'] = pd.to_datetime(df_poly['Date_Min'], errors='coerce')

# Total rows
total_poly = len(df_poly)

# Rows with valid dates
valid_date_poly = df_poly['Date_Min'].notna().sum()

# Filter for dates from 2000 to 2024
filtered_poly = df_poly[
    (df_poly['Date_Min'].dt.year >= 2000) & 
    (df_poly['Date_Min'].dt.year <= 2024)
]
count_filtered_poly = len(filtered_poly)

# Extract year, month, day
filtered_poly['Year_Min'] = filtered_poly['Date_Min'].dt.year
filtered_poly['Month_Min'] = filtered_poly['Date_Min'].dt.month
filtered_poly['Day_Min'] = filtered_poly['Date_Min'].dt.day

# Print summary
print("Polygon File Summary:")
print(f"Total rows: {total_poly}")
print(f"Rows with valid dates: {valid_date_poly}")
print(f"Rows with dates from 2000 to 2024: {count_filtered_poly}")

# Save to CSV
output_path = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_csv\\"
    "us_ls_v3_poly_with_dates_2000_2024.csv"
)
filtered_poly.to_csv(output_path, index=False)

print("Year, month, and day columns added and file saved successfully!")

# Load the original polygon shapefile
shp_path = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_shp\\"
    "us_ls_v3_poly.shp"
)
gdf_all = gpd.read_file(shp_path)

# Check and align key column (assumed to be 'USGS_ID')
common_id_col = "USGS_ID"

# Filter original shapefile to match the filtered IDs
gdf_matched = gdf_all[gdf_all[common_id_col].isin(filtered_poly[common_id_col])]

# Optional: merge additional columns (like year, month, day)
gdf_matched = gdf_matched.merge(
    filtered_poly[[common_id_col, 'Year_Min', 'Month_Min', 'Day_Min']],
    on=common_id_col,
    how='left'
)

# Drop reserved field names if needed (e.g., 'fid' or 'FID')
reserved_cols = ['fid', 'FID']
for col in reserved_cols:
    if col in gdf_matched.columns:
        gdf_matched = gdf_matched.drop(columns=col)

# Save to GeoPackage
output_gpkg = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_csv\\"
    "us_ls_v3_poly_with_dates_2000_2024.gpkg"
)
gdf_matched.to_file(output_gpkg, layer='polygon_landslides', driver='GPKG')

print("Filtered polygon-based GeoPackage saved successfully!")

# %%
# ! ################################################################################################
# ! # Title: Compare Confidence Level Distribution (All vs 2000–2024) for Landslide Records
# ! Purpose: Visualize and compare the distribution of confidence levels in both point and polygon
# !          datasets for all records and those from the year 2000 to 2024.
# ! Run Time: [~10 seconds]
# ! ################################################################################################

# Load datasets
point_all_path = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_csv\\"
    "us_ls_v3_point.csv"
)
point_filtered_path = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_csv\\"
    "us_ls_v3_point_with_dates_2000_2024.csv"
)
poly_all_path = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_csv\\"
    "us_ls_v3_poly.csv"
)
poly_filtered_path = (
    "C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\"
    "1_Rail_Project\\7_Landslide\\Data\\Ver.3.0.Feb2025\\US_Landslide_v3_csv\\"
    "us_ls_v3_poly_with_dates_2000_2024.csv"
)

# Load data
point_all = pd.read_csv(point_all_path)
point_filtered = pd.read_csv(point_filtered_path)
poly_all = pd.read_csv(poly_all_path)
poly_filtered = pd.read_csv(poly_filtered_path)

# Count confidence levels


def get_confidence_counts(df):
    return df['Confidence'].value_counts().sort_index()


point_all_counts = get_confidence_counts(point_all)
point_filtered_counts = get_confidence_counts(point_filtered)
poly_all_counts = get_confidence_counts(poly_all)
poly_filtered_counts = get_confidence_counts(poly_filtered)

# Plot function with total counts and percentages


def plot_confidence_comparison(counts_all, counts_filtered, color_all, color_filtered, label):
    all_levels = sorted(set(counts_all.index).union(set(counts_filtered.index)))
    counts_all = counts_all.reindex(all_levels, fill_value=0)
    counts_filtered = counts_filtered.reindex(all_levels, fill_value=0)

    x = range(len(all_levels))
    width = 0.35

    total_all = counts_all.sum()
    total_filtered = counts_filtered.sum()

    plt.figure(figsize=(10, 5))
    bars_all = plt.bar(
        [i - width / 2 for i in x],
        counts_all.values,
        width=width,
        label=f'All Data = {total_all}',
        color=color_all
    )
    bars_filtered = plt.bar(
        [i + width / 2 for i in x],
        counts_filtered.values,
        width=width,
        label=f'2000–2024 = {total_filtered}',
        color=color_filtered
    )

    # Add labels on top
    for i, (a, f) in enumerate(zip(counts_all.values, counts_filtered.values)):
        pct_all = (a / total_all) * 100 if total_all else 0
        pct_filt = (f / total_filtered) * 100 if total_filtered else 0
        y_pos_all = a + max(counts_all.values.max(), counts_filtered.values.max()) * 0.01
        plt.text(i - width / 2, y_pos_all, f"{a}\n ({pct_all:.1f}%)",
                 ha='center', fontsize=10)
        y_pos_filt = f + max(counts_all.values.max(), counts_filtered.values.max()) * 0.01
        plt.text(i + width / 2, y_pos_filt, 
                 f"{f}\n ({pct_filt:.1f}%)", ha='center', fontsize=10)

    plt.xticks(ticks=x, labels=[str(i) for i in all_levels], fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel("Confidence Level", fontsize=14)
    plt.ylabel("Frequency", fontsize=14)
    plt.legend(fontsize=12)
    plt.tight_layout()
    # increase the top frame 1.1 times of the max y value
    plt.ylim(0, max(counts_all.values.max(), counts_filtered.values.max()) * 1.1)
    if "point" in label.lower():
        plt.savefig("Confidence_Points_rev03.png", dpi=400, bbox_inches='tight')
    elif "poly" in label.lower():
        plt.savefig("Confidence_Polygon_rev03.png", dpi=400, bbox_inches='tight')


# Plot for points and polygons
plot_confidence_comparison(
    point_all_counts,
    point_filtered_counts,
    "#1a80bb",
    "#F37142",
    label="point"
)
plot_confidence_comparison(
    poly_all_counts,
    poly_filtered_counts,
    "#1a80bb",
    "#F37142",
    label="poly"
)


# %%
# Print the base directory
base_directory = os.path.dirname(os.path.abspath(__file__))
print(f"Base Directory: {base_directory}")
# %%
