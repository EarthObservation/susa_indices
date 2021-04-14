"""
STEP 3: Extract raster covered by polygon and calculate statistics. It is an
updated version of raster2table.py
30/03/2021

Variant 2
- use buffer and remove polygons that are too small
- calculate 75 percentile instead of mean
- add pixel count for each polygon
- calculate monthly statistics and interpolate where value is missing

NOTE: Before you can start extracting data from rasters, the rasters have to be
stacked into a single GeoTIFF file (see stack_gtif.py)
"""

import time
from tqdm import tqdm

from shapely.geometry import mapping
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from os.path import join, basename
from os import makedirs


def r2t(pth_raster, pth_shp, dir_out, suffix):
    """Function creates shape file and csv file containing mean and standard
    deviation of the underlain raster for each polygon.

    Parameters
    ----------
    pth_raster : str
        Path to input raster.
    pth_shp : str
        Path to input shapefile.
    dir_out : str
        Path to directory for saving results.
    suffix : str
        Suffix to be added to results.

    Returns
    -------
        Finished message.
    """

    def ms_rio(geom, raster):
        """Returns subset of an array covered by the input polygon. The input
        polygon has to be in the GeoJSON format. The crop attribute sets values
        not covered by polygon to nan. All_touched is used to prevent empty rasters
        for very thin polygons."""
        out_image, _ = mask(raster, geom, crop=True, all_touched=True, nodata=np.nan)
        return out_image

    # Prepare output name for saving results to files
    out_name = basename(pth_shp)[:-4] + "_" + suffix

    # Read polygons to data frame
    print("Reading shapefile...")
    t = time.time()
    tdf = gpd.read_file(pth_shp)
    t = time.time() - t
    print(f"Read SHP with GeoPandas: {t} seconds")

    # # Write to / read from pickle for faster debugging
    # pickle.dump(tdf, "df.p", "wb"))
    # tmp_read = pickle.load(open("df.p", "rb"))

    # # Uncomment for processing of a subset (useful for debugging)
    # # tdf = tdf[tdf.REGIJA == 4].copy()
    # tdf = tdf[0:1000].copy()

    # Add buffer and reformat geometry to GeoJSON format (append a new column)
    print("Adding buffer")
    tdf["buffered"] = tdf["geometry"].buffer(-5)
    tqdm.pandas(desc="geometry -> GeoJSON")
    tdf["geom"] = tdf["buffered"].progress_apply(lambda g: [mapping(g)])
    # # TEST WITHOUT BUFFER
    # tqdm.pandas(desc="geometry -> GeoJSON2")
    # tdf["geom2"] = tdf.geometry.progress_apply(lambda g: [mapping(g)])

    # Remove polygons with 0 area after buffer
    rows_a, _ = tdf.shape
    tdf = tdf[tdf["buffered"].area > 0].copy()
    rows_b, _ = tdf.shape
    rows_removed = rows_a - rows_b
    print(f"Filtering... Removed {rows_removed} rows")

    # Extract rasters, and calculate mean & std (each stored to a new column)
    src = rasterio.open(pth_raster)
    tqdm.pandas(desc="Extracting arrays")
    tdf["hand_rst"] = tdf.geom.progress_apply(lambda g: ms_rio(g, src))
    # # TEST WITHOUT
    # tqdm.pandas(desc="Extracting arrays2")
    # tdf["hand_rst2"] = tdf.geom2.progress_apply(lambda g: ms_rio(g, src))
    src.close()

    # Count valid pixels
    tqdm.pandas(desc="Counting pixels")
    tdf["pix_count"] = tdf.hand_rst.progress_apply(lambda g: int(np.count_nonzero(~np.isnan(g), axis=(1, 2))))

    # # Calculate 75th percentile by dates
    # tqdm.pandas(desc="75th percentile")
    # tdf["by_dates"] = tdf.hand_rst.progress_apply(lambda g: np.nanpercentile(g, 75, axis=(1, 2)))
    # print(" Splitting LIST to COLUMNS...")
    # # Create list of column names (dates of individual images)
    # with open("c:\\susa\\datumi_ZV2017.txt") as file:
    #     dates = [suffix + "_" + x.rstrip('\n') for x in file]
    # tdf[dates] = gpd.GeoDataFrame(tdf.by_dates.tolist(), index=tdf.index)
    # tdf = tdf.drop(columns=["by_dates"])

    # Calculate aggregated mean (HAND INDEX)
    tqdm.pandas(desc="Mean")
    index_tag = suffix + "_mean"
    tdf[index_tag] = tdf.hand_rst.progress_apply(lambda g: np.nanmean(g))

    # Caluclate Standard Deviation (HAND INDEX)
    tqdm.pandas(desc="Std")
    tdf["hand_std"] = tdf.hand_rst.progress_apply(lambda g: np.nanstd(g))

    # Save shapefile (drop GeoJSON and raster columns)
    print("Saving SHP...")
    makedirs(dir_out, exist_ok=True)
    out_shp = join(dir_out, out_name + ".shp")
    tdf = tdf.drop(columns=["buffered", "geom", "hand_rst"])
    tdf.to_file(out_shp)

    # Save CSV (also drop geometry)
    print("Saving CSV...")
    makedirs(dir_out, exist_ok=True)
    out_csv = join(dir_out, out_name + ".csv")
    tdf = tdf.drop(columns=["geometry"])
    tdf.to_csv(out_csv)

    return "DONE!"


if __name__ == "__main__":
    # SET PATHS
    # ---------
    # Input raster
    # geotiff = "c:\\susa\\ZV2017_NDVI_Cmask.tif"
    geotiff = "p:\\ARRS Susa\\podatki\\hand_index\\hand_index_d96tm.tif"

    # Input shape file
    # shapefile = "c:\\susa\\ZV2017_d96tm_Slo_big10\\ZV2017_d96tm_Slo_big10.shp"
    shapefile = "c:\\susa\\ARSKTRP_ZV_clean\\ZV2017_d96tm_clean.shp"
    # Output folder and suffix to be added to SHP and CSV files
    output_loc = "c:\\susa\\ZV2017_pc075"
    suff = "hand"

    print(f">>> Run for: {suff}")

    result = r2t(geotiff, shapefile, output_loc, suff)
    print(result)
