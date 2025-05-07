#%%
# TODO: Landslide
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Read the shapefile into a GeoDataFrame
rail_line_path = (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project"
    r"\Shapefiles\North_American_Rail_Network_Lines\North_American_Rail_Network_Lines.shp")
rail_line_gdf = gpd.read_file(rail_line_path)

# Buffer distances
distances = [15, 50, 100]

# Buffer styles
buffer_kwargs = {
    'cap_style': 2,  # flat cap style
    'join_style': 2,  # miter join style
    'mitre_limit': 3  # miter limit
}

# Create buffers and save them as new shapefiles
for distance in distances:
    buffered_geom = rail_line_gdf.buffer(distance, **buffer_kwargs)
    buffered_gdf = gpd.GeoDataFrame(rail_line_gdf.copy(), geometry=buffered_geom, crs=rail_line_gdf.crs)
    
    output_path = f"C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\1_Rail_Project\\7_Landslide\\Code_Assigning_to_Railway\\Rail_line_buffer_{distance}m.shp"
    buffered_gdf.to_file(output_path)
    print(f"Buffer of {distance} meters saved to {output_path}")

print("Done1 with buffering!")

#%%
# Load your shapefile
# gdf_15 = gpd.read_file(r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\7_Landslide" 
#                     r"\Code_Assigning_to_Railway\Rail_line_buffer_15m.shp")

# # Perform intersection to get the intersected areas
# intersected = gdf_15.overlay(gdf_15, how='intersection')

# # Remove original polygons if needed
# Exploaded = gdf_15.overlay(intersected, how='difference')

# # Save the resulting intersected polygons to a new shapefile
# intersected.to_file(r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\7_Landslide" 
#                     r"\Code_Assigning_to_Railway\Intersected_Rail_line_buffer_15m.shp")

# # Optionally, save the difference (non-intersected parts)
# Exploaded.to_file(r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\7_Landslide" 
#                     r"\Code_Assigning_to_Railway\Exploaded_Rail_line_buffer_15m.shp")


#%%
import geopandas as gpd
import pandas as pd

# Define the path to the shapefile
Landslide_path = r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\7_Landslide\Data\US_Landslide_2 (1)\US_Landslide_2\US_Landslide_2shp\us_ls_2_points.shp"

# Read the shapefile
LandslidePoint_gdf = gpd.read_file(Landslide_path)

# Convert the GeoDataFrame to a DataFrame
LandslidePoint_df = pd.DataFrame(LandslidePoint_gdf)

# Define the output path
output_path = r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\7_Landslide\Code_Assigning_to_Railway\LandslidePoint2.csv"

# Save the DataFrame as a CSV file
LandslidePoint_df.to_csv(output_path, index=False)

#%% 
import geopandas as gpd

# Load your shapefiles
gdf_list = {
    '15m': gpd.read_file(r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\7_Landslide\Code_Assigning_to_Railway\Rail_line_buffer_15m.shp"),
    '50m': gpd.read_file(r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\7_Landslide\Code_Assigning_to_Railway\Rail_line_buffer_50m.shp"),
    '100m': gpd.read_file(r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\7_Landslide\Code_Assigning_to_Railway\Rail_line_buffer_100m.shp")
}

Landslide_path = (r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\7_Landslide\Data\US_Landslide_2 (1)\US_Landslide_2\US_Landslide_2shp\us_ls_2_points.shp")
LandslidePoint_gdf = gpd.read_file(Landslide_path)

# Ensure the 'Date' column is in datetime format
LandslidePoint_gdf['Date'] = pd.to_datetime(LandslidePoint_gdf['Date'], errors='coerce')

# Filter the GeoDataFrame for dates between 2000 and 2024
filtered_LandslidePoint_gdf = LandslidePoint_gdf[(LandslidePoint_gdf['Date'] >= '2000-01-01') & (LandslidePoint_gdf['Date'] <= '2024-12-31')]

# Filter out rows without coordinates
LandslidePoint_gdf = LandslidePoint_gdf.dropna(subset=['geometry'])
print("Done with Loading Dataset!")

# Set CRS and reproject Landslide_gdf to match each GeoDataFrame's CRS
for key, gdf in gdf_list.items():
    LandslidePoint_gdf = LandslidePoint_gdf.set_crs(LandslidePoint_gdf.crs, allow_override=True)
    LandslidePoint_gdf_reprojected = LandslidePoint_gdf.to_crs(gdf.crs)

    # Perform a spatial join to retain all attributes
    point_in_poly = gpd.sjoin(LandslidePoint_gdf_reprojected, gdf, how='left', op='within')

    # Collect EVENT_IDs for each polygon
    polygon_event_ids = point_in_poly.groupby('index_right')['OBJECTID_left'].apply(lambda x: ','.join(x.astype(str)))

    # Count points in each polygon
    Num_Landslide = point_in_poly.groupby('index_right').size()

    # Add the frequency counts back to the GeoDataFrame
    gdf['OBJECTID_P'] = gdf.index.map(polygon_event_ids).fillna('')
    gdf['Num_Landslide'] = gdf.index.map(Num_Landslide).fillna(0)

    # Save the result to a new shapefile
    output_path = (f"C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\1_Rail_Project\\7_Landslide\\Code_Assigning_to_Railway\\Rail_{key}_Buffer_with_Slide_ObjectID.shp")
    gdf.to_file(output_path)

    print(f"Done with Saving Buffered Files with New Attributes for {key}!")

# %%
# Load the polyline shapefile
Rail_line_gdf = gpd.read_file(r"C:\Users\ghoreisb\Box\Oregon State University\0000- Research_OSU\1_Rail_Project\Shapefiles\North_American_Rail_Network_Lines\North_American_Rail_Network_Lines.shp")

# Ensure the Rail Line GeoDataFrame is in the same CRS as each buffer GeoDataFrame
for key, gdf in gdf_list.items():
    if Rail_line_gdf.crs != gdf.crs:
        Rail_line_gdf = Rail_line_gdf.to_crs(gdf.crs)

# Perform the intersection for each buffer GeoDataFrame
for key, gdf in gdf_list.items():
    intersection_landslide_Rail = gpd.overlay(Rail_line_gdf, gdf, how='intersection')

    # Reproject to Albers Equal Area
    albers_crs = "EPSG:5070"  # Albers Equal Area for the contiguous United States
    intersection_landslide_Rail_albers = intersection_landslide_Rail.to_crs(albers_crs)

    # Calculate the length of each line in meters
    intersection_landslide_Rail_albers['Length_Meters'] = intersection_landslide_Rail_albers.geometry.length

    # Convert the length from meters to feet and miles
    intersection_landslide_Rail_albers['Length_Feet'] = intersection_landslide_Rail_albers['Length_Meters'] * 3.28084
    intersection_landslide_Rail_albers['Length_Miles'] = intersection_landslide_Rail_albers['Length_Meters'] * 0.000621371

    # Save the result back to a new shapefile
    output_shapefile = (f"C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\1_Rail_Project\\7_Landslide\\Code_Assigning_to_Railway\\Rail_{key}_Buffer_with_Slide_Intersect.shp")
    intersection_landslide_Rail_albers.to_file(output_shapefile)

    # Save the result to a CSV file
    output_csv = (f"C:\\Users\\ghoreisb\\Box\\Oregon State University\\0000- Research_OSU\\1_Rail_Project\\7_Landslide\\Code_Assigning_to_Railway\\Rail_{key}_Buffer_with_Slide_Intersect.csv")
    intersection_landslide_Rail_albers.to_csv(output_csv, index=False)

    print(f"Done with {key} buffer file!")

