"""
STEP 2: Stack rasters into a single file. The final product to be used for
extraction of subsets of raster covered by polygons.
"""
import rasterio
import numpy as np
import time
from os.path import dirname, join, basename
from os import makedirs
import glob
from shutil import copyfile
import rioxarray as rxr


def stack_gtif(q_key, dir_out, copernicus, mr=(0, 13)):
    t = time.time()

    print(f"Query search: {q_key}")
    search_q = sorted(glob.glob(q_key))

    # List all timestamps
    timestamps_all = [basename(a)[:15] for a in search_q]

    # Obtain paths from copernicus folder
    img = []
    msk = []
    for ts in timestamps_all:
        yr = ts[:4]
        img_pth = glob.glob(join(copernicus, yr, ts + "*", ts + "*_p2atm_d96tm.tif"))
        msk_pth = glob.glob(join(copernicus, yr, ts + "*", ts + "*_p2atm_mask_d96tm.tif"))
        img.append(img_pth[0])
        msk.append(msk_pth[0])

    files_dict = [{
        "timestamp": a,
        "date": a[:8],
        "day": int(a[6:8]),
        "month": int(a[4:6]),
        "year": int(a[:4]),
        "img_path": b,
        "msk_path": c
    } for a, b, c in zip(timestamps_all, img, msk)]

    # Save a text file with all the file names and acquisition dates
    dates_txt = join(dir_out, "2017_stacked_timestamps.txt")
    with open(dates_txt, 'w') as fh:
        test = [a["date"] for a in files_dict if (mr[0] <= a["month"] <= mr[1])]
        fh.writelines(f"{place}\n" for place in test)

    # For each month, stack together
    for month in range(mr[0], mr[1] + 1):
        file_list = [sub for sub in files_dict if sub['month'] == month]
        print(month)

        images = len(file_list)

        pth_out = join(dir_out, f"monthly_mean_{month:02}.tif")

        if images > 1:
            # Read metadata of first file
            with rasterio.open(file_list[0]["img_path"]) as src0:
                meta = src0.meta
                shape = src0.shape
                bnds = src0.count  # Should have 4 bands

            # Update meta to reflect the number of layers
            meta.update(count=bnds)

            # Read directly into array (was slightly faster 28 seconds)
            stack = np.empty((images, bnds, shape[0], shape[1]), meta["dtype"])
            for b, dim in enumerate(file_list):
                print(dim)
                # Read image
                with rasterio.open(dim["img_path"]) as src:
                    temp_array = src.read()
                # Read cloud mask
                with rasterio.open(dim["msk_path"]) as src:
                    mask_array = src.read()

                temp_array = np.where(mask_array == 100, temp_array, np.nan)

                with rasterio.open("test.tif", 'w', **meta) as dst:
                    dst.write(temp_array)

                # landsat_pre = rxr.open_rasterio(dim["img_path"])  # .squeeze()
                # landsat_qa = rxr.open_rasterio(dim["msk_path"]).squeeze()
                #
                # landsat_pre_cl_free = landsat_pre.where(landsat_qa.isin([100]))
                #
                # landsat_pre_cl_free.rio.to_raster("test.tif")

                # Apply mask

                # Stack
                stack[b, :, :, :] = temp_array

            # TODO: Calculate mean of each month

            makedirs(dirname(pth_out), exist_ok=True)
            with rasterio.open(pth_out, 'w', **meta) as dst:
                dst.write(stack)

            print(f"{month} - Stacked {bnds} images")
        elif bnds == 1:
            makedirs(dirname(pth_out), exist_ok=True)
            # todo dest = copyfile(file_list[0], pth_out)
            print(f"{month} - Copied a single image to {dest}")
        else:
            print(f"{month} - No images for this month")

    t = time.time() - t
    return f"Finished in: {t} seconds"


if __name__ == "__main__":
    path = "p:\\ARRS Susa\\podatki\\Sentinel-2_atm_10m_D96_2017_Slovenia"
    q_disk_location = "j:\\Sentinel-2_atm_10m_mosaicked_d96"

    file = "*C122*.jpg"
    glob_keyword = join(path, file)
    months_range = (4, 10)  # First and last month of the interval (including both of them)

    out = stack_gtif(glob_keyword, path, q_disk_location, months_range)
    print(out)
