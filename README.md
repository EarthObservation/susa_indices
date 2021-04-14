# susa_indices
A series of routines used for aggregation of raster data into tables, developed for the ARRS Susa project.

##Main routine for processing:
1. prepare_clean_shape.py
   
Create a clean shape file that will be used for extraction of indexes.
The same shapefile will be used to extract different indices (ndvi, savi, etc.),
so it will make next steps easier (individual file per each index, but rows will match)

2. stack_gtif.py
   
Stack all rasters into a single file to speed-up processing. This step is a hack
that is ok for the current use, but may not work for other similar projects or
using a different PC (requires a lot of RAM).

3. raster2table.py (or r2t_*.py)

This is the main script that actually does all the processing.

##Other tools
All other scripts were used as tools through the development of the routine.
They will be kept for future references.

