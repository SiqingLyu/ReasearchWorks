# -*- coding: utf-8 -*-
import arcpy
import os
from tools import *


def main(in_file, clip_file, save_file):
    try:
        # polyline = arcpy.FeatureSet(in_file)
        # polygon = arcpy.FeatureSet(clip_file)
        #
        # print polyline.within(polygon)
        arcpy.Clip_analysis(in_file, clip_file, save_file)
    except Exception as e:
        print e
        return save_file

"""
F:\STKDATA\SHPs\TracksinRange_2\23_24\LANDSAT_8_39084.shp
F:\STKDATA\SHPs\TracksinRange_2\23_24\ZIYUAN_3_38046.shp
"""


if __name__ == '__main__':
    range_file = r'F:\STKDATA\SHPs\Range\Glacier_collapse_general_range_2.shp'
    for end_date in [24, 26, 28, 30]:
        shp_path = r'F:\STKDATA\SHPs\23_{}'.format(end_date)
        save_root = make_dir(r'F:\STKDATA\SHPs\TracksinRange_2\23_{}'.format(end_date))

        file_paths, file_names = file_name_shp(shp_path)
        for ii in range(len(file_paths)):
            file_path = file_paths[ii]
            file_name = file_names[ii]
            save_path = os.path.join(save_root, '{}.shp'.format(file_name))
            if os.path.exists(save_path):
                continue
            print save_path
            main(file_path, range_file, save_path)

