#RasterToPolygon_conversion (in_raster, out_polygon_features, {simplify}, {raster_field})
import os
import arcpy
from arcpy import env
from tools import make_dir, file_name_tif
# Set environment settings
# env.workspace = "D:\PythonProjects\DataProcess\Data\TEST_BSG\Beijing"
from tools import *

citynames = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
             'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
             'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
             'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
             'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
            'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan',  #]  # 'Shenyang',
             'Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
             'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Changsha', 'Huizhou', 'Lanzhou', 'Luoyang'
             ]
citynames = ['Changsha']
# make_dir(r"D:\experiment\results\Version2.0-Unet\UNet_M3Net_SSN_296_TESTBSG\shps")
work_dirs = [r'D:\experiment\results\Version1.0-Mask\Maskres50_result_V3.8Buffer30_leftright0_15city_92\shps']
# work_dirs = [r'D:\experiment\results\Version1.0-Mask\UNet_M3Net_SSN_296\shps']

for work_dir in work_dirs:
    filepaths, filenames = file_name_tif(work_dir)
    for ii in range(len(filenames)):
        filename = filenames[ii]
        filepath = filepaths[ii]
        filecity = filename.split('_')[0]
        if filecity in citynames:
            inRaster = filepath
            outPolygons = os.path.join(work_dir, filecity+'.shp')
            field = "VALUE"
            arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "NO_SIMPLIFY", field)

# # Set local variables
# inRaster = r"D:\experiment\results\Version2.0-Unet\UNet_M3Net_SSN_296_TESTBSG\Beijing\Beijing_0_10.tif"
# outPolygons = r"D:\experiment\results\Version2.0-Unet\UNet_M3Net_SSN_296_TESTBSG\Shps\Beijing.shp"
# field = "VALUE"
#
# # Execute RasterToPolygon
# arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "NO_SIMPLIFY", field)
# # Set local variables
# inRaster = r"D:\experiment\results\Version2.0-Unet\UNet_M3Net_SSN_296_TESTBSG\Shanghai\Shanghai_0_0.tif"
# outPolygons = r"D:\experiment\results\Version2.0-Unet\UNet_M3Net_SSN_296_TESTBSG\Shps\Shanghai.shp"
# field = "VALUE"
#
# # Execute RasterToPolygon
# arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "NO_SIMPLIFY", field)
#
# # Set local variables
# inRaster = r"D:\experiment\results\Version2.0-Unet\UNet_M3Net_SSN_296_TESTBSG\Guangzhou\Guangzhou_0_0.tif"
# outPolygons = r"D:\experiment\results\Version2.0-Unet\UNet_M3Net_SSN_296_TESTBSG\Shps\Guangzhou.shp"
# field = "VALUE"
#
# # Execute RasterToPolygon
# arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "NO_SIMPLIFY", field)