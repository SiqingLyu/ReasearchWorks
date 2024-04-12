# -*- coding: utf-8 -*-

from tools import *
import numpy
import os
import arcpy
from arcpy import env
from arcpy.sa import *

# SHPNAME = {
#     'Dome': "Domestic_prj_clip_combine.shp",
#     'Fore': "Foreign_prj_clip_combine.shp"
# }
# SAVENAME = {
#     'Dome': "Domestic_prj_clip_combine.shp",
#     'Fore': "Foreign_prj_clip_combine.shp"
# }
# PRINT_NAME = {
#     'Dome': "Chinese",
#     'Fore': "Other"
# }
# shpfields = ["AreaKM2"]
# AREA_BOX = 424677.788507
# out_coordinate_system = r'G:\Pakistan\WGS_1984_EASE_Grid_Global.prj'
# clip_features = r'G:\STKDATA\SHPs\Range\Glacier_collapse_general_range_2.shp'
# root_path = r'G:\STKDATA'
# for end_date in [24, 26, 28, 30]:
#     for region in ["Dome", "Fore"]:
#         areas = []
#         path = os.path.join(root_path, "Buffer_minres10_{}".format(region), "23_{}".format(end_date), SHPNAME[region])
#         save_path = os.path.join(root_path, "Buffer_minres10_{}".format(region), "23_{}".format(end_date), SAVENAME[region])
#
#         # arcpy.Project_management(path, save_path, out_coordinate_system)
#
#         # arcpy.Clip_analysis(path, clip_features, save_path)
#
#         # arcpy.AddField_management(path, "AreaKM2", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
#         # arcpy.CalculateField_management(path, "AreaKM2", "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")
#
#         # arcpy.Dissolve_management(path, save_path)
#
#         shprows = arcpy.SearchCursor(path, shpfields)
#         while True:
#             shprow = shprows.next()
#             if not shprow:
#                 break
#             areas.append(shprow.AreaKM2)
#
#         sum_area = 0.
#         for i in range(0, len(areas)):
#             # print areas[i]
#             sum_area += areas[i]
#         rate = np.round(sum_area / AREA_BOX, 4)
#         print "23 - 24, MAR, {} HR* Satellites cover {} km^2, {}% of the range".format(PRINT_NAME[region], sum_area, rate*100)

# 环的组成点集合
# points= [[71.584722, 34.244166], [74.166666, 33.224444], [77.501944, 38.419444], [74.7572222, 39.3922222], [71.584722, 34.244166]]
points= [[114.0, 36.0], [119.0, 36.0], [119.0, 41.0], [114.0, 41.0], [114.0, 36.0]]
SR = arcpy.SpatialReference(4326)  # WGS84

# 组成环的Array对象
ring=arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in points]), SR)
# 创建features列表，用于存放要素，在内存
features=[]
# 通过ring（Array）创建Polygon对象
# 将Polygon要素添加到features列表
features.append(ring)

# 调用复制要素工具，将内存中的features列表创建为shapefile
arcpy.CopyFeatures_management(features, r".\Hebei.shp")


