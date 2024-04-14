# -*- coding: utf-8 -*-
"""
此代码用于把轨道数据处理为buffer数据
可以通过改变 MIN_RES 控制输出的数据的最小分辨率
"""
import arcpy
import os
from tools import *

MIN_RES = 10
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
    'SENTINEL': 145,
    'LANDSAT': 92,
    'SPOT': 30,
    'IKONOS': 5.7

}

RES = {
    'GAOFEN_1': 8,
    'GAOFEN_2': 3.2,
    'GAOFEN_3': 5,
    'GAOFEN_4': 50,
    'GAOFEN_5': 20,
    'GAOFEN_6': 8,
    'GAOFEN_7': 2.6,
    'GAOFEN_DM': 2,
    'TIANHUI': 10,
    'JILIN': 2.88,
    'ZIYUAN_3': 5.8,
    'ZY1': 10,
    'GAOJING': 1,
    'SENTINEL': 10,
    'LANDSAT': 30,
    'SPOT': 6,
    'IKONOS': 4
}


def main(line_shp, sate_name, save_path):
    name_known = False
    for key in Widths.keys():
        if key in sate_name:
            name_known = True
            name = key
    assert name_known is True

    width = Widths[name]
    res = RES[name]
    if res >= MIN_RES:
        return
    out_buffer_shp = os.path.join(save_path, '{}.shp'.format(sate_name))
    if os.path.exists(out_buffer_shp):
        return
    arcpy.Buffer_analysis(line_shp, out_buffer_shp, "{} KILOMETERS".format(width), "FULL", "FLAT", "NONE")


if __name__ == '__main__':
    for end_date in [24, 26, 28, 30]:
        line_file_path = r'F:\STKDATA\SHPs\TracksinRange_2\23_{}'.format(end_date)
        save_path = make_dir(r'F:\STKDATA\Buffer_minres{}\23_{}'.format(MIN_RES, end_date))

        filepaths, filenames = file_name_shp(line_file_path)
        for ii in range(len(filepaths)):
            filepath = filepaths[ii]
            filename = filenames[ii]
            print 'processing {}'.format(filepath)
            main(filepath, filename, save_path)
            # print filename