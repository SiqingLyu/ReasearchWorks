# -*- coding: utf-8 -*-

from tools import *
import numpy
import os
import arcpy
from arcpy import env
from arcpy.sa import *

# Aggregate (in_raster, cell_factor, {aggregation_type}, {extent_handling}, {ignore_nodata})

in_raster_dir = r'D:\experiment\results\BSG_Maskres50_result_V2.3MUX_newscheduler_15city_60\IMG_10'
Nonodata_raster_dir = r'D:\experiment\results\BSG_Maskres50_result_V2.3MUX_newscheduler_15city_60\IMG_10_nodata0'
save_dir = r'D:\experiment\results\BSG_Maskres50_result_V2.3MUX_newscheduler_15city_60\IMG_10_500'
make_dir(save_dir)
make_dir(Nonodata_raster_dir)
filepaths, filenames = file_name_tif(in_raster_dir)
for ii in range(len(filenames)):
    filepath = filepaths[ii]
    filename = filenames[ii]
    expression = 'Con(IsNull("' + filepath + '"),0,"' + filepath + '")'

    print("processing ", filename)

    cellFactor = 50
    # Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")
    nonodata_raster = arcpy.gp.RasterCalculator_sa(expression, os.path.join(Nonodata_raster_dir, filename+'.tif'))
    # Execute Aggregate
    in_raster = os.path.join(Nonodata_raster_dir, filename+'.tif')
    outAggreg = Aggregate(in_raster, cellFactor, "MEAN", "TRUNCATE", "NODATA")
    # Save the output
    outAggreg.save(os.path.join(save_dir, filename+'.tif'))

