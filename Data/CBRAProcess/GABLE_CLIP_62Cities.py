# -*- coding: utf-8 -*-
"""
这个代码用于处理各种数据在61个城市上的数据
可能需要注意的是，这个代码在计算面积时，可能会报错，
这可能是由于程序执行过程中的不同线程优先级没有合理进行的原因，这个问题可以考虑加入time.sleep在IoU的计算函数之中

"""
from GABLEtoRaster import *
import json
import numpy as np
import time

citynames = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
             'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
             'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
             'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
             'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
            'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan']  #]  # 'Shenyang',
             # 'Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
             # 'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Changsha', 'Huizhou', 'Lanzhou', 'Luoyang'
             # ]
citynames += ['Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
             'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Changsha', 'Huizhou', 'Lanzhou', 'Luoyang']  # "Yantai"
# print citynames
city_dict = {
    "北京": ['Beijing'],
    "江苏": ['Nanjing', 'Changzhou', 'Suzhou', 'Yangzhou', 'Nantong', 'Wuxi', 'Xuzhou'],
    "天津": ['Tianjin'],
    "广东": ['Guangzhou', 'Shenzhen', 'Dongguan', 'Foshan', 'Huizhou', 'Shantou', 'Zhongshan', 'Zhuhai'],
    "重庆": ['Chongqing'],
    "黑龙江": ['Haerbin'],
    "浙江": ['Hangzhou', 'Ningbo', 'Taizhou', 'Wenzhou', 'Jinhua', 'Jiaxing', 'Shaoxing'],
    "云南": ['Kunming'],
    "江西": ['Nanchang'],
    "上海": ['Shanghai'],
    "湖北": ['Wuhan'],
    "福建": ['Xiamen', 'Fuzhou', 'Quanzhou'],
    "陕西": ['Xian'],
    "河南": ['Zhengzhou', 'Luoyang'],
    "澳门": ['Aomen'],
    "河北": ['Baoding', 'Shijiazhuang', 'Tangshan'],
    "吉林": ['Changchun'],
    "湖南": ['Changsha'],
    "四川": ['Chengdu'],
    "辽宁": ['Dalian', 'Shenyang'],
    "内蒙古": ['Eerduosi', 'Huhehaote'],
    "贵州": ['Guiyang'],
    "海南": ['Haikou', 'Sanya'],
    "安徽": ['Hefei', 'Wuhu'],
    "山东": ['Jinan', 'Qingdao'],
    "甘肃": ['Lanzhou'],
    "西藏": ['Lasa'],
    "广西": ['Nanning'],
    "山西": ['Taiyuan'],
    "香港": ['Xianggang'],
    "青海": ['Xining'],
    "宁夏": ['Yinchuan']
}

BF_project = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')

BF_city_dict = {
    "Beijing": ['Beijing'],
    "Jiangsu": ['Nanjing', 'Changzhou', 'Suzhou', 'Yangzhou', 'Nantong', 'Wuxi', 'Xuzhou'],
    "Tianjin": ['Tianjin'],
    "Guangdong": ['Guangzhou', 'Shenzhen', 'Dongguan', 'Foshan', 'Huizhou', 'Shantou', 'Zhongshan', 'Zhuhai'],
    "Chongqing": ['Chongqing'],
    "Heilongjiang": ['Harbin'],
    "Zhejiang": ['Hangzhou', 'Ningbo', 'Taizhou', 'Wenzhou', 'Jinhua', 'Jiaxing', 'Shaoxing'],
    "Yunnan": ['Kunming'],
    "Jiangxi": ['Nanchang'],
    "Shanghai": ['Shanghai'],
    "Hubei": ['Wuhan'],
    "Fujian": ['Xiamen', 'Fuzhou', 'Quanzhou'],
    "Shaanxi": ['Xian'],
    "Henan": ['Zhengzhou', 'Luoyang'],
    "Macau": ['Macau'],
    "Hebei": ['Baoding', 'Shijiazhuang', 'Tangshan'],
    "Jilin": ['Changchun'],
    "Hunan": ['Changsha'],
    "Sichuan": ['Chengdu'],
    "Liaoning": ['Dalian', 'Shenyang'],
    "NeiMongol": ['Ordos', 'Hohhot'],
    "Guizhou": ['Guiyang'],
    "Hainan": ['Haikou', 'Sanya'],
    "Anhui": ['Hefei', 'Wuhu'],
    "Shandong": ['Jinan', 'Qingdao'],
    "Gansu": ['Lanzhou'],
    "Tibet": ['Lhasa'],
    "Guangxi": ['Nanning'],
    "Shanxi": ['Taiyuan'],
    "Hongkong": ['Hongkong'],
    "Qinghai": ['Xining'],
    "Ningxia": ['Yinchuan']
}