# out_coor_system = r'C:\Users\Dell\AppData\Roaming\ESRI\Desktop10.2\ArcMap\Coordinate Systems\WGS_1984_UTM_Zone_51N.prj'
# #
# names = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
#          'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
#          'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
#          'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
#          'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
#           'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
#          'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan',
#          'Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing',
#          'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Shenyang']
#           #'Shenyang', 'Yantai',
# names = ['Shenyang']
# # # names = ['Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing',
# # #              'Wuxi', 'Wuhu', 'Xuzhou', 'Yantai', 'Zhuhai', 'Shenyang']
# # # names = ['Changsha', 'Huizhou', 'Lanzhou', 'Luoyang']
# # print (len(names))
# # in_raster_dir = r'D:\Dataset\@62allcities\VVHs_nodata0'
# # clip_raster_dir = r'D:\Dataset\@62allcities\Label_bk0_nodata0'
# # for name in names:
# #     in_raster = os.path.join(in_raster_dir, name+'.tif')
# #     in_temp = clip_raster_dir + '\\' + name + '.tif'
# #     out_raster = r'D:\Dataset\@62allcities\VVHs_nodata0_restricted' + '\\' + name + '.tif'
# #     arcpy.Clip_management(in_raster, in_template_dataset=in_temp, out_raster=out_raster, nodata_value=0.0)
#
#
# file_path = r'D:\Dataset\77citiesrefernce\Shanghai\Shanghai_fengxian'
# # file_path_ = r'D:\Dataset\CNBHChina62city'
# UTM_path = r'D:\Dataset\77citiesrefernce\Shanghai\Shanghai_fengxian_51N'
# make_dir(UTM_path)
# seasons = ['Spring', 'Summer', 'Autumn', 'Winter', '_allyear']
# # out_coor_system = r'C:\Users\Dell\AppData\Roaming\ESRI\Desktop10.2\ArcMap\Coordinate Systems\WGS 1984 UTM Zone 37N.prj'
# # for name in names:
# #     print 'processing' + name
# #     in_raster = os.path.join(file_path_, name + '.tif')
# #     out_raster = os.path.join(UTM_path, name + '.tif')
# #     arcpy.ProjectRaster_management(in_raster, out_raster, out_coor_system, cell_size=10)
# for season in seasons:
#     print 'processing' + os.path.join(file_path, 'Shanghai_fengxian' + season + '.tif')
#     # make_dir(os.path.join(UTM_path, season))
#     arcpy.ProjectRaster_management(os.path.join(file_path, 'Shanghai_fengxian' + season + '.tif'),
#                                    os.path.join(UTM_path, 'Shanghai_fengxian' + season + '.tif'), out_coor_system, cell_size=10)
#     print 'over'

# for i in range(1,9):
#     in_features = r'D:\Dataset\Turkey\building_raw\building_raw\building_shp\all.shp'
#     clip_features = r'D:\Dataset\Turkey\Clip' + str(i) + '.shp'
#     out_feature_class = r'D:\Dataset\Turkey\allClip' + str(i) + '.shp'
#     arcpy.Clip_analysis (in_features, clip_features, out_feature_class)

# in_features = r'D:\Dataset\Turkey\building_raw\building_raw\building_shp\all_dissolve.shp'
# clip_features = r'D:\Dataset\Turkey\Processed\Region\Yisilaxiye.shp'
# out_feature_class = r'D:\Dataset\Turkey\Processed\Clip_shps\Yisilaxiye.shp'
# arcpy.Clip_analysis (in_features, clip_features, out_feature_class)

#
# out_dataset = r'D:\Dataset\Turkey\Processed\Clip_shps\Aertezumu.shp'
# field = 'FIRST_grid'
# out_raster = r'D:\Dataset\Turkey\Processed\Clip_imgs\Aertezumu.tif'
# arcpy.FeatureToRaster_conversion(out_dataset, field, out_raster, cell_size=1)

# names = ['Sanya', 'Haikou', 'Zhuhai_clip', 'Aomen', 'Xianggang', 'Zhongshan', 'Shenzhen', 'Dongguan', 'Foshan', 'Nanning', 'Huizhou', 'Shantou', 'Guangzhou']
# names = ['Jinhua', 'Ningbo', 'Shaoxing', 'Hangzhou', 'Jiaxing', 'Shanghai', 'Suzhou', 'Wuhu', 'Wuxi', 'Changzhou', 'Hefei', 'Nanjing', 'Nantong', 'Yangzhou']
# names = ['Wuhan', 'Luoyang', 'Zhengzhou', 'Xuzhou', 'Jinan', 'Shijiazhuang', 'Taiyuan', 'Baoding', 'Tianjin', 'Beijing', 'Tangshan', 'Huhehaote']
# names = ['Chengdu', 'Chongqing', 'Xian', 'Lanzhou', 'Yinchuan', 'Xining', 'Eerduosi']
# names = ['Changchun', 'Haerbin', 'Dalian', 'Qingdao', 'Yantai']
# print (len(names))
# # in_raster_dir = r'D:\Dataset\@62allcities\VVHs_nodata0'
# clip_raster_dir = r'D:\Dataset\@62allcities\ClipROI'
# for name in names:
#     print 'processing '+ name
#     # in_raster = os.path.join(in_raster_dir, name+'.tif')
#     # in_raster = r'D:\Dataset\全国建筑物高度10m（Wu）数据集\121-127X37-45ChinaEastNorth.tif'
#     in_raster = r'D:\Dataset\WSF3D\WSF3D_V02_BuildingHeight.tif'
#     in_temp = clip_raster_dir + '\\' + name + '.shp'
#     # out_raster = r'D:\Dataset\全国建筑物高度10m（Wu）数据集' + '\\' + name + '.tif'
#     out_raster = r'D:\Dataset\全球90m数据集' + '\\' + name + '.tif'
#     arcpy.Clip_management(in_raster, in_template_dataset=in_temp, out_raster=out_raster, nodata_value=0)



