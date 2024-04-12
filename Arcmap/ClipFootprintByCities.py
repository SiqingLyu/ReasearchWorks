# -*- coding: utf-8 -*-

from tools import *
import numpy
import os
import arcpy
names = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
         'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
         'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
         'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
         'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
          'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
         'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan',
         'Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing',
         'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Shenyang']

years = [2017, 2018, 2019, 2020, 2021]



for year in years:
    root_path = os.path.join(r'F:\ExperimentData\Zeping5YearsBuildings', str(year))
    dirnames = os.listdir(root_path)
    print dirnames
    for name in names:
        print 'processing ' + name
        # in_raster = os.path.join(in_raster_dir, name+'.tif')
        # in_raster = r'D:\Dataset\全国建筑物高度10m（Wu）数据集\121-127X37-45ChinaEastNorth.tif'
        for dirname in dirnames:
            if name in dirname:
                in_path = make_dir(os.path.join(r'F:\ExperimentData\Zeping5YearsBuildings', str(year), dirname))
                _, filenames = file_name_tif(in_path)
                assert len(filenames) == 1
                in_raster = os.path.join(in_path, filenames[0]+'.tif')
                in_temp = r'F:\ExperimentData\Zeping5YearsBuildings\RoIs\ClipROI' + '\\' + name + '.shp'
                out_path = make_dir(os.path.join(r'F:\ExperimentData\Zeping5YearsBuildings\61Cities', str(year), dirname))
                out_raster = os.path.join(out_path, name+'.tif')
                if os.path.isfile(out_raster) is not True:
                    arcpy.Clip_management(in_raster, in_template_dataset=in_temp, out_raster=out_raster, nodata_value=0)

# 2020 Zhengzhou