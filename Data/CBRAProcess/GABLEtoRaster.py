# -*- coding: utf-8 -*-
import arcpy
from tools import *
import sys
import shutil
from arcpy import env
import json
import math
import io
ResOUT = 8.9831528e-005
# sys.stdout = io.TextIOWrapper(sys.stdout, encoding='utf-8')
reload(sys)
sys.setdefaultencoding('utf8')


def generate_shp(poses, save_path):
    Lon_min, Lat_min, Lon_max, Lat_max = poses
    save_path = os.path.join(save_path, "{}_{}_{}_{}".format(Lon_min, Lat_min, Lon_max, Lat_max).replace('.', 'p') + ".shp")
    if os.path.isfile(save_path):
        return

    points=[[Lon_min,Lat_min],[Lon_min,Lat_max],[Lon_max,Lat_max],[Lon_max,Lat_min],[Lon_min,Lat_min]]
    # SR = arcpy.SpatialReference(4490)  # GCS_China_Geodetic_Coordinate_System_2000
    SR = arcpy.SpatialReference(4326)  # GCS_China_Geodetic_Coordinate_System_2000
    ring = arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in points]), SR)
    # 创建features列表，用于存放要素，在内存
    features = []
    # 通过ring（Array）创建Polygon对象
    # 将Polygon要素添加到features列表
    features.append(ring)
    # 调用复制要素工具，将内存中的features列表创建为shapefile
    arcpy.CopyFeatures_management(features, save_path)


def if_in_rectangle(point, rectangle):
    point_x, point_y = point
    if (point_x >= rectangle[0][0] and point_x <= rectangle[2][0] and point_y >= rectangle[0][1] and point_y <= rectangle[2][1]):
        return True
    else:
        return False


