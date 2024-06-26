# -*- coding: utf-8 -*-
"""
这个代码用于将栅格文件转换为shp文件

"""
from tools import *


def to_shp_signle(filepath, savepath):
    arcpy.RasterToPolygon_conversion(filepath, savepath, "NO_SIMPLIFY", "VALUE")


def to_shp_dir(dpath, save_root):
    make_dir(save_root)
    paths, names = file_name_tif(dpath)
    for ii in range(len(paths)):
        print "processing {}/{}".format(ii, len(paths))
        file_path = paths[ii]
        file_name = names[ii]
        save_path = os.path.join(save_root, file_name+'.shp')


        to_shp_signle(file_path, save_path)


if __name__ == '__main__':
    year = 2016
    to_shp_dir(r'G:\ProductData\CBRA\CBRA_{}_10m'.format(year), save_root=r'G:\ProductData\CBRA\CBRA_{}_10m_shp')