# Filepaths, Filenames = file_name_tif(r'D:\Dataset\CNBH10m')
# print Filepaths
# in_raster = Filepaths[0]
# for ii in range(1, len(Filepaths)):
#     in_raster += ';' + Filepaths[ii]
# print in_raster
# arcpy.MosaicToNewRaster_management(in_raster, r'D:\Dataset\全国建筑物高度10m（Wu）数据集', '0_China.tif',  out_coor_system,  "8_BIT_UNSIGNED", "10", "1", "MAXIMUM","FIRST")

# for i in range(1,9):
#     print 'processing: D:\Dataset\Turkey\Processed\Clip_shps\\allClip'+ str(i)
#     out_dataset = r'D:\Dataset\Turkey\Processed\Clip_shps\allClip' + str(i) + '.shp'
#     field = 'gridcode'
#     out_raster = r'D:\Dataset\Turkey\Processed\Clip_imgs\allClip' + str(i) + '.tif'
#     arcpy.FeatureToRaster_conversion (out_dataset, field, out_raster, cell_size = 1)

# print 'processing 1'
# in_raster = r'G:\ExperimentData\Bi-Temporal\Img\Beijing_SummerallFeatures.tif'
# in_temp = r'G:\ExperimentData\Bi-Temporal\Lab\Beijing.tif'
# out_raster = r'G:\ExperimentData\Bi-Temporal\Img\Beijing_SummerallFeatures_clip.tif'
# arcpy.Clip_management(in_raster, in_template_dataset=in_temp, out_raster=out_raster, nodata_value=0.0, maintain_clipping_extent='MAINTAIN_EXTENT')


# print 'processing 2'
#
# in_raster = r'G:\ExperimentData\Bi-Temporal\Img\Beijing_WinterallFeatures.tif'
# in_temp = r'G:\ExperimentData\Bi-Temporal\Lab\Beijing.tif'
# out_raster = r'G:\ExperimentData\Bi-Temporal\Img\Beijing_WinterallFeatures_clip.tif'
# arcpy.Clip_management(in_raster, in_template_dataset=in_temp, out_raster=out_raster, nodata_value=0.0, maintain_clipping_extent='MAINTAIN_EXTENT')
# print 'processing 3'
#
# in_raster = r'G:\ExperimentData\Bi-Temporal\Img\Beijing_SummerGLCMFeatures.tif'
# in_temp = r'G:\ExperimentData\Bi-Temporal\Lab\Beijing.tif'
# out_raster = r'G:\ExperimentData\Bi-Temporal\Img\Beijing_SummerGLCMFeatures_clip.tif'
# arcpy.Clip_management(in_raster, in_template_dataset=in_temp, out_raster=out_raster, nodata_value=0.0, maintain_clipping_extent='MAINTAIN_EXTENT')
#
# print 'processing 4'
# in_raster = r'G:\ExperimentData\Bi-Temporal\Img\Beijing_WinterGLCMFeatures.tif'
# in_temp = r'G:\ExperimentData\Bi-Temporal\Lab\Beijing.tif'
# out_raster = r'G:\ExperimentData\Bi-Temporal\Img\Beijing_WinterGLCMFeatures_clip.tif'
# arcpy.Clip_management(in_raster, in_template_dataset=in_temp, out_raster=out_raster, nodata_value=0.0, maintain_clipping_extent='MAINTAIN_EXTENT')



