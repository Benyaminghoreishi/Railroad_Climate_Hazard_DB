# %%
# ! ----------------------------------------------------------------------------------------
# ! Title: Stacked Bar Chart of U.S. Billion-Dollar Weather and Climate Disasters (1990–2024)
# ! ----------------------------------------------------------------------------------------

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Get the current script's directory and load the file
directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(directory, "time-series-US-cost-1980-2024.csv")

df = pd.read_csv(file_path, skiprows=3)

# Clean column names
df.columns = df.columns.str.strip()

# Filter relevant columns
disaster_types = [
    'Drought Count', 'Flooding Count', 'Freeze Count', 'Severe Storm Count',
    'Tropical Cyclone Count', 'Wildfire Count', 'Winter Storm Count'
]
df_filtered = df[['Year'] + disaster_types].dropna()

# Convert 'Year' to int and filter for years >= 1990
df_filtered['Year'] = df_filtered['Year'].astype(int)
df_filtered = df_filtered[df_filtered['Year'] >= 1990].reset_index(drop=True)

# Define standard disaster colors
disaster_colors = {
    'Drought Count': '#F0E442',         # Orange
    'Flooding Count': '#56B4E9',        # Blue
    'Freeze Count': '#009E73',          # Green
    'Severe Storm Count': '#0072B2',    # Dark Blue
    'Tropical Cyclone Count': '#D55E00',# Red
    'Wildfire Count': '#CC79A7',        # Pink
    'Winter Storm Count': '#E69F00'     # Yellow
}

# Plot stacked bar chart
fig, ax = plt.subplots(figsize=(12, 6))
df_filtered.set_index('Year').plot(
    kind='bar', stacked=True, ax=ax, width=0.8, color=[disaster_colors[col] for col in disaster_types]
)

# Formatting
plt.xlabel("Year", fontsize=20)
plt.ylabel("Number of Disasters", fontsize=20)
plt.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True, fontsize=20)

# Show xticks every 2 years
xtick_positions = range(0, len(df_filtered), 2)
ax.set_xticks(xtick_positions)
ax.set_xticklabels(df_filtered['Year'].iloc[xtick_positions], rotation=45, fontsize=20)

plt.yticks(rotation=0, fontsize=20)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Save the plot at 720 dpi
output_path = os.path.join(directory, "disaster.png")
plt.tight_layout()
plt.savefig(output_path, dpi=720)

# Show the plot
plt.show()

# %%
# ! --------------------------------------------------------------------------------------------------
# ! Title: Stacked Bar Chart of U.S. Rail Equipment Accidents by Environmental Causes (2000–2024)
# ! --------------------------------------------------------------------------------------------------

# Get the current script's directory and load the file
directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(directory, "Rail_Equipment_Accident_Incident_Data__Form_54__20250225.csv")
df = pd.read_csv(file_path)

# Clean column names (remove whitespace if needed)
df.columns = df.columns.str.strip()

# Keep only the required columns
df_filtered = df[['Year', 'Accident Cause Code']].dropna()

# Convert 'Year' to integer and filter for years 2000-2024
df_filtered['Year'] = df_filtered['Year'].astype(int)
df_filtered = df_filtered[(df_filtered['Year'] >= 2000) & (df_filtered['Year'] <= 2024)]

# List of allowed accident cause codes from the image
allowed_codes = ['T001', 'T002', 'T109', 'M101', 'M102', 'M103', 'M104', 'M105', 'M199']

# Filter dataset to keep only allowed codes
df_filtered = df_filtered[df_filtered['Accident Cause Code'].isin(allowed_codes)]

# Extract numeric part of 'Accident Cause Code' for visualization
df_filtered['Accident Cause Code'] = df_filtered['Accident Cause Code'].str.extract('(\d+)')

# Convert extracted codes to integer
df_filtered['Accident Cause Code'] = df_filtered['Accident Cause Code'].astype(int)

