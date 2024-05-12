# # -*- coding: utf-8 -*-
# from ShpCreator import *
# import shutil
# from glob import glob
# from ExcelReader import *
#
# Widths = {
#     'GAOFEN_1': 30,
#     'GAOFEN_2': 22.5,
#     'GAOFEN_3': 25,
#     'GAOFEN_4': 200,
#     'GAOFEN_5': 30,
#     'GAOFEN_6': 30,
#     'GAOFEN_7': 10,
#     'GAOFEN_DM': 7.5,
#     'TIANHUI_1': 30,
#     'TIANHUI_2': 15,
#     'HAISI_1': 50,
#     'JILIN': 75,
#     'ZIYUAN_3': 25,
#     'ZIYUAN_1': 58,
#     'GAOJING': 6,
#
#     'SENTINEL_2': 145,
#     'LANDSAT': 92,
#     'SPOT': 30,
#     'IKONOS': 5.7,
#     'WORLDVIEW_1': 9,
#     'WORLDVIEW_3': 6.5,
#     'NOVASAR_1': 25,
#     'RADARSAT_2': 25,
#     'TERRASAR': 15,
#     'TANDEM': 15,
#     'ALOS_2': 15,
#     'ARIRANG_5': 50,
#     'COSMO_SKYMED': 50,
#
# }
#
# RES = {
#     'GAOFEN_1': 8,
#     'GAOFEN_2': 3.2,
#     'GAOFEN_3': 5,
#     'GAOFEN_4': 50,
#     'GAOFEN_5': 20,
#     'GAOFEN_6': 8,
#     'GAOFEN_7': 2.6,
#     'GAOFEN_DM': 2,
#     'TIANHUI_1': 10,
#     'TIANHUI_2': 3,
#     'HAISI_1': 1,
#     'JILIN': 2.88,
#     'ZIYUAN_3': 5.8,
#     'ZIYUAN_1': 10,
#     'GAOJING': 1,
#
#     'SENTINEL_2': 10,
#     'LANDSAT': 30,
#     'SPOT': 6,
#     'IKONOS': 4,
#     'WORLDVIEW_1': 1.8,
#     'WORLDVIEW_3': 1.2,
#     'NOVASAR_1': 20,
#     'RADARSAT_2': 25,
#     'TERRASAR': 3,
#     'TANDEM': 1,
#     'ALOS_2': 10,
#     'ARIRANG_5': 20,
#     'COSMO_SKYMED': 15,
# }
#
# Dome_widths = {
#     'GAOFEN_1': 30,
#     'GAOFEN_2': 22.5,
#     'GAOFEN_3': 25,
#     'GAOFEN_4': 200,
#     'GAOFEN_5': 30,
#     'GAOFEN_6': 30,
#     'GAOFEN_7': 10,
#     'GAOFEN_DM': 7.5,
#     'TIANHUI_1': 30,
#     'TIANHUI_2': 15,
#     'HAISI_1': 50,
#     'JILIN': 75,
#     'ZIYUAN_3': 25,
#     'ZIYUAN_1': 58,
#     'GAOJING': 6,
#
#
# }
#
# Fore_widths = {
#
#     'SENTINEL_2': 145,
#     'LANDSAT': 92,
#     'SPOT': 30,
#     'IKONOS': 5.7,
#     'WORLDVIEW_1': 9,
#     'WORLDVIEW_3': 6.5,
#     'NOVASAR_1': 25,
#     'RADARSAT_2': 25,
#     'TERRASAR': 15,
#     'TANDEM': 15,
#     'ALOS_2': 15,
#     'ARIRANG_5': 20,
#     'COSMO_SKYMED': 15,
# }
#
#
# class OrbitsThread:
#     def __init__(self, name, kml_root, from_date, to_dates, range_locs, min_res):
#         """
#         至少应该有一个国内卫星和一个国外卫星
#         输入kml文件的root，通过whole_thread可以直接得到所有结果
#         :param name: 灾害名称
#         :param kml_root:  kml的root文件夹 （以KML结尾， kml文件放在 kml_root/name/from_date_to_dates[i]下）
#         :param from_date: 卫星规划起始时间
#         :param to_dates:  结束时间
#         :param range_locs:  对应的区域范围
#         :param min_res:  最小的分辨率限制
#         """
#         self.name = name  # the name of the project
#         self.kml_root = make_dir(os.path.join(kml_root, name))  # "KMLs/name"
#         self.from_date = from_date
#         self.to_dates = to_dates
#         self.min_res = min_res
#         self.init_save_dirs()
#         self.generate_range_shp(range_locs)
#
#     def whole_thread(self):
#         print "——————KML to DB——————"
#         self.kml_dbs()
#         print "——————DB to SHP——————"
#         self.db_shps()
#         print "-—Clear Error Points—-"
#         self.clear_error_points(thd=180)
#         print "————————Clip—————————"
#         self.clip_to_ranges()
#         print "———————Buffer————————"
#         self.buffers()
#         print "———————Merge——————————"
#         self.merges()
#         print "——————Statistic———————"
#         self.clip_statistics(shp_path_=self.dome_root)
#         self.clip_statistics(shp_path_=self.fore_root)
#
#         print "Chinese Satellites:————————————————————"
#         self.clip_statistics(shp_path_=self.dome_root)
#         print "Other Satellites:——————————————————————"
#         self.clip_statistics(shp_path_=self.fore_root)
#
#     def init_save_dirs(self):
#         db_ = make_dir(self.kml_root.replace('KMLs', "DBs"))
#         shp_ = make_dir(self.kml_root.replace('KMLs', "SHPs"))
#         res_ = make_dir(self.kml_root.replace('KMLs', "RESULTs"))
#         range_ = make_dir(shp_.replace(self.name, "Range"))
#         clear_ = shp_ + '_CLEAR'
#
#         self.clear_root = clear_
#         self.db_root = db_
#         self.shp_root = shp_
#
#         self.range_root = range_
#         self.range_file = os.path.join(range_, "{}.shp".format(self.name))
#
#         range_path_ = make_dir(os.path.join(self.clear_root, "TracksinRange"))
#         self.range_track_root = range_path_
#
#         save_path_ = make_dir(r"{}\Buffer_minres{}".format(res_, self.min_res))
#         self.results_root = save_path_
#
#         dome_path_ = make_dir(r"{}\Buffer_minres{}".format(res_+'_Dome', self.min_res))
#         self.dome_root = dome_path_
#
#         fore_path_ = make_dir(r"{}\Buffer_minres{}".format(res_+'_Fore', self.min_res))
#         self.fore_root = fore_path_
#
#     def generate_range_shp(self, locs):
#         SC = ShpCreator(locations=locs, save_path=self.range_root)
#         SC.create_rectangle(name='{}.shp'.format(self.name))
#
#     def kml_dbs(self):
#         for end_date in self.to_dates:
#             kml = r"{}\{}_{}".format(self.kml_root, self.from_date, end_date)
#             db = make_dir(r"{}\{}_{}".format(self.db_root, self.from_date, end_date))
#             self.kml_db(kml, db)
#
#     def kml_db(self, kml, db):
#         # Set workspace (where all the KMLs are) 放kml文件的文件夹，如果kml文件过多，建议50个kml一个文件夹，多执行几个py就行，否则500个kml可能要一个小时
#         arcpy.env.workspace = kml
#         # Set local variables and location for the consolidated file geodatabase 导出的geodata文件夹
#         outLocation = db
#         # Create the master FileGeodatabase
#         # Convert all KMZ and KML files found in the current workspace 找出kml文件，速度不快的
#         for kmz in arcpy.ListFiles('*.kml'):
#             arcpy.KMLToLayer_conversion(kmz, outLocation)
#
#     def db_shps(self):
#         for end_date in self.to_dates:
#             out_path = make_dir(r"{}\{}_{}".format(self.shp_root, self.from_date, end_date))
#             db = make_dir(r"{}\{}_{}".format(self.db_root, self.from_date, end_date))
#             self.db_shp(out_path, db)
#
#     @staticmethod
#     def db_shp(out_path, db):
#         arcpy.env.workspace = db
#         # Loop through all the FileGeodatabases within the workspace
#         wks = arcpy.ListWorkspaces('*', 'FileGDB')
#         # Skip the Master GDB
#         for fgdb in wks:
#             fcz = []
#             satellite_name = fgdb.split('\\')[-1].split('.')[0].replace('-', '_')
#             save_name = os.path.join(out_path, '{}.shp'.format(satellite_name))
#             if os.path.exists(save_name):
#                 continue
#             # Change the workspace to the current FileGeodatabase
#             arcpy.env.workspace = fgdb
#             # For every Featureclass inside, copy it to the Master and use the name from the original fGDB
#             featureClasses = arcpy.ListFeatureClasses('*', '', 'Placemarks')
#             for fc in featureClasses:
#                 if fc == 'Polylines':  # 只要线段，点不要，这个看自己的需求
#                     fcCopy = fgdb + os.sep + 'Placemarks' + os.sep + fc
#                     fcz.append(fcCopy)
#             arcpy.Merge_management(fcz, save_name)
#
#     def clear_error_points(self, thd=180):
#         for end_date in self.to_dates:
#             db = r"{}\{}_{}".format(self.shp_root, self.from_date, end_date)
#             filepaths, filenames = file_name_shp(db)
#             for ii in range(len(filepaths)):
#                 filepath = filepaths[ii]
#                 filename = filenames[ii]
#                 features = self.filter_points(filepath, thd)
#                 SC = ShpCreator(locations=features,
#                                 save_path=make_dir(r"{}\{}_{}".format(self.clear_root, self.from_date, end_date)))
#                 SC.create_polylines(filename)
#
#     @staticmethod
#     def filter_points(fc, thd):
#         features = [[]]
#         index = 0
#         # 遍历所有图层中的要素，并根据要素名构建输出文件名,
#         field_names = arcpy.ListFields(fc)
#         for field in field_names:
#             if field.name not in ['FID', 'Shape', 'shape length', 'shape area']:
#                 with arcpy.da.SearchCursor(fc, ["SHAPE@", field.name]) as cursor:
#                     for row in cursor:
#                         array = row[0].getPart(0)
#                         num_points = array.count
#                         for i in range(1, num_points):
#                             A = arcpy.Point(array.getObject(i - 1).X, array.getObject(i - 1).Y)
#                             B = arcpy.Point(array.getObject(i).X, array.getObject(i).Y)
#                             features[index].append([A.X, A.Y])
#                             if abs(A.X - B.X) > thd:  # 180是自己设置的点间经度差值的过滤阈值
#                                 features.append([])
#                                 index += 1
#         return features
#
#     def clip_to_ranges(self):
#         for end_date in self.to_dates:
#             shp_path = make_dir(r'{}\{}_{}'.format(self.clear_root, self.from_date, end_date))
#             save_root = make_dir(r'{}\{}_{}'.format(self.range_track_root, self.from_date, end_date))
#             file_paths, file_names = file_name_shp(shp_path)
#             for ii in range(len(file_paths)):
#                 file_path = file_paths[ii]
#                 file_name = file_names[ii]
#                 save_path = os.path.join(save_root, '{}.shp'.format(file_name))
#                 if os.path.exists(save_path):
#                     continue
#                 self.clip_to_range(file_path, self.range_file, save_path)
#
#     @staticmethod
#     def clip_to_range(in_file, clip_file, save_file):
#         try:
#             arcpy.Clip_analysis(in_file, clip_file, save_file)
#         except Exception as e:
#             print e
#             print in_file + "has no tracks here"
#             return save_file
#
#     def buffers(self):
#         for end_date in self.to_dates:
#             line_file_path = r'{}\{}_{}'.format(self.range_track_root, self.from_date, end_date)
#             save_path = make_dir(r'{}\{}_{}'.format(self.results_root, self.from_date, end_date))
#
#             filepaths, filenames = file_name_shp(line_file_path)
#             for ii in range(len(filepaths)):
#                 filepath = filepaths[ii]
#                 filename = filenames[ii]
#                 self.buffer(filepath, filename, save_path)
#                 # print filename
#
#     def buffer(self, line_shp, sate_name, save_path):
#         name_known = False
#         for key in Widths.keys():
#             if key in sate_name:
#                 name_known = True
#                 name = key
#         assert name_known is True, "{} Not Known".format(sate_name)
#
#         width = Widths[name]
#         res = RES[name]
#         if res >= self.min_res:
#             return
#         out_buffer_shp = os.path.join(save_path, '{}.shp'.format(sate_name))
#         if os.path.isfile(out_buffer_shp):
#             return
#         arcpy.Buffer_analysis(line_shp, out_buffer_shp, "{} KILOMETERS".format(width), "FULL", "FLAT", "NONE")
#
#     def merges(self):
#         Dome_lists = Dome_widths.keys()
#         Fore_lists = Fore_widths.keys()
#         for end_date in self.to_dates:
#             dome_file_paths = []
#             fore_file_paths = []
#             dome_file_names = []
#             fore_file_names = []
#             line_file_path = r'{}\{}_{}'.format(self.results_root, self.from_date, end_date)
#             save_path_dome = make_dir(r'{}\{}_{}'.format(self.dome_root, self.from_date, end_date))
#             save_path_fore = make_dir(r'{}\{}_{}'.format(self.fore_root, self.from_date, end_date))
#             filepaths, filenames = file_name_shp(line_file_path)
#             for ii in range(len(filenames)):
#                 filepath = filepaths[ii]
#                 filename = filenames[ii]
#                 for key in Dome_lists:
#                     if key in filename:
#                         dome_file_paths.append(filepath)
#                         dome_file_names.append(filename)
#                 for key in Fore_lists:
#                     if key in filename:
#                         fore_file_paths.append(filepath)
#                         fore_file_names.append(filename)
#             assert (len(dome_file_paths) + len(fore_file_paths)) == len(filenames)
#             # print dome_file_paths, fore_file_paths
#             assert len(dome_file_paths) >= 1, "国内卫星至少应有一个"
#             assert len(fore_file_paths) >= 1, "国外卫星至少应有一个"
#
#             if len(dome_file_paths) > 1:
#                 self.merge(dome_file_paths, os.path.join(save_path_dome, 'ChineseSatellites.shp'))
#             else:
#                 src_file_list = glob(line_file_path + '\\' + dome_file_names[0] + '*')  # glob获得路径下所有文件，可根据需要修改
#                 for srcfile in src_file_list:
#                     shutil.move(srcfile, save_path_dome)
#             if len(fore_file_paths) > 1:
#                 self.merge(fore_file_paths, os.path.join(save_path_fore, 'OtherSatellites.shp'))
#             else:
#                 src_file_list = glob(line_file_path + '\\' + fore_file_names[0] + '*')  # glob获得路径下所有文件，可根据需要修改
#                 for srcfile in src_file_list:
#                     shutil.move(srcfile, save_path_fore)
#
#     @staticmethod
#     def merge(merge_list, save_path):
#         arcpy.Merge_management(merge_list, save_path)
#
#     def clip_statistics(self, shp_path_):
#
#         cursor = arcpy.da.SearchCursor(self.range_file, ["SHAPE@AREA"])
#         area_whole = 0
#         for row in cursor:
#             area = row[0]
#             area_whole += area
#         del cursor
#
#         save_path_1 = make_dir(r"{}_Dissolve".format(shp_path_))
#         save_path_2 = make_dir(r"{}_Restrict".format(shp_path_))
#
#         for end_date in self.to_dates:
#             shp_path = make_dir(r'{}\{}_{}'.format(shp_path_, self.from_date, end_date))
#             save_root1 = make_dir(r'{}\{}_{}'.format(save_path_1, self.from_date, end_date))
#             save_root2 = make_dir(r'{}\{}_{}'.format(save_path_2, self.from_date, end_date))
#
#             file_paths, file_names = file_name_shp(shp_path)
#             for ii in range(len(file_paths)):
#                 file_path = file_paths[ii]
#                 file_name = file_names[ii]
#                 save_path1 = os.path.join(save_root1, '{}.shp'.format(file_name))
#                 save_path2 = os.path.join(save_root2, '{}.shp'.format(file_name))
#                 # print save_path
#
#                 if os.path.isfile(save_path1) | os.path.isfile(save_path2):
#                     cursor = arcpy.da.SearchCursor(save_path2, ["SHAPE@AREA"])
#                     area_total = 0
#                     for row in cursor:
#                         area = row[0]
#                         area_total += area
#                     del cursor
#                     porp = np.round(area_total / area_whole, 4) * 100
#                     print "{} to {}, Satellites covers {:.2f}% of the interesrted area".format(self.from_date, end_date,
#                                                                                                porp)
#                     continue
#
#                 self.clip_statistic(file_path, self.range_file, save_path1, save_path2)
#
#     @staticmethod
#     def clip_statistic(in_file, clip_file, save_path1, save_path2):
#         try:
#             arcpy.Dissolve_management(in_file, save_path1)
#             arcpy.Clip_analysis(save_path1, clip_file, save_path2)
#         except Exception as e:
#             print e
#             return save_path1
#
#
# if __name__ == '__main__':
#     O = OrbitsThread(name="Landslide_SAR", kml_root=r'G:\STKDATA\Test\KMLs', from_date=14, to_dates=[15, 17, 19, 21],
#                      min_res=21, range_locs=[[61.224444444444, 23.209166666666, 86.06, 47.5805555555]])
#     O.whole_thread()
