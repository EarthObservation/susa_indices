"""
STEP 1: Create CLEAN shape file: prepare SHP to be used for aggregation of
drought indices.
23/03/2021

1. Read SHP file (example: ZV2017_d96tm.shp)
2. Filter rows (by area, location, etc..)
3. Remove any surplus columns
4. Change POLJINA_ID type from float to int
"""
import geopandas as gpd
from os.path import join
from os import makedirs

# Read Geo Data Frame
slo = gpd.read_file("c:\\Users\\ncoz\\ARRS_susa\\drought_indices\\ZV2017_d96tm_big10_slo_all.shp")

# Set output location
out_dir = "c:\\Users\\ncoz\\ARRS_susa\\ARSKTRP_ZV_clean"
out_nam = "ZV2017_d96tm_clean.shp"
out_pth = join(out_dir, out_nam)
makedirs(out_dir, exist_ok=True)

# 2017 shape has already been filtered, here add filter for other years

# Print column names
slo.keys()
# Print dtypes of columns
slo.dtypes()

# Drop surplus columns (required for 2017)
clean = slo.drop(columns=[
    'ndvi_mean', 'evi2_mean', 'ndwi_mean',
    'savi_mean', 'hand_mean', 'hand_std'
])
clean.keys()

# Change dtype of POLJINA_ID
clean = clean.astype({"POLJINA_ID": 'int64'})
print(clean.POLJINA_ID.dtype)

# Save as SHP file
clean.to_file(out_pth)