# Map numeric codes to their full descriptions
cause_descriptions = {
    1: "T001: Roadbed settled or soft",
    2: "T002: Washout/rain/slide/flood/snow/ice damage",
    109: "T109: Track alignment irregular (buckled/sunkink)",
    101: "M101: Snow, ice, mud, gravel, coal, sand, etc. on track",
    102: "M102: Extreme environmental condition – tornado",
    103: "M103: Extreme environmental condition – flood",
    104: "M104: Extreme environmental condition – dense fog",
    105: "M105: Extreme environmental condition – extreme wind velocity",
    199: "M199: Other extreme environmental conditions"
}

# Replace codes with full descriptions
df_filtered['Accident Cause Code'] = df_filtered['Accident Cause Code'].map(cause_descriptions)

# Remove NaN values (cases not in mapping)
df_filtered = df_filtered.dropna()

# Count occurrences of each accident cause per year
df_pivot = df_filtered.pivot_table(index='Year', columns='Accident Cause Code', aggfunc='size', fill_value=0)

# Define a color mapping with a visually distinct color palette
cause_colors = {
    "T001: Roadbed settled or soft": "#b2df8a",  # Light green
    "T002: Washout/rain/slide/flood/snow/ice damage": "#1f78b4",  # Strong blue
    "T109: Track alignment irregular (buckled/sunkink)": "#ff7f00",  # Orange
    "M101: Snow, ice, mud, gravel, coal, sand, etc. on track": "#33a02c",  # Green
    "M102: Extreme environmental condition – tornado": "#e31a1c",  # Red
    "M103: Extreme environmental condition – flood": "#6a3d9a",  # Purple
    "M104: Extreme environmental condition – dense fog": "#b15928",  # Brown
    "M105: Extreme environmental condition – extreme wind velocity": "#fb9a99",  # Light red
    "M199: Other extreme environmental conditions": "#a6cee3"  # Light blue
}

# Plot stacked bar chart with improved styling
fig, ax = plt.subplots(figsize=(14, 7))
df_pivot.plot(kind='bar', stacked=True, ax=ax, color=[cause_colors[col] for col in df_pivot.columns], width=0.85)

# Formatting
plt.xlabel("Year", fontsize=22)
plt.ylabel("Number of Accidents", fontsize=20)
plt.xticks(rotation=45, fontsize=20)
plt.yticks(fontsize=20)

# Increase y-axis limit to 160
ax.set_ylim(0, 250)
xtick_positions = range(0, len(df_pivot), 2)
ax.set_xticks(xtick_positions)
# Move legend inside and adjust layout
ax.legend(fontsize=13, loc="upper left", bbox_to_anchor=(0.44, 0.99))  # Adjusted legend placement

plt.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout to add space for the legend
plt.subplots_adjust(top=0.85)  # Expands the top margin

# Show the plot
plt.tight_layout()

# Save the plot at 720 dpi
output_path = os.path.join(directory, "weather_accidents.png")
plt.tight_layout()
plt.savefig(output_path, dpi=720)

# Show the plot
plt.show()
# %%
# ! --------------------------------------------------------------------------------------------------
# ! Title: U.S. Rail Equipment Accidents Involving Flood, Washout, and Track Buckling (2000–2024)
# ! --------------------------------------------------------------------------------------------------

# Get the current script's directory and load the file
directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(directory, "Rail_Equipment_Accident_Incident_Data__Form_54__20250225.csv")
df = pd.read_csv(file_path)

# Clean column names (remove whitespace if needed)
df.columns = df.columns.str.strip()

# Keep only the required columns
df_filtered = df[['Year', 'Accident Cause Code']].dropna()

# Convert 'Year' to integer and filter for years 2000-2024
df_filtered['Year'] = df_filtered['Year'].astype(int)
df_filtered = df_filtered[(df_filtered['Year'] >= 2000) & (df_filtered['Year'] <= 2024)]

# List of allowed accident cause codes from the image
allowed_codes = ['T002', 'T109', 'M101', 'M102', 'M103', 'M104', 'M105', 'M199']

