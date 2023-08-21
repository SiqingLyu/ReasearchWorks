#!/usr/bin/python
# -*- coding: UTF-8 -*-

import tifffile as tif
from skimage.measure import label, regionprops
import os
import numpy as np
from os.path import join
from tools import *
city_dict={
    'Aomen': 1, 'Baoding': 2, 'Beijing': 3, 'Changchun': 4, 'Changsha': 5,
    'Changzhou': 6, 'Chengdu': 7, 'Chongqing': 8, 'Dalian': 9, 'Dongguan': 10,
    'Eerduosi': 11, 'Foshan': 12, 'Fuzhou': 13, 'Guangzhou': 14, 'Guiyang': 15,
    'Haerbin': 16, 'Haikou': 17, 'Hangzhou':18, 'Hefei': 19, 'Huhehaote': 20,
    'Huizhou': 21, 'Jinan': 22, 'Kunming':23, 'Lanzhou': 24, 'Lasa': 25,
    'Luoyang': 26, 'Nanchang': 27, 'Nanjing': 28, 'Nanning': 29, 'Ningbo': 30,
    'Quanzhou': 31, 'Sanya': 32, 'Shanghai': 33, 'Shantou': 34, 'Shenyang': 35,
    'Shenzhen': 36, 'Shijiazhuang': 37, 'Suzhou': 38, 'Taiyuan': 39, 'Taizhou': 40,
    'Tangshan': 41, 'Tianjin': 42, 'Wenzhou': 43, 'Wuhan':44, 'Xiamen': 45,
    'Xianggang': 46, 'Xian': 47, 'Xining': 48, 'Yangzhou': 49, 'Yinchuan':50,
    'Zhengzhou': 51, 'Zhongshan': 52
}


def process_nan(imgdata):
    imgdata = np.nan_to_num(imgdata)
    imgdata[imgdata < (-3.4028235e+37)] = 0
    return imgdata


def normalize_maxmin(array):
    '''
    Normalize the array
    '''
    mx = np.max(array)
    mn = np.min(array)
    assert ((mx-mn) != 0)
    t = (array-mn)/(mx-mn)
    return t


def normalize_meanstd(array):
    '''
    Normalize the array
    '''
    array_mean = np.mean(array)
    array_std = np.std(array, ddof=1)
    assert (array_std != 0)
    t = (array-array_mean)/array_std
    return t


def make_dataset(filepath,split=[0.7, 0.1, 0.2]):
    '''
    :param filepath: the root dir of img, lab and ssn
    :return: img, lab
    '''
    if not os.path.exists(filepath):
        raise ValueError('The path of the dataset does not exist.')
    else:
        img = [join(filepath, 'image', 'optical',  name) for name in os.listdir(join(filepath, 'image', 'optical'))]
        ssn = [join(filepath, 'image', 'season', 'all', name) for name in os.listdir(join(filepath, 'image', 'season', 'all'))]
        lab = [join(filepath, 'label', name) for name in os.listdir(join(filepath, 'label'))]
        vvh = [join(filepath, 'image', 'VVVH', name) for name in os.listdir(join(filepath, 'image', 'VVVH'))]

    assert len(img) == len(ssn)
    assert len(img) == len(lab)
    assert len(img) == len(vvh)


    img.sort()
    ssn.sort()
    lab.sort()
    vvh.sort()

    num_samples=len(img)
    img=np.array(img)
    ssn=np.array(ssn)
    lab=np.array(lab)
    vvh=np.array(vvh)

    # generate sequence
    # load the path
    seqpath = join(filepath, 'seq.txt')
    if os.path.exists(seqpath):
        seq = np.loadtxt(seqpath, delimiter=',')
    else:
        seq = np.random.permutation(num_samples)
        np.savetxt(seqpath, seq, fmt='%d', delimiter=',')
    seq = np.array(seq, dtype='int32')

    num_train = int(num_samples * split[0]) # the same as floor
    num_val = int(num_samples * split[1])

    train = seq[0:num_train]
    val = seq[num_train:(num_train+num_val)]
    test = seq[num_train+num_val:]

    imgt=np.vstack((img[train], ssn[train], vvh[train])).T
    labt=lab[train]

    imgv=np.vstack((img[val], ssn[val], vvh[val])).T
    labv=lab[val]

    imgte=np.vstack((img[test], ssn[test], vvh[test])).T
    labte=lab[test]

    return imgt, labt, imgv, labv, imgte, labte


def get_mask_label(labelpath, area_thd=4, label_is_nos=True):
    file_name = (labelpath.split('\\')[-1]).split('.')[0]
    city_name = file_name.split('_')[0]
    # print('------------------', file_name, '-------------------')
    image_id = [int(city_dict[city_name]), int(file_name.split('_')[1]), int(file_name.split('_')[2])]
    lab = tif.imread(labelpath)  # building floor * 3 (meters) in float format
    lab = np.nan_to_num(lab)
    label_region = label(lab > 0, connectivity=2)
    boxes, masks, labels, areas, nos_list = [], [], [], [], []
    for region in regionprops(label_region):
        if region.area < area_thd: continue
        # region.bbox垂直方向为x， 而目标检测中水平方向为x
        y_min, x_min, y_max, x_max = region.bbox
        # print(x_max)
        boxes.append([x_min, y_min, x_max, y_max])
        m = label_region == region.label
        # 取众数
        v_nos = np.bincount(lab[m]).argmax()
        nos_list.append(v_nos)
        masks.append(m)
        labels.append(v_nos if label_is_nos else 1)
        areas.append(region.area)
    assert len(boxes) > 0
    target = {
        'boxes': boxes,
        'labels': labels,
        'masks': masks,
        'area': areas,
        'image_id': image_id,
        'nos': nos_list,
        'file_name': file_name
    }
    return target


def save_maskes(label_folder_path , mask_savepath = '.\labelmaskes'):
    filepath_list, filename_list = file_name_tif(label_folder_path)
    make_dir(mask_savepath)

    for ii in range(len(filepath_list)):
        label_path = filepath_list[ii]
        label_name = filename_list[ii]
        target = get_mask_label(label_path)
        save_folder_path = mask_savepath + '\\' + label_name
        make_dir(save_folder_path)
        mask_list = target['masks']
        mask_no = 0
        print("processing : ", label_name)
        for mask_item in mask_list:
            save_path = save_folder_path + '\\' + str(mask_no) + '.tif'
            # mask_data = np.array(mask_item, dtype='uint8')
            tif.imsave(save_path, mask_item)
            mask_no += 1


if __name__ == '__main__':
    save_maskes('D:\PythonProjects\DataProcess\Data\label_bkas0', 'D:\PythonProjects\DataProcess\Data\Maskes')
