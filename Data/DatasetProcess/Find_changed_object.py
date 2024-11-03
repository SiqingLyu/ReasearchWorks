"""
此代码用于找到变化的区域，新增为 1， 拆除为 2， 其他为 0

此代码用于找到变化的区域，并将新增或拆除的建筑分布制图出来
"""
import numpy as np

from tools import *
from empatches022 import *

em = EMPatches()

NODATA = 0


def find_in_patch(before_patch, after_patch):
    data_changed_patch = np.zeros_like(after_patch)
    after_tar = LabelTarget(label_data=after_patch).to_target_cpu(background=0, value_mode="max")
    before_tar = LabelTarget(label_data=before_patch).to_target_cpu(background=0, value_mode="max")
    after_masks = after_tar['masks']
    before_masks = before_tar['masks']

    # 新建房子统计
    for mask in after_masks:
        before_ = before_patch[mask]
        no_building_pixels = len(before_ == NODATA)
        no_building_rate = no_building_pixels / len(before_)
        if no_building_rate > 0.9:  # 此前几乎没有建筑物在此地，说明有新建
            data_changed_patch[mask] = 1

    # 拆除房子统计
    for mask in before_masks:
        after_ = after_patch[mask]
        no_building_pixels = len(after_ == NODATA)
        no_building_rate = no_building_pixels / len(after_)
        if no_building_rate > 0.9:  # 此后几乎没有建筑物在此，说明有拆除
            data_changed_patch[mask] = 2

    return data_changed_patch


def find_single(data_before, data_after):
    assert data_after.shape == data_before.shape
    after_patches, indices = em.extract_patches(data_after, patchsize=400, overlap=0.0)
    before_patches, _ = em.extract_patches(data_before, patchsize=400, overlap=0.0)
    data_changed_list = []
    for ii in range(len(after_patches)):
        after_patch = after_patches[ii]
        before_patch = before_patches[ii]
        data_changed_patch = find_in_patch(before_patch, after_patch)
        data_changed_list.append(data_changed_patch)
    data_changed = em.merge_patches(data_changed_list, indices, mode='overwrite')
    return data_changed


def find_in_dir(dir_path_before, dir_path_after, save_dir):
    paths_before, names = file_name_tif(dir_path_before)
    paths_after, _ = file_name_tif(dir_path_after)
    assert len(paths_after) == len(paths_before)
    for ii in range(len(paths_after)):
        name_ = names[ii]
        path_before = paths_before[ii]
        path_after = paths_after[ii]
        data_before = tif.imread(path_before)
        data_after = tif.imread(path_after)
        data_changed = find_single(data_before, data_after)
        save_file = os.path.join(save_dir, name_ + '.tif')
        tif.imwrite(save_file, data_changed)


# def statistic_changed_single(data):
#
#     return nochange_num, removed_num, new_num


# def statistic_dir(dir_path):
#     paths, names = file_name_tif(dir_path)
#     nochange, removed, new = 0, 0, 0
#     for ii in range(len(paths)):
#         path_ = paths[ii]
#         name_ = names[ii]
#         data_ = tif.imread(path_)
#         nochange_, removed_, new_ = statistic_changed_single(data_)
#         nochange += nochange_
#         removed += removed_
#         new += new_
#
#     remove_rate = np.round(100 * removed / nochange, 2)
#     new_rate = np.round(100* new / nochange, 2)
#     changed_rate = remove_rate + new_rate
#     print(f"本年变化总比例： {changed_rate}%， 拆除比例：{remove_rate}%， 新建比例：{new_rate}%")


if __name__ == '__main__':
    years = range(2017, 2022, 1)
    for year in years:
        path_before = rf'G:\ProductData\CBRA\CBRA_{year - 1}'
        path_after = rf'G:\ProductData\CBRA\CBRA_{year}'
        save_dir = rf'G:\ProductData\CBRA\Changes\CBRA_CHANGE_{year}'
        find_in_dir(path_before, path_after, save_dir)