# Filter dataset to keep only allowed codes
df_filtered = df_filtered[df_filtered['Accident Cause Code'].isin(allowed_codes)]

# Extract numeric part of 'Accident Cause Code' for visualization
df_filtered['Accident Cause Code'] = df_filtered['Accident Cause Code'].str.extract('(\d+)')

# Convert extracted codes to integer
df_filtered['Accident Cause Code'] = df_filtered['Accident Cause Code'].astype(int)

# Map numeric codes to their full descriptions
cause_descriptions = {
    2: "T002: Washout/rain/slide/flood/snow/ice damage",
    109: "T109: Track alignment irregular (buckled/sunkink)",
    103: "M103: Extreme environmental condition – flood",
}

# Replace codes with full descriptions
df_filtered['Accident Cause Code'] = df_filtered['Accident Cause Code'].map(cause_descriptions)

# Remove NaN values (cases not in mapping)
df_filtered = df_filtered.dropna()

# Count occurrences of each accident cause per year
df_pivot = df_filtered.pivot_table(index='Year', columns='Accident Cause Code', aggfunc='size', fill_value=0)

# Define a color mapping with a visually distinct color palette
cause_colors = {
    "T002: Washout/rain/slide/flood/snow/ice damage": '#1a80bb',  # blue
    "T109: Track alignment irregular (buckled/sunkink)": '#b3cde0',     # light blue
    "M103: Extreme environmental condition – flood": '#FFB84F'        # yellow-orange
}

# Plot stacked bar chart with improved styling
fig, ax = plt.subplots(figsize=(6.8, 3.5))
df_pivot.plot(kind='bar', stacked=True, ax=ax, color=[cause_colors[col] for col in df_pivot.columns], width=0.85)

# Formatting
plt.xlabel("Year", fontsize=13)
plt.ylabel("Number of Accidents", fontsize=13)
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)

# Increase y-axis limit to 160
ax.set_ylim(0, 80)
xtick_positions = range(0, len(df_pivot), 2)
ax.set_xticks(xtick_positions)
# Move legend inside and adjust layout
ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(0.44, 0.99))  # Adjusted legend placement

plt.grid(axis='y', linestyle='--', alpha=0.2)

# Adjust layout to add space for the legend
plt.subplots_adjust(top=0.85)  # Expands the top margin

# Show the plot
plt.tight_layout()

# Save the plot at 720 dpi
output_path = os.path.join(directory, "three_codes.png")
plt.tight_layout()
plt.savefig(output_path, dpi=400)

# Show the plot
plt.show()
# %%
# ! --------------------------------------------------------------------------------------------------
# ! Title: Summary of Rail Accident Causes with Derailment and Track Type Breakdown
# ! --------------------------------------------------------------------------------------------------

# Set the correct file path as a raw string
file_path = r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal\Codes\Filtered.xlsx"

# Read the Excel file
df = pd.read_excel(file_path)

# Make sure all relevant columns exist
required_cols = ['Accident Cause Code', 'Accident Type', 'Joint Track Type']
df = df[[col for col in required_cols if col in df.columns]]

# Get unique cause codes
cause_codes = df['Accident Cause Code'].dropna().unique()

# Prepare summary list
summary = []

for code in cause_codes:
    subset = df[df['Accident Cause Code'] == code]
    total = len(subset)

    derailments = subset[subset['Accident Type'].str.lower().str.contains('derailment', na=False)]
    other = total - len(derailments)

    main_track = subset[subset['Joint Track Type'].str.lower().str.contains('main', na=False)]
    yard = subset[subset['Joint Track Type'].str.lower().str.contains('yard', na=False)]

    derail_main = len(main_track[main_track['Accident Type'].str.lower().str.contains('derailment', na=False)])
    derail_yard = len(yard[yard['Accident Type'].str.lower().str.contains('derailment', na=False)])

    pct_derail = round(len(derailments) / total * 100, 1) if total > 0 else 0

    summary.append({
        "Code": code,
        "Total Events": total,
        "Derailments": len(derailments),
        "Derailment %": pct_derail,
        "Other Accidents": other,
        "Main Track Events": len(main_track),
        "Derailments on Main Track": derail_main,
        "Yard Events": len(yard),
        "Derailments in Yard": derail_yard
    })

