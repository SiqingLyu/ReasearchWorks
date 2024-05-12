# -*- coding: utf-8 -*-
import numpy as np
import os
import shutil


def get_range(x):
    ma = np.max(x)
    mi = np.min(x)
    return mi, ma


def cal_rmse(y_true, ypred):
    diff=y_true.flatten()-ypred.flatten()
    return np.sqrt(np.mean(diff*diff))


def move_all_file(old_path, new_path):
    print(old_path)
    print(new_path)
    filelist = os.listdir(old_path)  # 列出该目录下的所有文件,listdir返回的文件列表是不包含路径的。
    print(filelist)
    for file in filelist:
        src = os.path.join(old_path, file)
        dst = os.path.join(new_path, file)
        print('src:', src)  # 原文件路径下的文件
        print('dst:', dst)  # 移动到新的路径下的文件
        shutil.move(src, dst)


def mycopyfile(srcfile, dstpath):  # 复制函数
    if not os.path.isfile(srcfile):
        print ("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建路径
        shutil.copy(srcfile, dstpath + fname)  # 复制文件
        # print ("copy %s -> %s" % (srcfile, dstpath + fname))


def mymovefile(srcfile, dstpath):  # 移动函数
    if not os.path.isfile(srcfile):
        print ("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建路径
        shutil.move(srcfile, dstpath + fname)  # 移动文件
        # print ("move %s -> %s" % (srcfile, dstpath + fname))


def trans_list_to_str(l, split=' '):
    s = '"'
    for item in l:
        s += str(item) + split
    # s = s[-1]
    s += '"'
    return s


def trans_str_to_list(s=None, split=' ', typename='int'):
    s = s.split(split)
    s_ = []
    for i in s:
        if len(i) == 0:
            continue
        if typename == 'float':
            s_.append(float(i))
        elif typename == 'int':
            s_.append(int(i))
        elif typename == 'str':
            s_.append(i)
    return s_


def make_dir(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)
    return path


def Normalize(array):
    '''
    Normalize the array
    '''
    mx = np.nanmax(array)
    mn = np.nanmin(array)
    t = (array-mn)/((mx-mn))
    return t


def file_name_tif(file_dir):
    '''
    eg: Listfile, allFilename = file_name(r'/www/lsq/optical')
    only record tif files
    :param file_dir: str
    :return: two List: a list of file absolute path & a list of file with no suffix
    '''
    if (os.path.isdir(file_dir)):
        L = []
        allFilename = []
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if file.split('.')[-1] != 'tif':
                    continue
                formatName = os.path.splitext(file)[1]
                fileName = os.path.splitext(file)[0]
                allFilename.append(fileName)
                if (formatName == '.tif'):
                    tempPath = os.path.join(root, file)
                    L.append(tempPath)
        return L, allFilename
    else:
        print('must be folder path')

def file_name_shp(file_dir):
    '''
    eg: Listfile, allFilename = file_name(r'/www/lsq/optical')
    only for shp files
    :param file_dir: str
    :return: two List: a list of file absolute path & a list of file with no suffix
    '''
    if (os.path.isdir(file_dir)):
        L = []
        allFilename = []
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if file.split('.')[-1] != 'shp':
                    continue
                formatName = os.path.splitext(file)[1]
                fileName = os.path.splitext(file)[0]
                allFilename.append(fileName)
                if (formatName == '.shp'):
                    tempPath = os.path.join(root, file)
                    L.append(tempPath)
        return L, allFilename
    else:
        print('must be folder path')

def haversine_dis(lon1, lat1, lon2, lat2):
    # 将十进制转为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    aa = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(aa))
    r = 6371  # 地球半径，千米
    # 返回单位：km
    return c * r