# inRaster = r'D:\Dataset\TEST\SH_TEST\Shanghai_all.tif'
# outPolygons = r'D:\Dataset\TEST\SH_TEST\Shanghai_footprint.shp'
# field = 'VALUE'
# # arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "NO_SIMPLIFY", field)
# in_features = outPolygons
# clip_features = r'D:\画图\研究区\北上广ROI\Shanghai_TEST.shp'
# out_feature_class = r'D:\Dataset\TEST\SH_TEST\Shanghai_footprint_clipped.shp'
# # arcpy.Clip_analysis (in_features, clip_features, out_feature_class)
#
# in_dataset = r'D:\Dataset\TEST\SH_TEST\Shanghai_footprint_clipped.shp'
# out_dataset = r'D:\Dataset\TEST\SH_TEST\Shanghai_footprint_clipped_51N.shp'
# # arcpy.Project_management (in_dataset, out_dataset, out_coor_system)
# field = 'GRIDCODE'
# out_raster = r'D:\Dataset\TEST\SH_TEST\Label\Shanghai.tif'
# arcpy.FeatureToRaster_conversion (out_dataset, field, out_raster, cell_size = 10)


# in_features = r'D:\Dataset\GRIP4_Region6_vector_shp\GRIP4_region6.shp'
# for i in range(len(names)):
#     print("processing:", names[i])
#     clip_features = r'D:\Dataset\52Cities\Areas' + '\\' + names[i] + '.shp'
#     out_feature_class = r'D:\Dataset\52Cities\Roads' + '\\' + names[i] + '.shp'
#     if os.path.isfile(out_feature_class):
#         print (names[i],"already exist")
#         continue
#     arcpy.Clip_analysis (in_features, clip_features, out_feature_class)
#
# for i in range(len(names)):
#     print ("processing " + names[i])
#     in_dataset = r'D:\Dataset\@62allcities_min\MUX_RAW\\' + names[i] + '.shp'
#     out_dataset = r'D:\Dataset\@62allcities_min\MUX\\' + names[i] + '.shp'
#     make_dir(r'D:\Dataset\@62allcities_min\MUX\\')
#     arcpy.Project_management (in_dataset, out_dataset, out_coor_system)
#
#
#
#
# for i in range(len(names)):
#     print ('processing ' + names[i])
#     in_features = r'D:\Dataset\11cities\clip_shps_utm_51N\\' + '\\' + names[i] + '.shp'
#     field = 'Floor'
#     out_raster = r'D:\Dataset\11cities\Label' + '\\' + names[i] + '.tif'
#     make_dir(r'D:\Dataset\11cities\Label')
#     arcpy.FeatureToRaster_conversion (in_features, field, out_raster, cell_size = 10)




# file_path = r'D:\Dataset\Mydata_all\SSN'
# UTM_path = file_path + '_UTM'
# make_dir(UTM_path)
# season = ['spring', 'summer', 'autumn', 'winter']
# out_coor_system = r'C:\Users\Dell\AppData\Roaming\ESRI\Desktop10.2\ArcMap\Coordinate Systems\WGS_1984_UTM_Zone_51N.prj'
#
# arcpy.ProjectRaster_management(r'D:\Dataset\Mydata_all\SSN\summer\Guiyang.tif',
#                                r'D:\Dataset\Mydata_all\SSN_UTM\summer\Guiyang.tif', out_coor_system, cell_size=10)
# print 'over'
#
# arcpy.ProjectRaster_management(r'D:\Dataset\Mydata_all\SSN\summer\Xiamen.tif',
#                                r'D:\Dataset\Mydata_all\SSN_UTM\summer\Xiamen.tif', out_coor_system, cell_size=10)
# print 'over'
#
# arcpy.ProjectRaster_management(r'D:\Dataset\Mydata_all\SSN\spring\Shenzhen.tif',
#                                r'D:\Dataset\Mydata_all\SSN_UTM\spring\Shenzhen.tif', out_coor_system, cell_size=10)
# print 'over'
#
# arcpy.ProjectRaster_management(r'D:\Dataset\Mydata_all\SSN\fall\Chengdu.tif',
#                                r'D:\Dataset\Mydata_all\SSN_UTM\fall\Chengdu.tif', out_coor_system, cell_size=10)
# print 'over'