summary_df = pd.DataFrame(summary)

# Save the summary to an Excel file in the same directory
output_path = r"C:\Users\ghoreisb\Box\Oregon State University\000- Papers\Publish Purpose\2025\New_Journal\Codes\Accident_Summary.xlsx"
summary_df.to_excel(output_path, index=False)

print(f"Summary saved to: {output_path}")

# %%
# ! -----------------------------------------------------------------------------------------------------
# ! Title: Comparison of Total Events, Derailments, and Track Location by FRA Weather-Related Cause Codes
# ! -----------------------------------------------------------------------------------------------------

# Data setup
codes = ['T001', 'T002', 'T109', 'M199', 'M105', 'M103', 'M102', 'M101']
total_events = [567, 153, 616, 104, 448, 177, 70, 668]
total_derailments = [553, 135, 609, 40, 257, 101, 48, 557]
main_track = [245, 122, 515, 56, 221, 86, 35, 210]
yard = [221, 19, 61, 42, 190, 63, 20, 243]
main_derailments = [234, 107, 513, 21, 169, 75, 29, 127]
yard_derailments = [218, 17, 57, 15, 62, 17, 8, 221]

# Color map
colors = {
    'Total Events': '#4B4B4B',               # Dark Gray
    'Derailments': '#A9A9A9',                # Light Gray
    'Main Track': '#2CA02C',                 # Green
    'Yard': '#1F77B4',                       # Blue
    'Main Track Derailments': '#98DF8A',     # Light Green
    'Yard Derailments': '#AEC7E8'            # Light Blue
}

# Plot setup
x = np.arange(len(codes))
width = 0.18
fig, ax = plt.subplots(figsize=(6.8, 3.5))

# Plot bars
ax.bar(x - 1.5*width, total_events, width, label='Total Events', color=colors['Total Events'])
ax.bar(x - 0.5*width, total_derailments, width, label='Derailments', color=colors['Derailments'])
ax.bar(x + 0.5*width, main_track, width, label='Main Track', color=colors['Main Track'])
ax.bar(x + 0.5*width, yard, width, bottom=main_track, label='Yard', color=colors['Yard'])
ax.bar(x + 1.5*width, main_derailments, width, label='Main Track Derailments', color=colors['Main Track Derailments'])
ax.bar(x + 1.5*width, yard_derailments, width, bottom=main_derailments, label='Yard Derailments', color=colors['Yard Derailments'])

# Add value labels
# for i in range(len(x)):
#     # Total Events
#     ax.text(x[i] - 1.5*width, total_events[i] + 5, str(total_events[i]), ha='center', va='bottom', fontsize=10)   
#     # Derailments
#     ax.text(x[i] - 0.5*width, total_derailments[i] + 5, str(total_derailments[i]), ha='center', va='bottom', fontsize=10)
#     # Main Track
#     ax.text(x[i] + 0.5*width, main_track[i] / 2, str(main_track[i]), ha='center', va='center', fontsize=10, color='white')
#     # Yard
#     ax.text(x[i] + 0.5*width, main_track[i] + yard[i] / 2, str(yard[i]), ha='center', va='center', fontsize=10, color='white')
#     # Total of Main + Yard
#     main_yard_total = main_track[i] + yard[i]
#     ax.text(x[i] + 0.5*width, main_yard_total + 5, str(main_yard_total), ha='center', va='bottom', fontsize=10)
#     # Main Track Derailments
#     ax.text(x[i] + 1.5*width, main_derailments[i] / 2, str(main_derailments[i]), ha='center', va='center', fontsize=10)
#     # Yard Derailments
#     ax.text(x[i] + 1.5*width, main_derailments[i] + yard_derailments[i] / 2, str(yard_derailments[i]), ha='center', va='center', fontsize=10)
#     # Total Derailments stacked
#     total_derail = main_derailments[i] + yard_derailments[i]
#     ax.text(x[i] + 1.5*width, total_derail + 5, str(total_derail), ha='center', va='bottom', fontsize=10)
# Labels and formatting
ax.set_ylabel('Reported Event Frequency', fontsize=13)
ax.set_xlabel('Extreme Weather-Related FRA Cause Codes', fontsize=13)
# ax.set_title('Summary of Events and Derailments by FRA Code', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(codes, fontsize=13)
ax.tick_params(axis='y', labelsize=13)
ax.legend(loc='upper right', bbox_to_anchor=(0.85, 1), fontsize=8)