change_name_dict = {
    "Haerbin": "Harbin",
    "Aomen": "Macau",
    "Xianggang": "Hongkong",
    "Eerduosi": "Ordos",
    "Huhehaote": "Hohhot",
    "Lasa": "Lhasa"
}

name_change_dict = {
    "Harbin": "Haerbin",
    "Macau": "Aomen",
    "Hongkong": "Xianggang",
    "Ordos": "Eerduosi",
    "Hohhot": "Huhehaote",
    "Lhasa": "Lasa"
}

def find_all_file(fileroot):
    filepaths, filenames = file_name_shp(fileroot)
    for ii in range(len(filepaths)):
        filepath = filepaths[ii]
        filename = filenames[ii]
        if "_all" in filename:
            return filepath


def shp_to_json(in_shp, json_path):
    cur = arcpy.da.SearchCursor(in_shp, ["Floor", "height"])  # 提取RASTERVALU列数据
    t_list = []

    for row in cur:  # cursor是按照一行一行顺序读取数据
        # t = row[0]  # 上面cursor只寻找一列数据，因此是第0列
        if int(row[1]) > 0:
            t_list.append([row[0], row[1]])

    t_dict = {"result": t_list}
    with open(r'{}'.format(json_path), 'w') as f:
        json.dump(t_dict, f, indent=3)
        print(r'[+] Downloaded TLE data in {}'.format(json_path))


def analyse_difference(jsonfile, thd=3):
    with open(jsonfile, 'r') as json_f:
        json_data = json.load(json_f)['result']
        json_arr = np.array(json_data)
        # json_arr[:, 1] /= 3  # GABLE 变floor
        json_arr[:, 0] *= 3  # Amap 变Height

        RMSE = metric_RMSE(json_arr[:, 0], json_arr[:, 1])
        MAE = metric_MAE(json_arr[:, 0], json_arr[:, 1])
        total_num = len(json_arr[:, 1])
        thd_num = 0.0
        for [floor, height] in json_arr:
            # print floor, height
            if abs(floor - height) > thd:
                thd_num += 1
        # print total_num, thd_num
        rate_ = np.round(100*(thd_num/total_num), 2)
        print "超过阈值的占：{}%, RMSE={}, MAE={}".format(rate_, RMSE, MAE)
        return total_num, thd_num, [rate_, RMSE, MAE], list(json_arr[:, 0]), list(json_arr[:, 1])


def metric_RMSE(data, compare):
    diff = data.flatten() - compare.flatten()
    RMSE = np.sqrt(np.mean(diff * diff))
    return RMSE


def metric_MAE(data, compare):
    MAE = np.mean(np.abs(data - compare))
    return MAE


