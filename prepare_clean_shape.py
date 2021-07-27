"""
STEP 1: Create CLEAN shape file: prepare SHP to be used for aggregation of
drought indices.
23/03/2021

1. Read SHP file (example: ZV2017_d96tm.shp)
2. Filter rows (by area, location, etc..)
3. Remove any surplus columns
4. Change POLJINA_ID type from float to int
"""
import time

import geopandas as gpd
from os.path import join
from os import makedirs

# Read Geo Data Frame
# slo = gpd.read_file("c:\\Users\\ncoz\\ARRS_susa\\drought_indices\\ZV2017_d96tm_big10_slo_all.shp")
# slo = gpd.read_file("p:\\ARRS Susa\\podatki\ARSKTRP_ZV\\ZV2018_d96tm.shp")
slo = gpd.read_file("p:\\ARRS Susa\\podatki\\ARSKTRP_KMRS\\KMRS_2019.shp")

# Set output location
out_dir = "c:\\Users\\ncoz\\ARRS_susa\\ARSKTRP_ZV_clean"
# out_nam = "ZV2017_d96tm_clean.shp"
# out_nam = "ZV2018_d96tm_clean.shp"
out_nam = "KMRS2019_clean.shp"
out_pth = join(out_dir, out_nam)
makedirs(out_dir, exist_ok=True)

# 2017 shape has already been filtered, here add filter for other years
# 1.) keep only larger than 10 ar
slo_big10 = slo[slo["geometry"].area > 1000]
# slo_big10 = slo[slo["POVR_ar"] > 10]

# 2.) Filter with buffer (exclude
slo_big10["buffered"] = slo_big10["geometry"].buffer(-5)
slo_big10 = slo_big10[slo_big10["buffered"].area > 0]
slo_big10 = slo_big10.drop(columns=['buffered'])
slo_big10 = slo_big10.reset_index()

# 3.) Remove those outside the border
border = gpd.read_file("c:\\Users\\ncoz\\ARRS_susa\\DrzavnaMejaSLO\\DrzavnaMejaSLO_d96tm.shp")
my_grid = slo_big10.geometry.sindex.query_bulk(border.geometry, predicate="contains")

# open 2017 shape for comparison
# slo17 = gpd.read_file("p:\ARRS Susa\podatki\ARSKTRP_ZV_clean\ZV2017_d96tm_clean.shp")

# Print column names
# slo.keys()
# Print dtypes of columns
# slo.dtypes()

# # Drop surplus columns (required for 2017)
# clean = slo.drop(columns=[
#     'ndvi_mean', 'evi2_mean', 'ndwi_mean',
#     'savi_mean', 'hand_mean', 'hand_std'
# ])
# clean.keys()

# Change dtype of POLJINA_ID
slo_big10 = slo_big10.astype({"POLJINA_ID": 'int64'})
print(slo_big10.POLJINA_ID.dtype)

# Save as SHP file
slo_big10.to_file(out_pth)