plt.tight_layout()
# Save the plot at 720 dpi
output_path = os.path.join(directory, "extreme_causecodes_summary.png")
plt.tight_layout()
plt.savefig(output_path, dpi=400)

# Show the plot
plt.show()

# %%
# ! ----------------------------------------------------------------------------------------------------------
# ! Title: Classification of Flood-Related Rail Accidents (T002 & M103) by Coordinate Data Quality (2000–2024)
# ! ----------------------------------------------------------------------------------------------------------

import pandas as pd
import os
import re
import matplotlib.pyplot as plt

# Set up file path
directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(directory, "Rail_Equipment_Accident_Incident_Data__Form_54__20250225_2.csv")

# Load and clean data
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()

# Filter years
df = df[(df['Year'] >= 2000) & (df['Year'] <= 2024)]

# Step 1: Filter by Accident Cause Code
df_t002_raw = df[df['Accident Cause Code'] == 'T002']
df_m103 = df[df['Accident Cause Code'] == 'M103']

# Step 2: Define flood-related keywords for T002 filtering
keywords = ['washout', 'rain', 'flood']
pattern = r'\b(?:' + '|'.join(re.escape(k) for k in keywords) + r')\b'
df_t002 = df_t002_raw[df_t002_raw['Narrative'].str.contains(pattern, case=False, na=False, regex=True)]

# Step 3: Define classification function
def classify_by_coords(df_subset):
    df_nan = df_subset[df_subset[['Latitude', 'Longitude']].isnull().any(axis=1)]
    df_zero = df_subset[
        df_subset['Latitude'].notnull() &
        df_subset['Longitude'].notnull() &
        ((df_subset['Latitude'] == 0) | (df_subset['Longitude'] == 0))
    ]
    df_valid = df_subset[
        df_subset['Latitude'].notnull() &
        df_subset['Longitude'].notnull() &
        (df_subset['Latitude'] != 0) &
        (df_subset['Longitude'] != 0)
    ]
    df_invalid = pd.concat([df_zero, df_nan])
    return df_valid, df_invalid

# Step 4: Classify each group
valid_t002, invalid_t002 = classify_by_coords(df_t002)
valid_m103, invalid_m103 = classify_by_coords(df_m103)

# Step 5: Combine for total
valid_all = pd.concat([valid_t002, valid_m103])
invalid_all = pd.concat([invalid_t002, invalid_m103])

# Step 6: Save valid records
output_path = os.path.join(directory, "1-Flood_Causes(T002&M103)_ValidCoordinates.xlsx")
valid_all.to_excel(output_path, index=False)

# Step 7: Bar Plot
categories = ['T002 (Filtered)', 'M103', 'Combined']
valid = [len(valid_t002), len(valid_m103), len(valid_all)]
invalid = [len(invalid_t002), len(invalid_m103), len(invalid_all)]

fig, ax = plt.subplots(figsize=(8, 5))
bar1 = ax.bar(categories, valid, label='Valid Coordinates', color='#4CAF50')
bar2 = ax.bar(categories, invalid, bottom=valid, label='Invalid Coordinates', color='#F44336')

