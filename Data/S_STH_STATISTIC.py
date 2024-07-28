# -*- coding: utf-8 -*-

"""
本代码用于统计不同城市功能区内的建筑物层高和层数分布，
最终得到的结果应该是一个字典：
{
“北方”：[ ["居民区", "13层", "3.8 m/层"], ..., []]，
“南方”：[ ["居民区", "13层", "3.8 m/层"], ..., []]，
“西北”：[ ["居民区", "13层", "3.8 m/层"], ..., []]，
“青藏”：[ ["居民区", "13层", "3.8 m/层"], ..., []]，
}

"""
import numpy as np

from tools import *
from empatches022 import *
import statistics

NODATA_DICT = {
    "EULUC": 0,
    "GEDI": 0,
    "NoS": 255,
    "GABLE": 0,
    "Height": 0
}

citynames = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
             'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
             'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
             'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
             'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
             'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan']  # ]  # 'Shenyang',
# 'Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
# 'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Changsha', 'Huizhou', 'Lanzhou', 'Luoyang'
# ]
citynames += ['Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
              'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Changsha', 'Huizhou', 'Lanzhou', 'Luoyang']  # "Yantai"

BEIFANG_citynames = ['Beijing', 'Tianjin', 'Haerbin', 'Xian', 'Zhengzhou', 'Baoding', 'Changchun', 'Dalian',
                     'Jinan', 'Luoyang', 'Shijiazhuang', 'Taiyuan', 'Taizhou', 'Tangshan', 'Qingdao', 'Shenyang']
# BEIFANG_citynames = ['Tianjin']
QINGZANG_citynames = ["Lasa", "Xining"]
XIBEI_citynames = ["Xining", "Huhehaote", "Eerduosi", "Lanzhou", "Yinchuan"]
NANFANG_citynames = []
for city in citynames:
    if city in BEIFANG_citynames:
        continue
    if city in QINGZANG_citynames:
        continue
    if city in XIBEI_citynames:
        continue
    NANFANG_citynames.append(city)


def get_info_from_a_pair(EULUC, NoS, GEDI, GABLE):
    """
    输入的三种数据的形状大小应当保持一致
    """
    LT = LabelTarget(label_data=NoS)
    if LT.to_target_cpu(background=255) is None:
        return None
    target = LT.to_target_cpu(background=255)
    masks, nos = target["masks"], target["nos"]
    info_list = []
    Height = np.zeros_like(GEDI)
    # Height[(GABLE != NODATA_DICT["GABLE"]) & (GABLE < 24)] = GABLE
    Height = np.where((GABLE != NODATA_DICT["GABLE"]) & (GABLE < 24), GABLE, Height)
    Height = np.where((GEDI != NODATA_DICT["GEDI"]) & (GEDI >= 24), GEDI, Height)
    # Height[(GEDI != NODATA_DICT["GEDI"]) & (GEDI >= 24)] = GEDI

    for ii in range(len(nos)):
        nos_ = nos[ii]
        mask = masks[ii]

        EULUC_ = EULUC[(mask == 1) & (EULUC != NODATA_DICT['EULUC'])]
        Height_ = Height[(mask == 1) & (Height != NODATA_DICT['Height'])]

        if (len(EULUC_) == 0) or (len(Height_) == 0):
            continue
        EULUC_ = int(statistics.mode(EULUC_))

        Height_ = np.max(Height_)

        info_ = [EULUC_, nos_, Height_]
        info_list.append(info_)
    return info_list


def pre_process(data):
    data[data < 0] = 0
    data[data > 10000] = 0
    return data


