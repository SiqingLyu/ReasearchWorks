# -*- coding: utf-8 -*-
"""
此代码用于将所有国内数据合并为一个，把所有国外数据合并为一个
以完成国内外数据的对比

"""
import arcpy
import os
from tools import *

Widths = {
    'GAOFEN_1': 30,
    'GAOFEN_2': 22.5,
    'GAOFEN_3': 25,
    'GAOFEN_4': 200,
    'GAOFEN_5': 30,
    'GAOFEN_6': 30,
    'GAOFEN_7': 10,
    'GAOFEN_DM': 7.5,
    'TIANHUI': 30,
    'JILIN': 75,
    'ZIYUAN_3': 25,
    'ZY1': 58,
    'GAOJING': 6,

}

Fore_widths = {
    'SENTINEL': 145,
    'LANDSAT': 92,
    'SPOT': 30,
    'IKONOS': 5.7
}


def main(merge_list, save_path):
    arcpy.Merge_management(merge_list, save_path)


if __name__ == '__main__':
    Dome_lists = Widths.keys()
    Fore_lists = Fore_widths.keys()
    print Fore_lists, Dome_lists
    for end_date in [24, 26, 28, 30]:
        dome_file_paths = []
        fore_file_paths = []
        line_file_path = r'F:\STKDATA\Buffer_minres10\23_{}'.format(end_date)
        save_path_dome = make_dir(r'F:\STKDATA\Buffer_minres10_Dome\23_{}'.format(end_date))
        save_path_fore = make_dir(r'F:\STKDATA\Buffer_minres10_Fore\23_{}'.format(end_date))
        filepaths, filenames = file_name_shp(line_file_path)
        for ii in range(len(filenames)):
            filepath = filepaths[ii]
            filename = filenames[ii]
            name_known = False
            for key in Dome_lists:
                if key in filename:
                    dome_file_paths.append(filepath)
            for key in Fore_lists:
                if key in filename:
                    fore_file_paths.append(filepath)
        assert (len(dome_file_paths) + len(fore_file_paths)) == len(filenames)

        main(dome_file_paths, os.path.join(save_path_dome, 'Domestic.shp'))
        main(fore_file_paths, os.path.join(save_path_fore, 'Foreign.shp'))