# Add value labels
for i in range(len(categories)):
    # Valid
    ax.text(i, valid[i] / 2, str(valid[i]), ha='center', va='center', color='white', fontsize=10)
    # Invalid
    ax.text(i, valid[i] + invalid[i] / 2, str(invalid[i]), ha='center', va='center', color='white', fontsize=10)
    # Total
    ax.text(i, valid[i] + invalid[i] + 2, f"{valid[i] + invalid[i]}", ha='center', fontsize=11, fontweight='bold')

# Plot formatting
ax.set_ylabel("Number of Records", fontsize=12)
ax.set_title("Flood-Related Records by Coordinate Classification", fontsize=14)
ax.legend(title="Coordinate Status")
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)
plt.tight_layout()

# Save and show
output_plot = os.path.join(directory, "1-Flood_Causes(T002&M103).png")
plt.savefig(output_plot, dpi=720)
plt.show()

# %%
# ! -----------------------------------------------------------------------------------------------------------------------------
# ! Title: Identification and Classification of T109 (Sun Kink / Heat Buckling) Rail Accidents with Valid Coordinates (2000–2024)
# ! -----------------------------------------------------------------------------------------------------------------------------

import pandas as pd
import os
import re

# Set up file path
directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(directory, "Rail_Equipment_Accident_Incident_Data__Form_54__20250225_2.csv")

# Load and clean data
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()

# Filter years
df = df[(df['Year'] >= 2000) & (df['Year'] <= 2024)]

# Step 1: Filter for T109 (track alignment irregular - buckling / sun kink)
df_t109 = df[df['Accident Cause Code'] == 'T109']

# Step 2: Define keywords and match as whole words using \b
keywords = ['sun', 'thermal', 'heat', 'temperature', 'sunkink', 
            'sun kink', 'hot', 'kinked', 'buckling']

escaped_keywords = [re.escape(k) for k in keywords]
pattern = r'\b(?:' + '|'.join(escaped_keywords) + r')\b'
df_t109_heat = df_t109[df_t109['Narrative'].str.contains(pattern, case=False, na=False, regex=True)]

# Step 3: Classify based on coordinate availability
df_t109_valid = df_t109_heat[
    df_t109_heat['Latitude'].notnull() &
    df_t109_heat['Longitude'].notnull() &
    (df_t109_heat['Latitude'] != 0) &
    (df_t109_heat['Longitude'] != 0)
]

df_t109_zero = df_t109_heat[
    df_t109_heat['Latitude'].notnull() &
    df_t109_heat['Longitude'].notnull() &
    ((df_t109_heat['Latitude'] == 0) | (df_t109_heat['Longitude'] == 0))
]

df_t109_nan = df_t109_heat[df_t109_heat[['Latitude', 'Longitude']].isnull().any(axis=1)]

# Step 4: Add readable description
df_t109_valid = df_t109_valid.copy()
df_t109_valid['Cause Description'] = "T109: Track alignment irregular (sun kink / heat)"

# Step 5: Print summary
print("\n--- T109 (Track Buckling / Sun Kink) Summary ---")
print(f"Total T109 records (filtered by keywords): {len(df_t109_heat)}")
print(f"Valid coordinates: {len(df_t109_valid)}")
print(f"Zero coordinates: {len(df_t109_zero)}")
print(f"Missing coordinates (NaN): {len(df_t109_nan)}")

# Step 6: Save valid filtered data to Excel
output_path = os.path.join(directory, "2-SunKink_T109_Filtered.xlsx")
df_t109_valid.to_excel(output_path, index=False)

print(f"\nValid T109 records saved to: {output_path}")

print("\n--- Keyword Occurrences in Valid T109 Records ---")
for kw in keywords:
    if ' ' in kw or '-' in kw:
        # Phrase or hyphenated term (no word boundary)
        count = df_t109_valid['Narrative'].str.contains(re.escape(kw), case=False, na=False).sum()
    else:
        # Whole word match using word boundaries
        count = df_t109_valid['Narrative'].str.contains(r'\b' + re.escape(kw) + r'\b', case=False, na=False).sum()
    print(f"{kw}: {count}")

