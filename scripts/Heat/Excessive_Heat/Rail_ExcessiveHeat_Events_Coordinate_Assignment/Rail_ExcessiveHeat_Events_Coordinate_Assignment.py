# %%
# TODO: Assigning the NCEI Heat Events to the US Railway Network  
########################################
# ! 1_Importing the necessary libraries
########################################
import pandas as pd
import geopandas as gpd
import os

# %% Set base directory
base_dir = os.path.abspath(os.path.join("..", ".."))

# File paths
csv_path = os.path.join(base_dir, "5_Sunkink", "NWS Forecast Zone", "Excessive Heat", "Excessive Heat.csv")
NWS_path = os.path.join(base_dir, "5_Sunkink", "NWS Forecast Zone", "NWS_Forcat_Zone", "z_18mr25.shp")

# Load data
ncei_df = pd.read_csv(csv_path)
nws_gdf = gpd.read_file(NWS_path)

# Step 1: Create FIPS dictionary
fips_dict = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08",
    "CT": "09", "DE": "10", "DC": "11", "FL": "12", "GA": "13", "HI": "15",
    "ID": "16", "IL": "17", "IN": "18", "IA": "19", "KS": "20", "KY": "21",
    "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27",
    "MS": "28", "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33",
    "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
    "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45", "SD": "46",
    "TN": "47", "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53",
    "WV": "54", "WI": "55", "WY": "56"
}

# Step 2: Format and build FIPS_5 in NCEI data
ncei_df['STATE_FIPS'] = ncei_df['STATE_FIPS'].astype(float).astype(int).astype(str).str.zfill(2)
ncei_df['CZ_FIPS'] = ncei_df['CZ_FIPS'].astype(float).astype(int).astype(str).str.zfill(3)
ncei_df['FIPS_5'] = ncei_df['STATE_FIPS'] + ncei_df['CZ_FIPS']

# Step 3: Format and build FIPS_5 in NWS shapefile
nws_gdf['STATE'] = nws_gdf['STATE_ZONE'].str[:2]
nws_gdf['ZONE'] = nws_gdf['STATE_ZONE'].str[2:].str.zfill(3)
nws_gdf['STATE_FIPS'] = nws_gdf['STATE'].map(fips_dict)
nws_gdf['FIPS_5'] = nws_gdf['STATE_FIPS'] + nws_gdf['ZONE']

# Step 4: Convert geometry to lat/lon (for polygon shapefile, use centroids)
nws_gdf = nws_gdf.to_crs(epsg=4326)
nws_gdf['geometry_centroid'] = nws_gdf.geometry.centroid
nws_gdf['LAT'] = nws_gdf['geometry_centroid'].y
nws_gdf['LON'] = nws_gdf['geometry_centroid'].x


# Step 5: Merge NCEI with coordinates from matching NWS forecast zones
ncei_df = ncei_df.merge(nws_gdf[['FIPS_5', 'LAT', 'LON']], on='FIPS_5', how='left')

# Remove rows with NaN or zero in LAT or LON
ncei_df = ncei_df.dropna(subset=['LAT', 'LON'])
ncei_df = ncei_df[(ncei_df['LAT'] != 0) & (ncei_df['LON'] != 0)]

# Step 6: Save the result
output_path = os.path.join(base_dir, "5_Sunkink", "NWS Forecast Zone", "Excessive Heat", "Excessive_heat_with_coords.csv")
ncei_df.to_csv(output_path, index=False)

# %%