def area_cal(shp):
    fields = [field.name for field in arcpy.ListFields(shp)]
    if "AreaM2" in fields:
        return
        # arcpy.management.DeleteField(shp, ["AreaM2"])
    arcpy.AddField_management(shp, "AreaM2", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(shp, "AreaM2", "!shape.geodesicArea@SQUAREMETERS!", "PYTHON_9.3")


def get_total_area(shp):
    fields = [field.name for field in arcpy.ListFields(shp)]
    assert "AreaM2" in fields
    total_area = 0.0
    with arcpy.da.SearchCursor(shp, ["AreaM2"]) as cursor:
        for row in cursor:
            if row[0] >= 1:
                total_area += row[0]
    return total_area


def IoU_cal(data1, data2, inter_root, union_root, shpname):
    inter_path = os.path.join(inter_root, shpname)
    union_path = os.path.join(union_root, shpname)

    if not os.path.isfile(union_path):
        union_shp(data1, data2, union_path)
    time.sleep(5)
    if not os.path.isfile(inter_path):
        inter_shp(data1, data2, inter_path)
    time.sleep(5)

    area_cal(inter_path)
    area_cal(union_path)
    inter_area = get_total_area(inter_path)
    union_area = get_total_area(union_path)
    iou = inter_area / union_area
    return iou


def inter_shp(shp1, shp2, save_path):
    arcpy.Intersect_analysis(in_features=[shp1, shp2], out_feature_class=save_path)


def union_shp(shp1, shp2, save_path):
    arcpy.Union_analysis(in_features=[shp1, shp2], out_feature_class=save_path)


if __name__ == '__main__':
    # amap_root = r'G:\ProductData\61cities_AMAP_shpfile_49N'
    # data_root = r'G:\ProductData\East_Asian_buildings\61cities'
    # inter_root = make_dir(r'G:\ProductData\East_Asian_buildings\61cities_Inter')
    # union_root = make_dir(r'G:\ProductData\East_Asian_buildings\61cities_Union')
    # json_save = r'G:\ProductData\East_Asian_buildings\IoUs.json'
    # amap_paths, amap_names = file_name_shp(amap_root)
    # IoUs = {}
    # for ii in range(len(amap_paths)):
    #     amap_path = amap_paths[ii]
    #     amap_name = amap_names[ii]
    #     if amap_name in change_name_dict.keys():
    #         data_name = change_name_dict[amap_name]
    #     else:
    #         data_name = amap_name
    #     data_path = os.path.join(data_root, data_name+'.shp')
    #     IoU = IoU_cal(amap_path, data_path, inter_root, union_root, data_name+'.shp')
    #     IoUs[amap_name] = IoU
    #     print amap_name, IoU
    # with open('{}'.format(json_save), 'w') as f:
    #     json.dump(IoUs, f, indent=3)
    #     print('[+] Downloaded TLE data in {}'.format(json_save))

    # Amap_root = r'G:\ProductData\East_Asian_buildings\61cities'
    # save_root = make_dir(r'G:\ProductData\East_Asian_buildings\61cities_49N')
    # amap_paths, amap_names = file_name_shp(Amap_root)
    # for ii in range(len(amap_names)):
    #     amap_name = amap_names[ii]
    #     amap_path = amap_paths[ii]
    #     print "projecting {}".format(amap_name)
    #     save_path = os.path.join(save_root, amap_name + '.shp')
    #     # arcpy.Project_management(amap_path, save_path, BF_project)
    #     spatial_ref = arcpy.Describe(amap_path).spatialReference
    #     if 'WGS_1984_UTM_Zone_49N' not in spatial_ref.exportToString().split('[')[1].split(',')[0]:
    #         print spatial_ref.exportToString().split('[')[1].split(',')[0]
    #         print "{} is projected in WGS84 49N".format(amap_path)
    #         save_path = os.path.join(save_root, amap_name+'.shp')
    #         print u"Projecting  " + amap_name
    #         if os.path.isfile(save_path):
    #             continue
    #         arcpy.Project_management(amap_path, save_path, BF_project)
    #
    #     else:
    #         if os.path.isfile(os.path.join(save_root, amap_name+'.shp')):
    #             continue
    #         for suffix in ['.dbf', '.prj', '.shp', '.shp.xml', '.shx', '.sbn', '.sbx']:
    #             from_file = amap_path.replace('.shp', suffix)
    #             print from_file, save_root
    #             if os.path.isfile(from_file):
    #                 mycopyfile(from_file, save_root)




    BF_root = r'F:\Data\3DGLOBFP\China\CHINA'
    save_root = make_dir(r'F:\Data\3DGLOBFP\China\61cities')
    projected_root = make_dir(r'F:\Data\3DGLOBFP\China\wgs84')
    for province in BF_city_dict.keys():
        assert os.path.exists(r'{}\{}.shp'.format(BF_root, province.lower())), province
        for city in BF_city_dict[province]:
            clip_file = r'D:\Dataset\@62allcities\ClipROI\{}.shp'.format(city)
            if not os.path.isfile(clip_file):
                clip_file = r'D:\Dataset\@62allcities\ClipROI\{}.shp'.format(name_change_dict[city])
            assert os.path.isfile(clip_file)

            # tar_file = r'{}\{}\{}.shp'.format(BF_root, province, city)
            tar_file = r'{}\{}.shp'.format(BF_root, province.lower())
            # tar_file = r'{}\{}\{}.shp'.format(projected_root, province, city)
            # if province == "Hainan":
            #     tar_file = r'{}\{}\{}.shp'.format(BF_root, province, province)
            assert os.path.exists(tar_file), tar_file

            # spatial_ref = arcpy.Describe(tar_file).spatialReference
            # if 'GCS_WGS_1984' not in spatial_ref.exportToString().split('[')[1].split(',')[0]:
            # # if 'WGS_1984_UTM_Zone_49N' not in spatial_ref.exportToString().split('[')[1].split(',')[0]:
            #     print spatial_ref.exportToString().split('[')[1].split(',')[0]
            #     print "{} is projected in WGS84".format(tar_file)
            #     save_path = os.path.join(projected_root, province.lower()+'.shp')
            #     print u"Projecting  " + province
            #     if os.path.isfile(save_path):
            #         continue
                arcpy.Project_management(tar_file, save_path, BF_project)
            #
            # else:
            #     if os.path.isfile(os.path.join(projected_root, province.lower()+'.shp')):
            #         continue
            #     for suffix in ['.dbf', '.prj', '.shp', '.shp.xml', '.shx', '.sbn', '.sbx']:
            #         from_file = tar_file.replace('.shp', suffix)
            #         print from_file, projected_root
            #         if os.path.isfile(from_file):
            #             mymovefile(from_file, projected_root)
            #
            # tar_file_ = r'{}\{}.shp'.format(projected_root, province.lower())

            print u"CLIPPING  " + clip_file
            save_path = os.path.join(save_root, city + ".shp")
            if os.path.isfile(save_path):
                continue
            print clip_file, tar_file, save_path
            arcpy.Clip_analysis(tar_file, clip_file, save_path)

#     # G = GABLE(fileroot=r'G:\ProductData\GABLE', saveroot=r'G:\ProductData\GABLE_TIF_10m')
#     # G.to_wgs84_dir(r'G:\ProductData\61cities_AMAP_shpfile', make_dir(r'G:\ProductData\61cities_AMAP_shpfile_wgs84'))
#     #
#     metrics_dict = {}
#     floors = []
#     heights = []
#     thd = 3
#     all_total = 0.0
#     all_thd = 0.0
#     for province in city_dict.keys():
#         for city in city_dict[province]:
#             # fileroot = r'G:\ProductData\GABLE_61cities\{}'.format(city)
#             # print province, city
#             # if city != 'Shenzhen':
#             #     continue
#             # print "processing " + city
#             # G.clip_single(clip_file=r'D:\Dataset\@62allcities\ClipROI\{}.shp'.format(city),
#             #               target_name=province, save_root=make_dir(r'G:\ProductData\GABLE_61cities\{}'.format(city)))
#             # G.merge_dir(r'G:\ProductData\GABLE_61cities\{}'.format(city))
#             # G.to_raster_61city(r'G:\ProductData\GABLE_61cities\{}'.format(city))
#
#             # G.to_wgs84_dir(r'G:\ProductData\GABLE_61cities\{}'.format(city))
#             shp_to_json(r'G:\ProductData\61cities\GABLE_61cities_join_byAmap\{}.shp'.format(city),
#                        json_path=make_dir(r'G:\ProductData\61cities\GABLE_61cities_join_byAmap_json') + "\\{}.json".format(city))
#
#             total_num, thd_num, metrics, floor, height = analyse_difference(r'G:\ProductData\61cities\GABLE_61cities_join_byAmap_json\{}.json'.format(city), thd)
#             metrics_dict[city] = metrics
#             floors += floor
#             heights += height
#             all_total += total_num
#             all_thd += thd_num
#
#             # G.join_by_Amap(find_all_file(fileroot), r'G:\ProductData\61cities_AMAP_shpfile_wgs84\{}.shp'.format(city),
#             #                save_path=make_dir(r'G:\ProductData\GABLE_61cities_join_byAmap') + "\\{}.shp".format(city))
#     GABLE_metric_meta_data = {"pred": heights, "gt": floors}
#     write_json('GABLE_Metric_META.json', GABLE_metric_meta_data)
#     all_rate = np.round(100*(all_thd/all_total), 2)
#     RMSE_all = metric_RMSE(np.array(floors), np.array(heights))
#     MAE_all = metric_MAE(np.array(floors), np.array(heights))
#
#     all_dict = {"AMAP": floors, "GABLE/3": heights}
#
#     print "总超过阈值的占：{}%, RMSE={}, MAE={}".format(all_rate, RMSE_all, MAE_all)
#     metrics_dict['Overall'] = [all_rate, RMSE_all, MAE_all]
#     save_json = r'G:\ProductData\61cities\GABLE_61cities_join_byAmap_json\all_metrics_thd{}.json'.format(thd)
#     with open(save_json, 'w') as f:
#         json.dump(metrics_dict, f, indent=3)
#         print(r'[+] Downloaded TLE data in {}'.format(save_json))
#     save_json = r'G:\ProductData\61cities\GABLE_61cities_join_byAmap_json\all_data.json'
#     with open(save_json, 'w') as f:
#         json.dump(all_dict, f, indent=3)
#         print(r'[+] Downloaded TLE data in {}'.format(save_json))
#
#
# # D:\PythonProjects\Arcmap\Orbits\Main\Satellites_info.xls