"""
This script applies cloud mask to S-2 images:
- select images based on files prepared by Ursa on p: drive
- use rasterio to mask
- save to an external drive (nvme on this occasion)
"""
import numpy as np
import time
from os.path import join, basename
from os import makedirs
import glob
from osgeo import gdal


def stack_gtif(q_key, q2_key, dir_save):
    t = time.time()

    # SIGMA
    print(f"Query search: {q_key}")
    search_q = sorted(glob.glob(q_key))
    images = [a for a in search_q if 3 < int(basename(a)[4:6]) < 11]
    images = [images[i:i + 4] for i in range(0, len(images), 4)]

    # COHERENCE
    print(f"Query search: {q_key}")
    search_q2 = sorted(glob.glob(q2_key))
    images2 = [a for a in search_q2 if 3 < int(basename(a)[4:6]) < 11]
    images2 = [images2[i:i + 4] for i in range(0, len(images2), 4)]

    weeks = [a + b for a, b in zip(images, images2)]

    for files in weeks:
        # Number of new bands
        fil_save = basename(files[0])[:8]
        output_name = join(dir_save, f"slc_{fil_save}.tif")

        # Set output bounds for Slovenia
        out_bounds = [368930, 5024780, 627570, 5197200]

        # Create VRT
        vrt = 'OutputImage.vrt'
        vrt2 = 'WarpedImage.vrt'
        gdal.BuildVRT(vrt, files, separate=True, callback=gdal.TermProgress_nocb)

        ii1 = gdal.Open(vrt, 0)  # open the VRT in read-only mode
        ds = gdal.Warp(vrt2, ii1, srcNodata=np.nan, format='VRT',
                       dstNodata=np.nan, outputBounds=out_bounds,
                       callback=gdal.TermProgress_nocb)
        ds = None
        ii1 = None
        ii2 = gdal.Open(vrt2, 0)  # open the VRT in read-only mode
        gdal.Translate(output_name, ii2, format='GTiff',
                       creationOptions=['TILED:NO'],
                       callback=gdal.TermProgress_nocb)
        ii2 = None

    t = time.time() - t
    return f"\nFinished in: {t} seconds"


if __name__ == "__main__":
    # Search for files in this folder
    glob_keyword = "o:\\aitlas_slc_SI_sigma\\yr17*\\*.tif"
    glob_keyword2 = "o:\\aitlas_slc_SI_coherence\\yr17*\\*.tif"

    # Save to this folder
    save_path = "t:\\susa\\slc_stacks"
    makedirs(save_path, exist_ok=True)

    out = stack_gtif(glob_keyword, glob_keyword2, save_path)
    print(out)
