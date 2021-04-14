"""
TOOL: Combine 4 shapefiles with individual indices into a single file!

- collate all the data into a single DataFrame and rename column labels
- be careful with index column when reading/writing CSV

ndvi, savi, ndwi, evi2 --> all
"""

import pandas as pd
from os.path import join
import time

t = time.time()

print("Reading primary file...")

csv_dir = "c:\\Users\\ncoz\\ARRS_susa\\indeksi_pc075"

# Row indices were saved in the source CSVs, so ignore import of  the first column
# therefore the index_col= attribute is used to ignore the unnamed column
df_main = pd.read_csv(join(csv_dir, "ZV2017_d96tm_pc075_hand.csv"), index_col="Unnamed: 0")

indices = ["ndvi", "savi", "ndwi", "evi2"]

print("Appending indices...")

for idx in indices:
    print(idx)
    df = pd.read_csv(join(csv_dir, f"ZV2017_d96tm_pc075_{idx}.csv"), index_col="Unnamed: 0")
    # df_test = df.copy()

    # Find monthly labels
    labels_0 = [a for a in df.keys() if any(m in a for m in ["pc075"])]
    # Rename labels
    labels_1 = [f"{idx}_" + a[-2:] for a in labels_0]
    # Save new columns to df
    for l0, l1 in zip(labels_0, labels_1):
        df.rename(columns={l0: l1}, inplace=True)
    # Append monthly statistics to original file
    df_main[labels_1] = df[labels_1]

# Save to csv
print("Saving to CSV...")
df_main.to_csv(join(csv_dir, f"ZV2017_d96tm_pc075_all.csv"), index=False)

t = time.time() - t
print(f"DONE!\n\nProcessing time: {t:02} seconds.")