class GABLE:
    def __init__(self, fileroot, saveroot):
        self.fileroot = fileroot
        self.saveroot = make_dir(saveroot)
        self.filepaths, self.filenames = self.init_files()
        return

    def init_files(self):
        return file_name_shp(self.fileroot)

    def repair_all(self):
        for ii in range(len(self.filenames)):
            filepath = self.filepaths[ii]
            filename = self.filenames[ii]
            print u"Repairing  " + filename.decode('gbk')
            self.repair(filepath)

    def repair(self, filepath):
        arcpy.RepairGeometry_management(filepath, "DELETE_NULL")

    def to_raster(self, filepath):
        filename = os.path.basename(filepath)
        out_raster = os.path.join(self.saveroot, filename.replace('.shp', '.tif'))
        if os.path.isfile(out_raster):
            return
        else:
            arcpy.FeatureToRaster_conversion(filepath, "height", out_raster, ResOUT)
        # arcpy.PolygonToRaster_conversion(filepath, "height", out_raster,
        #                                  "MAXIMUM_AREA", "NONE", ResOUT)

    def to_raster_61city(self, filepath):
        shppaths, shpnames = file_name_shp(filepath)
        for ii in range(len(shpnames)):
            shpname = shpnames[ii]
            shppath = shppaths[ii]
            if "all" in shpname:
                shppath = shppath.decode('gbk')
                out_raster = shppath[:-4] + '.tif'
                if os.path.isfile(out_raster):
                    continue
                print out_raster
                arcpy.FeatureToRaster_conversion(shppath, "height", out_raster, ResOUT)
            else:
                continue
        # arcpy.PolygonToRaster_conversion(filepath, "height", out_raster,
        #                                  "MAXIMUM_AREA", "NONE", ResOUT)

    def to_raster_all(self):
        for ii in range(len(self.filenames)):
            filepath = self.filepaths[ii]
            filename = self.filenames[ii]
            print u"processing  " + filename.decode('gbk')
            self.to_raster(filepath, filename)

    def get_province_dict(self):
        prov_dict = {}
        for ii in range(len(self.filenames)):
            filepath = self.filepaths[ii]
            filename = self.filenames[ii]
            prov_name = filename.split('_')[0]
            if prov_name not in prov_dict.keys():
                prov_dict[prov_name] = [filepath]
            else:
                prov_dict[prov_name].append(filepath)
        self.prov_dict = prov_dict

    def merge_shp(self, save_root):
        make_dir(save_root)
        self.get_province_dict()
        for key in self.prov_dict.keys():
            prov_paths = self.prov_dict[key]
            save_path = os.path.join(save_root, "{}.shp".format(key))
            if os.path.isfile(save_path):
                continue
            arcpy.Merge_management(prov_paths, save_path)

    def merge_dir(self, file_dir):
        assert os.path.exists(file_dir)
        filepaths, filenames = file_name_shp(file_dir)
        tar_name = filenames[0].decode('gbk')
        tar_path = filepaths[0].decode('gbk')
        # print tar_name
        # print tar_path.replace(tar_name, (tar_name.split('_')[0]+'_all'))
        tar_path = tar_path.replace(tar_name, (tar_name.split('_')[0]+'_all'))
        if os.path.isfile(tar_path):
            return
        arcpy.Merge_management(filepaths, tar_path)

        tar_path_51N = tar_path.replace(tar_name, (tar_name.split('_')[0]+'_all_51N'))
        arcpy.Project_management

    def merge_in_province(self):
        tiffiles, tifnames = file_name_tif(self.saveroot)
        province_dict = {}
        self.mosaic_save_root = self.saveroot+'_mosaic'
        for ii in range(len(tiffiles)):
            tiffile = tiffiles[ii]
            tifname = tifnames[ii]
            province_name = tifname.split('_')[0]
            if province_name not in province_dict.keys():
                province_dict[province_name] = [[tiffile, tifname]]
            else:
                province_dict[province_name].append([tiffile, tifname])
        for province in province_dict.keys():
            all_path = ""
            all_name = []
            for (path, partname) in province_dict[province]:
                all_path += path + ";"
                all_name.append(partname)
            all_path = all_path[:-1]
            arcpy.Mosaic_management(all_path, all_path.split(';')[0], "MAXIMUM", "FIRST")
            mymovefile(all_path.split(';')[0], self.mosaic_save_root)
            os.rename(os.path.join(self.mosaic_save_root, all_name[0]+'.tif'),
                      os.path.join(self.mosaic_save_root, all_name[0].split('_')[0]+'.tif'))

    def merge_whole_country(self, path):
        assert os.path.exists(path)
        env.workspace = path  # 输入栅格所在目录
        rasters = arcpy.ListRasters('*', raster_type='TIF')  # 如果是TIF影像，改下这个参数：raster_type='TIF'
        print ('栅格目录:' + str(rasters))
        # 存储所有的栅格文件名
        data = []
        for raster in rasters:
            data.append(raster)
        # 去掉第一个
        data2 = data[1:]
        # 第一个参数为除去第一个以外的所有栅格，第二个参数为第一个栅格即要合并到的栅格（拼接到第一个栅格中）
        if len(data) > 1:
            arcpy.Mosaic_management(data2, data[0])
            print('拼接完成:' + str(env.workspace) + os.sep + str(data[0]))
            # 删除其他拼接前的栅格，只保留拼接后的栅格数据集
            # for otherRaster in data2:
            #     removeGivenFile(str(env.workspace) + os.sep + str(otherRaster))

    def clip_other_product(self, filepath, clip_name, save_root):
        self.get_bboxes()
        bbox = self.bboxes[clip_name]
        save_name = os.path.split(filepath)[-1].replace(".tif", "_clip_by_GABLE.tif")
        save_path = os.path.join(save_root, save_name)
        Lon_min, Lat_min, Lon_max, Lat_max = bbox
        arcpy.Clip_management(in_raster=filepath, rectangle='{} {} {} {}'.format(Lon_min, Lat_min, Lon_max, Lat_max),
                              out_raster=save_path)

    def split_by_fishnet(self, fishnet_file=None, save_root=r''):
        for ii in range(len(self.filepaths)):
            filepath = self.filepaths[ii]
            filename = self.filenames[ii]
            print u"Splitting  " + filename.decode('gbk')
            save_path = os.path.join(save_root, filename)
            make_dir(save_path)
            arcpy.Split_analysis(filepath, fishnet_file, "Name", save_path)

    def clip_single(self, clip_file, target_name, save_root):
        for ii in range(len(self.filepaths)):
            filepath = self.filepaths[ii]
            filename = self.filenames[ii]
            filename = u"" + filename.decode('gbk')
            if target_name not in filename:
                continue
            else:
                print u"CLIPPING  " + filename + "=====" + target_name

                make_dir(save_root)
                save_path = os.path.join(save_root, filename+"_clip.shp")
                if os.path.isfile(save_path):
                    continue
                arcpy.Clip_analysis(filepath, clip_file, save_path)

    def clip_by_fishnet(self, fileroot=None, fishnet_json=None, clip_root=None):
        self.get_bboxes()
        self.clip_root = make_dir(clip_root)
        if fileroot is not None:
            self.filepaths, self.filenames = file_name_shp(fileroot)
        with open(fishnet_json, 'r') as fishnet:
            fishnet_data = json.load(fishnet)
            for ii in range(len(self.filepaths)):
                filepath = self.filepaths[ii]
                filename = self.filenames[ii]
                print u"Clipping  " + filename.decode('gbk')

                bbox_tmp = self.bboxes[filename]
                region_rectangle = [(bbox_tmp[0], bbox_tmp[1]), (bbox_tmp[2], bbox_tmp[1]),
                                    (bbox_tmp[2], bbox_tmp[3]), (bbox_tmp[0], bbox_tmp[3])]

                for grid in fishnet_data:

                    lon_min, lat_min, lon_max, lat_max = grid
                    clip_shp = os.path.join(self.fishnet_root,
                                            "{}_{}_{}_{}".format(lon_min, lat_min, lon_max, lat_max).replace('.',
                                                                                                             'p') + ".shp")
                    # out_raster = os.path.join(save_path, filename+".shp")
                    save_shp = os.path.join(self.clip_root, filename + "_{}_{}_{}_{}".format(lon_min, lat_min, lon_max,
                                                                                             lat_max).replace('.',
                                                                                                              'p') + ".shp")
                    if os.path.isfile(save_shp):
                        # print "YESSSS"
                        continue

                    if_in = False
                    # for point in [[lon_min, lat_min], [lon_min, lat_max], [lon_max, lat_max], [lon_max, lat_min]]:
                        # if if_in_rectangle(point, region_rectangle):
                    if if_rectanle1_in_rectangle2(bbox_tmp, grid) or if_rectanle1_in_rectangle2(grid, bbox_tmp):
                        if_in = True

                    if if_in:
                        # pass
                        arcpy.Clip_analysis(filepath, clip_shp, save_shp)

    def init_bboxes(self):
        self.bboxes = {}

    def generate_all_fishnet(self, fishnet_root, fishnet_file="ChinaFishNet.json"):
        print "Generating ChinaFishNet Patterns"
        self.fishnet_root = make_dir(fishnet_root)
        with open(fishnet_file, 'r') as fishnet:
            fishnet_data = json.load(fishnet)
            for grid in fishnet_data:
                generate_shp(grid, save_path=fishnet_root)

    def get_bboxes(self):
        print "Get Bounding Box of shpfiles"
        self.init_bboxes()
        for ii in range(len(self.filepaths)):
            # 获取shp文件的外包矩形
            filepath = self.filepaths[ii]
            filename = self.filenames[ii]
            extent = arcpy.Describe(filepath).extent
            self.bboxes[filename] = [extent.XMin, extent.YMin, extent.XMax, extent.YMax]
            # 输出矩形坐标
            # print("XMin:", extent.XMin)
            # print("YMin:", extent.YMin)
            # print("XMax:", extent.XMax)
            # print("YMax:", extent.YMax)

    def to_wgs84_dir(self, filedir, save_root):
        out_CS = arcpy.SpatialReference('WGS 1984')

        filepaths, filenames = file_name_shp(filedir)
        for ii in range(len(filepaths)):
            filepath = filepaths[ii]
            filename = filenames[ii]
            print filepath.decode('gbk')
            spatial_ref = arcpy.Describe(filepath).spatialReference
            if 'GCS_WGS_1984' not in spatial_ref.exportToString().split('[')[1].split(',')[0]:
                # pass
                save_path = os.path.join(save_root, filename+'.shp')
                print u"Projecting  " + filename.decode('gbk')
                if os.path.isfile(save_path):
                    continue
                arcpy.Project_management(filepath, save_path, out_CS)
            else:
                for suffix in ['.dbf', '.prj', '.shp', '.shp.xml', '.shx', '.sbn', '.sbx']:
                    from_file = filepath.replace('.shp', suffix)
                    print from_file, save_root
                    if os.path.isfile(from_file):
                        mycopyfile(from_file, save_root)

    def join_by_Amap(self, filepath, Amap_path, save_path):
        if os.path.isfile(save_path):
            return
        arcpy.SpatialJoin_analysis(Amap_path, filepath, save_path)

    def to_wgs84_all(self):
        for ii in range(len(self.filepaths)):
            filepath = self.filepaths[ii]
            filename = self.filenames[ii]
            spatial_ref = arcpy.Describe(filepath).spatialReference
            # print(spatial_ref.exportToString().split('[')[1].split(',')[0])
            if 'GCS_WGS_1984' not in spatial_ref.exportToString().split('[')[1].split(',')[0]:
                print(spatial_ref.exportToString().split('[')[1].split(',')[0])
                for suffix in ['dbf', 'prj', 'shp', 'shp.xml', 'shx']:
                    from_file = filepath.replace('shp', suffix)
                    mymovefile(from_file, r'G:\ProductData\GABLE_prj2000')
                # save_path = filepath[:-4] + '_wgs84.shp'
                # if os.path.isfile(save_path):
                #     continue
                # print u"Projecting  " + filename.decode('gbk')
                # arcpy.Project_management(filepath, save_path, out_CS)


