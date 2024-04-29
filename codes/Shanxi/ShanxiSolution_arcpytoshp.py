# -*- coding: utf-8 -*-
import arcpy
import argparse
from arcpy import env
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str, default=r"test.tif")
    parser.add_argument('--savepath', type=str, default="test.shp")
    parser.add_argument('--oripath', type=str, default="test.shp")
    args = parser.parse_args()

    tif_path = args.filepath
    savepath = args.savepath
    oripath = args.oripath
    # arcpy.management.DeleteField(oripath, ["area"])

    line_ = savepath[:-4] + '_line.shp'
    polygon_ = savepath[:-4] + '_polygon.shp'
    erase_ = savepath[:-4] + '_erase.shp'
    join_ = savepath[:-4] + '_jointemp.shp'
    merge_ = savepath[:-4] + '_merge.shp'
    dissolve_ = savepath[:-4] + '_dissolve.shp'

    arcpy.RasterToPolygon_conversion(tif_path, savepath, "SIMPLIFY", "VALUE")

    arcpy.FeatureToLine_management(savepath,  line_)
    arcpy.FeatureToPolygon_management(line_, polygon_)
    arcpy.Erase_analysis(polygon_, savepath, erase_)
    arcpy.SpatialJoin_analysis(erase_, savepath, join_)
    arcpy.Merge_management([join_, savepath], merge_)
    arcpy.Dissolve_management(merge_, dissolve_, ["GRIDCODE"], None, "SINGLE_PART", "DISSOLVE_LINES")

