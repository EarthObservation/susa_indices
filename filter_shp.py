"""
TOOL: Filter SHP to only include matching rows from a different shapefile.
30/03/2021

We have one layer with x amount of rows and another with y amount, where x < y.
The x rows are a subset of y rows. We want to reduce the y layer to only include
the rows contained in x. The unique row ID is "POLJINA_ID".
"""

import geopandas as gpd
from os.path import join

index = "evi2"

# Target size
slo = gpd.read_file("c:\\Users\\ncoz\\ARRS_susa\\drought_indices\\ZV2017_d96tm_big10_slo_all.shp")

# # Some lines that can be used for examining the data
# # 1) list al unique values in the selected column
# unique = slo["POLJINA_ID"].unique()
# # 2) How many instances of each value there are in a column
# instances = slo["REGIJA"].value_counts()

# Input file
filter_dir = "c:\\susa\\ZV2017_susni_indeksi_ts"
filter_name = f"ZV2017_d96tm_Slo_big10_{index}_{index}.shp"
to_filter = join(filter_dir, filter_name)

# Output file
save_dir = r"c:\susa\ZV2017_susni_indeksi_SLO_ts"
save_name = f"ZV2017_d96tm_big10_slo_ts_{index}.shp"
save_file = join(save_dir, save_name)

# Read gdf:
gdf = gpd.read_file(to_filter)

keys = ["GERK_PID", "POLJINA_ID"]

i1 = gdf.set_index(keys).index
i2 = slo.set_index(keys).index
gdf = gdf[i1.isin(i2)]

# Save shapefile (drop GeoJSON and raster columns)
print("Saving SHP...")
gdf.to_file(save_file)

# Save CSV (also drop geometry)
print("Saving CSV...")
gdf2 = gdf.drop(columns=["geometry"])
gdf2.to_csv(save_file[:-4] + ".csv")