if __name__ == '__main__':
    # rectangle = [(0, 0), (4, 0), (4, 2), (0, 2)]
    # point = (0, 1)
    # print if_in_rectangle(point, rectangle)

    # G = GABLE(fileroot=r'G:\GABLE_left_regions_wgs84', saveroot=r'G:\ProductData\GABLE\CHINA_PROCESS')
    G = GABLE(fileroot=r'G:\ProductData\3DGLOBFP\China\CHINA', saveroot=r'G:\ProductData\3DGLOBFP\China\CHINA_PROCESS')
    # G = GABLE(fileroot=r'G:\ProductData\East_Asian_buildings\China_wgs84', saveroot=r'G:\ProductData\East_Asian_buildings\CHINA_PROCESS')

    # G.merge_shp(save_root=r'G:\ProductData\GABLE_province')
    # G.split_by_fishnet(fishnet_file=r'D:\画图\全国省份行政区划数据\china_fishnet_0dot5_2000.shp',
    #                    save_root=r'G:\ProductData\GABLE_SPLIT')
    # G.to_wgs84_all()
    # G.generate_all_fishnet(fishnet_root=r'G:\ProductData\CHINA_fishnet_0p5', fishnet_file="China_fishnet_0p5_wgs_84.json")
    G.fishnet_root = r'G:\ProductData\CHINA_fishnet_0p5'
    # G.clip_by_fishnet(fishnet_json="China_fishnet_0p5_wgs_84.json", clip_root=r'G:\ProductData\3DGLOBFP\China\CHINA_CLIP')
    G.clip_by_fishnet(fishnet_json="China_fishnet_0p5_wgs_84.json", clip_root=r'G:\ProductData\3DGLOBFP\China\CHINA_CLIP')
    # G.clip_by_fishnet(fishnet_json="China_fishnet_0p5_wgs_84.json", clip_root=r'G:\ProductData\East_Asian_buildings\China_0p5')
    # arcpy.RepairBadGeometry(r'G:\ProductData\GABLE\广东省_part1.shp')

    # G.repair_all()
    # G.repair(r'G:\ProductData\GABLE_TEST\GABLE_left_regions (2)\广东省_part1.shp')
    # out_CS = arcpy.SpatialReference('WGS 1984')
    #
    # arcpy.Project_management(r'G:\ProductData\GABLE_TEST\GABLE_left_regions\广东省_part1.shp',
    #                          r'G:\ProductData\GABLE_TEST\GABLE_left_regions\广东省_part1_wgs84.shp', out_CS)
    # G.to_raster_all()
    # G.to_raster(filepath=r'G:\ProductData\GABLE\北京市_part2.shp', filename=r'北京市_part2')
