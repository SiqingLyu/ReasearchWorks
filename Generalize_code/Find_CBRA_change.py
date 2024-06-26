"""
此代码用于找到变化的区域，新增为 1， 拆除为 2， 无变化为 3，无数据为 0
数据需要使用50m分辨率的CBRA数据进行

"""
import numpy as np
from tools import *

NODATA = 0
BUILDING = 255


def find_single(data_before, data_after):
    assert data_after.shape == data_before.shape
    data_changed = np.zeros_like(data_before)
    data_changed = np.where((data_before == BUILDING) & (data_after == BUILDING), 3, data_changed)
    data_changed = np.where((data_before == BUILDING) & (data_after != BUILDING), 2, data_changed)
    data_changed = np.where((data_before != BUILDING) & (data_after == BUILDING), 1, data_changed)
    return data_changed


def find_in_dir(dir_path_before, dir_path_after, save_dir):
    paths_before, _ = file_name_tif(dir_path_before)
    paths_after, names = file_name_tif(dir_path_after)
    assert len(paths_after) == len(paths_before)
    for ii in range(len(paths_after)):
        name_ = names[ii]
        path_before = paths_before[ii]
        path_after = paths_after[ii]
        data_before = tif.imread(path_before)
        data_after = tif.imread(path_after)
        data_changed = find_single(data_before, data_after)
        save_file = os.path.join(save_dir, name_ + '.tif')
        tif.imsave(save_file, data_changed)


def statistic_changed_single(data):
    nochange_num = len(data[data == 3])
    removed_num = len(data[data == 2])
    new_num = len(data[data == 1])
    return nochange_num, removed_num, new_num


def statistic_changed_single_shp(data):
    assert
    nochange_num = len(data[data == 3])
    removed_num = len(data[data == 2])
    new_num = len(data[data == 1])
    return nochange_num, removed_num, new_num


def statistic_dir(dir_path):
    paths, names = file_name_tif(dir_path)
    nochange, removed, new = 0, 0, 0
    for ii in range(len(paths)):
        path_ = paths[ii]
        name_ = names[ii]
        data_ = tif.imread(path_)
        nochange_, removed_, new_ = statistic_changed_single(data_)
        nochange += nochange_
        removed += removed_
        new += new_

    remove_rate = np.round(100 * removed / nochange, 2)
    new_rate = np.round(100 * new / nochange, 2)
    changed_rate = remove_rate + new_rate
    print(f"本年变化总比例： {changed_rate}%， 拆除比例：{remove_rate}%， 新建比例：{new_rate}%")
    return [changed_rate, remove_rate, new_rate]

def statistic_dir_shp(dir_path):
    paths, names = file_name_tif(dir_path)
    nochange, removed, new = 0, 0, 0
    for ii in range(len(paths)):
        path_ = paths[ii]
        name_ = names[ii]
        data_ = tif.imread(path_)
        nochange_, removed_, new_ = statistic_changed_single(data_)
        nochange += nochange_
        removed += removed_
        new += new_

    remove_rate = np.round(100 * removed / nochange, 2)
    new_rate = np.round(100 * new / nochange, 2)
    changed_rate = remove_rate + new_rate
    print(f"本年变化总比例： {changed_rate}%， 拆除比例：{remove_rate}%， 新建比例：{new_rate}%")
    return [changed_rate, remove_rate, new_rate]


if __name__ == '__main__':
    # years = range(2017, 2022, 1)
    # change_dict = {"name": ["changed_rate", "remove_rate", "new_rate"]}
    # for year in years:
    #     res = statistic_dir(rf'G:\ProductData\CBRA\CBRA_CHANGE_{year}_50m')
    #     change_dict[year] = res
    # write_json(r'CBRA_Change.json', change_dict)
    year = 2021
    path_before = rf'G:\ProductData\CBRA\G:\ProductData\CBRA\CBRA_{year - 1}_10m_shp'
    path_after = rf'G:\ProductData\CBRA\CBRA_{year}_10m_shp'
    save_dir = make_dir(rf'G:\ProductData\CBRA\CBRA_{year}_10m_shp_CHANGE')
    print("processing", path_after)
    find_in_dir(path_before, path_after, save_dir)
