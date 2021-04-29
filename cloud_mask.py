"""
This script applies cloud mask to S-2 images:
- select images based on files prepared by Ursa on p:\ drive
- use rasterio to mask
- save to an external drive (nvme on this occasion)
"""
import rasterio
import numpy as np
import time
from os.path import dirname, join, basename
from os import makedirs
import glob


def stack_gtif(q_key, dir_save, copernicus, mr=(0, 13)):
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
    dates_txt = join(dir_save, "2017_stacked_timestamps.txt")
    with open(dates_txt, 'w') as fh:
        test = [a["date"] for a in files_dict if (mr[0] <= a["month"] <= mr[1])]
        fh.writelines(f"{place}\n" for place in test)

    # For each month apply cloud mask
    for scene in files_dict:
        if mr[0] <= scene["month"] <= mr[1]:
            t2 = time.time()
            month = scene["month"]
            day = scene["day"]
            pth_out = join(dir_save, f"ZV2017_s2_Cmask_{month:02}_{day:02}.tif")
            print(pth_out)

            # Read image
            with rasterio.open(scene["img_path"]) as src:
                temp_array = src.read()
                meta = src.meta
                shape = src.shape
                bnds = src.count

            # Read cloud mask
            with rasterio.open(scene["msk_path"]) as src:
                mask_array = src.read()
            cloud_mask = mask_array != 100
            cloud_mask = np.broadcast_to(cloud_mask, (bnds, shape[0], shape[1]))

            # Apply cloud mask
            temp_array[cloud_mask] = np.nan

            # Save to TIFF
            makedirs(dirname(pth_out), exist_ok=True)
            with rasterio.open(pth_out, 'w', **meta) as dst:
                dst.write(temp_array)

            t2 = time.time() - t2
            print(f"Time for Cmask: {t2:02} sec.")

    t = time.time() - t
    return f"\nFinished in: {t} seconds"


if __name__ == "__main__":
    path = "p:\\ARRS Susa\\podatki\\Sentinel-2_atm_10m_D96_2017_Slovenia"
    q_disk_location = "j:\\Sentinel-2_atm_10m_mosaicked_d96"
    save_path = "t:\\susa"

    file = "*C122*.jpg"
    glob_keyword = join(path, file)
    months_range = (4, 10)  # First and last month of the interval (including both of them)

    out = stack_gtif(glob_keyword, save_path, q_disk_location, months_range)
    print(out)