# --- Plot Section ---
total_count = len(df_t109_heat)
valid_count = len(df_t109_valid)
invalid_count = len(df_t109_zero) + len(df_t109_nan)

# Bar segments and settings
segments = [valid_count, invalid_count]
labels = ['Valid Coordinates', 'Invalid Coordinates']
colors = ['#4CAF50', '#F44336']

# Create plot
fig, ax = plt.subplots(figsize=(6, 6))
bottom = 0
for count, label, color in zip(segments, labels, colors):
    ax.bar('T109 (Heat)', count, bottom=bottom, label=f"{label}: {count}", color=color, edgecolor='black')
    ax.text(0, bottom + count / 2, f'{count}', ha='center', va='center', color='white', fontsize=11, fontweight='bold')
    bottom += count

# Add total count
ax.text(0, bottom + 5, f"{total_count}", ha='center', fontsize=12, fontweight='bold')

# Format plot
ax.set_ylabel("Number of Records", fontsize=12)
ax.set_ylim(0, bottom + 20)
ax.set_title("T109 Coordinate Classification (2000–2024)", fontsize=14)
ax.legend(loc='upper right')
plt.tight_layout()

# Save and show
plot_path = os.path.join(directory, "2-SunKink_T109.png")
plt.savefig(plot_path, dpi=720)
plt.show()

print(f"Plot saved to: {plot_path}")

# %%
# ! ---------------------------------------------------------------------------------------------------------------------
# ! Title: Identification of Landslide-Related Rail Accidents by Keyword Filtering and Coordinate Validation (2000–2024)
# ! ---------------------------------------------------------------------------------------------------------------------

import pandas as pd
import os
import re

# Set up file path
directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(directory, "Rail_Equipment_Accident_Incident_Data__Form_54__20250225_2.csv")

# Load and clean data
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()

# Filter years
df = df[(df['Year'] >= 2000) & (df['Year'] <= 2024)]

# Filter relevant accident cause codes
relevant_codes = ['M101', 'M103', 'M199', 'M402', 'M404', 'T001', 'T002', 'T099']
df = df[df['Accident Cause Code'].isin(relevant_codes)]

# Define strict regex pattern to catch 'slide', 'landslide', 'mudslide', etc., but not 'slidemaster'
pattern = r'\b(?:landslide|mudslide|rockslide|slide|earthslide)\b'

# Filter for landslide-related events
df_slide_filtered = df[df['Narrative'].str.contains(pattern, case=False, na=False, regex=True)]

# The above code is saving the filtered results from the DataFrame `df_slide_filtered` to an Excel
# file named "3-1-Filtered_Slide_Keyword_All.xlsx" in the specified directory. The `to_excel` method
# is used to write the DataFrame to an Excel file without including the index column.
# Save all filtered results
# output_all = os.path.join(directory, "3-1-Filtered_Slide_Keyword_All.xlsx")
# df_slide_filtered.to_excel(output_all, index=False)

# Filter for valid coordinates
df_slide_valid = df_slide_filtered[
    df_slide_filtered['Latitude'].notnull() &
    df_slide_filtered['Longitude'].notnull() &
    (df_slide_filtered['Latitude'] != 0) &
    (df_slide_filtered['Longitude'] != 0)
]

# Save valid coordinate matches
output_coords = os.path.join(directory, "3-Filtered_Slide_Keyword_WithCoords.xlsx")
df_slide_valid.to_excel(output_coords, index=False)

# Report summary dictionary
summary = {
    "Total keyword matches (slide variants)": len(df_slide_filtered),
    "Valid coordinate matches": len(df_slide_valid),
    "Cause Codes Included": relevant_codes,
    "Output Files": {
        "All Matches": output_all,
        "With Coordinates": output_coords
    }
}
summary

# Group by cause code and count keyword matches
total_per_code = df_slide_filtered['Accident Cause Code'].value_counts()
valid_per_code = df_slide_valid['Accident Cause Code'].value_counts()