def get_info_by_region(region_dict: dict = None, data_root: str = '', patch_size: int = 100):
    """
    :param patch_size: 分块处理的窗口大小
    :param region_dict: {“北方”：[文件名, ... , 文件名], ...}
    :param data_root: 此文件路径下存放三个文件夹： EULUC，NoS， Height，分别以相同的名称保存各大城市的数据。
    :return: 得到最终结果
    """
    final_dict = {}
    for region in region_dict.keys():
        data_files = region_dict[region]
        region_list = []
        for data_file in data_files:
            print(f"processing  {region}:  {data_file}")
            data_dict = {"EULUC": None, "NoS": None, "GEDI": None, "GABLE": None}
            for data_name in data_dict.keys():
                data_path = os.path.join(data_root, data_name)

                data_file_path = os.path.join(data_path, data_file + '.tif')  # 查看需不需要加后缀
                data_dict[data_name] = pre_process(read_tif(data_file_path))

            EM = EMPatches()
            _, indices = EM.extract_patches(data_dict["NoS"], patchsize=patch_size, overlap=0.0)
            for index_ in indices:
                x_from: int = index_[0]
                x_to: int = index_[1]
                y_from: int = index_[2]
                y_to: int = index_[3]
                info_list = get_info_from_a_pair(data_dict["EULUC"][x_from:x_to, y_from: y_to],
                                                 data_dict["NoS"][x_from:x_to, y_from: y_to],
                                                 data_dict["GEDI"][x_from:x_to, y_from: y_to],
                                                 data_dict["GABLE"][x_from:x_to, y_from: y_to])
                if info_list is not None:
                    region_list += info_list
        final_dict[region] = region_list
    write_json(f"S_STH_STATISTIC.json", final_dict)
    # print(final_dict)
    return final_dict


def get_distribution(data_arr, from_, to_):
    total = len(data_arr)
    if total == 0:
        return None
    prop_dict = {}
    for ii in range(from_, to_ + 1):
        num_tmp = len(data_arr[data_arr == ii])
        prop_tmp = num_tmp / total
        prop_dict[ii] = prop_tmp
    return prop_dict


def get_mean_value_of_region(data_list, name_ = ''):
    value_dict = {}
    nos_list = []
    for (city_type, nos, height) in data_list:
        sth = height / nos
        if (sth < 2) or (sth > 6):
            continue
        nos_list.append(nos)
        if city_type not in value_dict.keys():
            value_dict[city_type] = [[nos, sth]]
        else:
            value_dict[city_type].append([nos, sth])

    nos_arr_all = np.array(nos_list)
    nos_dis_all = get_distribution(nos_arr_all, from_=1, to_=30)
    sth_mean_dict = {}
    nos_dis_dict = {}

    for city_type in value_dict.keys():
        type_data_list = value_dict[city_type]
        nos_arr = np.array(type_data_list)[:, 0]
        sth_arr = np.array(type_data_list)[:, 1]
        nos_dis = get_distribution(nos_arr, from_=1, to_=30)
        sth_mean = np.mean(sth_arr)
        sth_mean_dict[city_type] = sth_mean
        nos_dis_dict[city_type] = nos_dis
    print(sth_mean_dict)
    print(nos_dis_dict)
    print(nos_dis_all)
    write_json(f'{name_}_sth_mean_dict.json', sth_mean_dict)
    write_json(f'{name_}_nos_dis_dict.json', nos_dis_dict)
    write_json(f'{name_}_nos_all_dis.json', nos_dis_all)
    return sth_mean_dict, nos_dis_dict, nos_dis_all


if __name__ == '__main__':
    # region_dict = {
    #     "BF": BEIFANG_citynames,
    #     "NF": NANFANG_citynames,
    #     "XB": XIBEI_citynames,
    #     "QZ": QINGZANG_citynames
    # }
    # get_info_by_region(region_dict=region_dict, data_root=r'F:\Codes\CBRA_Check\data\S_STH',
    #                    patch_size = 100)

    data_dict = read_json('S_STH_STATISTIC.json')
    # print(data_dict)
    sth_mean_total_dict,  nos_dis_total_dict, nos_dis_total_all = {}, {}, {}
    for name_ in ["BF", "NF", "XB", "QZ"]:
        if len(data_dict[name_]) == 0:
            continue
        sth_mean_dict, nos_dis_dict, nos_dis_all = get_mean_value_of_region(data_dict[name_], name_=name_)
        sth_mean_total_dict[name_] = sth_mean_dict
        nos_dis_total_dict[name_] = nos_dis_dict
        nos_dis_total_all[name_] = nos_dis_all

    write_json("TOTAL_sth_mean_dict.json", sth_mean_total_dict)
    write_json("TOTAL_nos_dis_dict.json", nos_dis_total_dict)
    write_json("TOTAL_nos_dis_all.json", nos_dis_total_all)
    # print(vd)