# file_path = r'D:\Dataset\TEST\SH_TEST\Seasons'
# UTM_path = r'D:\Dataset\TEST\SH_TEST\Seasons_51N'
# make_dir(UTM_path)
# for i in range(4):
#     file_path_ = file_path + '\\' + season[i]
#     UTM_path_ = UTM_path + '\\' + season[i]
#     make_dir(UTM_path_)
#     Listfile, allFilename = file_name_tif(file_path_)
#
#     for ii in range(len(allFilename)):
#         tif_filepath = Listfile[ii]
#         tif_fileid = allFilename[ii]
#         # if 'Shenyang' in tif_fileid:
#         input_raster = tif_filepath
#         output_raster = UTM_path_ + '\\' + tif_fileid + '.tif'
#         print("processing:\nin:" + tif_filepath + "\nout:" + output_raster)
#         arcpy.ProjectRaster_management(input_raster, output_raster, out_coor_system, cell_size=10)



#
# i = 0
# for i in range(0, len(names)):
#     in_features = r'D:\Dataset\52Cities\shpfiles\UTM_51M.gdb' + '\\' + names[i]
#     field = 'Floor'
#     make_dir(r'D:\Dataset\52Cities\Label_SR')
#     out_raster = r'D:\Dataset\52Cities\Label_SR' + '\\' + names[i] + '.tif'
#     print (in_features)
#     print (out_raster)
#     arcpy.FeatureToRaster_conversion(in_features, 'Floor', out_raster, cell_size=2.5)





# for i in range(len(names)):
#     print ("processing " + names[i])
#     in_raster = r'D:\Dataset\@62allcities_min\MUX_RAW\\' + names[i] + '.tif'
#     out_raster = r'D:\Dataset\@62allcities_min\MUX\\' + names[i] + '.tif'
#     make_dir(r'D:\Dataset\@62allcities_min\MUX\\')
#     arcpy.ProjectRaster_management (in_raster, out_raster, out_coor_system, cell_size = 10)
#
# for i in range(len(names)):
#     print ("processing " + names[i])
#     in_raster = r'D:\Dataset\@62allcities\MUXs_raw\\' + names[i] + '.tif'
#     out_raster = r'D:\Dataset\@62allcities\MUXs_UTM\\' + names[i] + '.tif'
#     make_dir(r'D:\Dataset\@62allcities\MUXs_UTM\\')
#     arcpy.ProjectRaster_management (in_raster, out_raster, out_coor_system, cell_size = 10)


# for i in range(37, len(names)):
#     print ("processing " + names[i] + ' of longtime')
#     in_raster = r'D:\Dataset\52Cities\Image\longtime\\' + names[i] + '.tif'
#     out_raster = r'D:\Dataset\52Cities\Image\\' + names[i] + '.tif'
#     arcpy.ProjectRaster_management (in_raster, out_raster, out_coor_system, cell_size = 10)
#     print ("processing " + names[i] + ' of Fall')
#     #fall
#     in_raster = fall_dir  + '\\' + names[i] + '.tif'
#     out_raster = fall_UTM  + '\\' + names[i] + '.tif'
#     arcpy.ProjectRaster_management(in_raster, out_raster, out_coor_system, cell_size=10)
#
#     print ("processing " + names[i] + ' of summer')
#     #Summer
#     in_raster = summer_dir  + '\\' + names[i] + '.tif'
#     out_raster = summer_UTM  + '\\' + names[i] + '.tif'
#     arcpy.ProjectRaster_management(in_raster, out_raster, out_coor_system, cell_size=10)
#
#     print ("processing " + names[i] + ' of winter')
#     #winter
#     in_raster = winter_dir  + '\\' + names[i] + '.tif'
#     out_raster = winter_UTM  + '\\' + names[i] + '.tif'
#     arcpy.ProjectRaster_management(in_raster, out_raster, out_coor_system, cell_size=10)