# Align indexes and compute invalids
codes = sorted(total_per_code.index.union(valid_per_code.index))
total_counts = total_per_code.reindex(codes, fill_value=0)
valid_counts = valid_per_code.reindex(codes, fill_value=0)
invalid_counts = total_counts - valid_counts

# Append total summary for all codes
codes.append("Total")
total_counts["Total"] = total_counts.sum()
valid_counts["Total"] = valid_counts.sum()
invalid_counts["Total"] = invalid_counts.sum()

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
bar_width = 0.6

# Plot stacked bars
bars_valid = ax.bar(codes, valid_counts, label='Valid Coordinates', color='tab:blue')
bars_invalid = ax.bar(codes, invalid_counts, bottom=valid_counts, label='Invalid Coordinates', color='tab:orange')

# Add count labels
for i, code in enumerate(codes):
    valid_val = valid_counts[code]
    invalid_val = invalid_counts[code]
    total_val = total_counts[code]
    
    # Valid label inside blue bar
    if valid_val > 0:
        ax.text(i, valid_val / 2, str(valid_val), ha='center', va='center', color='white', fontsize=9)

    # Invalid label inside orange bar
    if invalid_val > 0:
        ax.text(i, valid_val + invalid_val / 2, str(invalid_val), ha='center', va='center', color='black', fontsize=9)

    # Total on top
    ax.text(i, total_val + 1, str(total_val), ha='center', va='bottom', fontsize=10)

# Final touches
ax.set_xlabel("Accident Cause Code", fontsize=12)
ax.set_ylabel("Number of Records", fontsize=12)
ax.set_title("Landslide-Related Records by Cause Code (2000–2024)", fontsize=14)
ax.legend()
# ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
# Save the figure
plot_path = os.path.join(directory, "3-Landslide_CauseCode_StackedBar.png")
plt.savefig(plot_path, dpi=720)
plt.show()

print(f"Plot saved to: {plot_path}")
# %%
import matplotlib.pyplot as plt
import numpy as np

# Define categories for each hazard type
hazards = ["Flood (T002+M103)", "Heat Buckling (T109)", "Landslide (Slide Codes)"]

# Sample data manually extracted from previous summaries
valid_counts = [134, 131, 62]        # Replace 62 with actual landslide valid count if known
invalid_counts = [106, 137, 53]      # Zero + NaN for each hazard (from previous calculations)

# Compute total
total_counts = [v + i for v, i in zip(valid_counts, invalid_counts)]

# Plot
x = np.arange(len(hazards))
bar_width = 0.6

fig, ax = plt.subplots(figsize=(9, 6))

bars_valid = ax.bar(x, valid_counts, label='Valid Coordinates', color='#4CAF50')
bars_invalid = ax.bar(x, invalid_counts, bottom=valid_counts, label='Invalid Coordinates', color='#F44336')

# Add text labels
for i in range(len(hazards)):
    # Valid inside
    ax.text(x[i], valid_counts[i] / 2, str(valid_counts[i]), ha='center', va='center', color='white', fontsize=10)
    # Invalid inside
    ax.text(x[i], valid_counts[i] + invalid_counts[i] / 2, str(invalid_counts[i]), ha='center', va='center', color='white', fontsize=10)
    # Total on top
    ax.text(x[i], total_counts[i] + 2, str(total_counts[i]), ha='center', va='bottom', fontsize=11, fontweight='bold')

# Labels
ax.set_xticks(x)
ax.set_xticklabels(hazards, fontsize=11)
ax.set_ylabel("Number of Records", fontsize=12)
ax.set_title("Natural Hazard-Related Rail Accidents by Coordinate Classification (2000–2024)", fontsize=14)
ax.legend(title="Coordinate Status")
plt.tight_layout()

# Save the figure
combined_plot_path = os.path.join(directory, "Combined_Hazard_Coordinate_Classification.png")
plt.savefig(combined_plot_path, dpi=720)
plt.show()

combined_plot_path

# %%
