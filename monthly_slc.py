import pandas as pd
import time


t = time.time()

src_pth = "t:\\susa\\ZV2017_slc\\ZV2017_utm_clean_slc.csv"
out_pth = "t:\\susa\\ZV2017_slc\\ZV2017_utm_clean_slc_monthly_linear.csv"

df = pd.read_csv(src_pth)
# df = df[:100].copy()

# List of bands
bands = ["SIG_ASC_VH", "SIG_ASC_VV", "SIG_DES_VH", "SIG_DES_VV",
         "COH_ASC_VH", "COH_ASC_VV", "COH_DES_VH", "COH_DES_VV"]
# List for saving new columns
mean_cols = []
# Define "permanent"" columns
permanent_cols = df.columns.to_list()[:9]

# Calculate monthly mean for each band
for month in range(4, 11):
    for band in bands:
        # Find columns containing current band and month
        tmp_cols = [col for col in df.columns if f"{band}_{month:02}" in col]
        # Append new column name to the list of mean columns
        new_col = f"{band}_{month:02}_mean"
        mean_cols.append(new_col)
        # Calculate nanmean
        df[new_col] = df[tmp_cols].mean(axis=1)

# Interpolate
df[mean_cols] = df[mean_cols].interpolate(axis=1)

# Save temp CSV
print("Saving final CSV...")
df[permanent_cols + mean_cols].to_csv(out_pth, index=False)

t = time.time() - t
print(f"Finished in {t:02} seconds.")
