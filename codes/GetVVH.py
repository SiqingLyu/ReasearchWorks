from osgeo import gdal
import numpy as np
import math
import time
from tqdm import tqdm
import os
import tifffile as tif
from tools import make_dir
Nodata_lab = 0
Nodata_img = 0
Nodata_VVH = -1.797693e+308
folder = 'TEST_VVH'
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
# citynames = ['Dongguan']
VV_MAX = 40.9
VV_MIN = -40.9
VH_MAX = 35.6
VH_MIN = -55.4
def Normalize_VV(array, outpath):
    '''
    Normalize the array
    '''
    array[(array != array) | (array < -10000)] = VV_MIN

    mx = np.nanmax(array)
    mn = np.nanmin(array)
    print(mn,mx)
    if mx == mn:
        print(outpath, 'value is :', mx)
        t = np.zeros_like(array)
        t[t == 0] = mx
    if mx > 100 or mn < -100:
        print(outpath, 'value is :', mx)
        # print('------', mn)
    # array = np.where(np.isnan(array), mn, array)
    t = (array-VV_MIN)/(VV_MAX - VV_MIN)
    return t

def Normalize_VH(array, outpath):
    '''
    Normalize the array
    '''
    array[(array!=array) | (array < -10000)] = VH_MIN

    mx = np.nanmax(array)
    mn = np.nanmin(array)
    # print(mn,mx)
    if mx == mn:
        print(outpath, 'value is :', mx)
        t = np.zeros_like(array)
        t[t == 0] = mx
    if mx > 100 or mn < -100:
        print(outpath, 'value is :', mx)
        # print('------', mn)
    # array = np.where(np.isnan(array), mn, array)
    t = (array-VH_MIN)/(VH_MAX-VH_MIN)
    return t

def ClipVVVH_2dim(dataset_VVVH, outpath='VVVH.tif'):
    in_band_VV = dataset_VVVH.GetRasterBand(1)
    in_band_VH = dataset_VVVH.GetRasterBand(2)
    out_band_VV = in_band_VV.ReadAsArray()
    out_band_VH = in_band_VH.ReadAsArray()

    # print(np.max(out_band_VV), np.min(out_band_VV))
    # print(np.max(out_band_VH), np.min(out_band_VH))

    out_band_VV= Normalize_VV(out_band_VV, outpath)
    out_band_VH = Normalize_VH(out_band_VH, outpath)
    # VVH = VV * γ^VH (γ = 5)
    out_band = out_band_VV * pow(5,out_band_VH)
    assert not np.any(np.isnan(out_band))
    # print(np.max(out_band), np.min(out_band))
    mn = np.min(out_band)
    # print(np.min(out_band))
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    # print(out_band.shape)
    out_ds = gtif_driver.Create(outpath, out_band.shape[1], out_band.shape[0], 1, in_band_VV.DataType)
    # print("create new tif file succeed")
    geomat = dataset_VVVH.GetGeoTransform()
    # 读取原图仿射变换参数值
    top_left_x = geomat[0]  # 左上角x坐标
    w_e_pixel_resolution = geomat[1]  # 东西方向像素分辨率
    top_left_y = geomat[3]  # 左上角y坐标
    n_s_pixel_resolution = geomat[5]  # 南北方向像素分辨率

    # 根据反射变换参数计算新图的原点坐标
    top_left_x = top_left_x
    top_left_y = top_left_y

    # 将计算后的值组装为一个元组，以方便设置
    dst_transform = (top_left_x, geomat[1], geomat[2], top_left_y, geomat[4], geomat[5])

    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(dst_transform)

    # 设置SRS属性（投影信息）
    out_ds.SetProjection(dataset_VVVH.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(0.0)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def ClipVVVH_2dim_VVVH(dataset_VVVH, outpath_VV='VV.tif', outpath_VH='VH.tif'):
    in_band_VV = dataset_VVVH.GetRasterBand(1)
    in_band_VH = dataset_VVVH.GetRasterBand(2)
    out_band_VV = in_band_VV.ReadAsArray()
    out_band_VH = in_band_VH.ReadAsArray()

    out_band_VV= Normalize_VV(out_band_VV, outpath_VV)
    out_band_VH = Normalize_VH(out_band_VH, outpath_VH)
    # VVH = VV * γ^VH (γ = 5)
    assert not np.any(np.isnan(out_band_VV))
    assert not np.any(np.isnan(out_band_VH))

    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    # print(out_band.shape)
    out_ds = gtif_driver.Create(outpath_VV, out_band_VV.shape[1], out_band_VV.shape[0], 1, in_band_VV.DataType)
    # print("create new tif file succeed")
    geomat = dataset_VVVH.GetGeoTransform()
    # 读取原图仿射变换参数值
    top_left_x = geomat[0]  # 左上角x坐标
    w_e_pixel_resolution = geomat[1]  # 东西方向像素分辨率
    top_left_y = geomat[3]  # 左上角y坐标
    n_s_pixel_resolution = geomat[5]  # 南北方向像素分辨率

    # 根据反射变换参数计算新图的原点坐标
    top_left_x = top_left_x
    top_left_y = top_left_y

    # 将计算后的值组装为一个元组，以方便设置
    dst_transform = (top_left_x, geomat[1], geomat[2], top_left_y, geomat[4], geomat[5])

    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(dst_transform)

    # 设置SRS属性（投影信息）
    out_ds.SetProjection(dataset_VVVH.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(np.min(out_band_VV))
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band_VV)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds
    out_ds = gtif_driver.Create(outpath_VH, out_band_VH.shape[1], out_band_VH.shape[0], 1, in_band_VV.DataType)
    # print("create new tif file succeed")
    geomat = dataset_VVVH.GetGeoTransform()
    # 读取原图仿射变换参数值
    top_left_x = geomat[0]  # 左上角x坐标
    w_e_pixel_resolution = geomat[1]  # 东西方向像素分辨率
    top_left_y = geomat[3]  # 左上角y坐标
    n_s_pixel_resolution = geomat[5]  # 南北方向像素分辨率

    # 根据反射变换参数计算新图的原点坐标
    top_left_x = top_left_x
    top_left_y = top_left_y

    # 将计算后的值组装为一个元组，以方便设置
    dst_transform = (top_left_x, geomat[1], geomat[2], top_left_y, geomat[4], geomat[5])

    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(dst_transform)

    # 设置SRS属性（投影信息）
    out_ds.SetProjection(dataset_VVVH.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(np.min(out_band_VH))
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band_VH)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def get_VVHs():
    save_path = r"D:\Dataset\@62allcities\VVHs"
    make_dir(save_path)
    # save_path = r"D:\Dataset\@62allcities\VVHs\VV"
    # make_dir(save_path)
    # save_path = r"D:\Dataset\@62allcities\VVHs\VH"
    # make_dir(save_path)

    for i in range(len(citynames)):
        print("processing ", citynames[i])
        VVVH = r"D:\Dataset\@62allcities\SARs_UTM" + '\\' + citynames[i] + '.tif'
        dataset_VVVH = gdal.Open(VVVH, gdal.GA_Update)
        dataset_VVVH.FlushCache()
        # ClipVVVH_2dim(dataset_VVVH, outpath=os.path.join(save_path, 'VV', citynames[i] + '.tif'))
        ClipVVVH_2dim_VVVH(dataset_VVVH, outpath_VV=os.path.join(save_path, 'VV', citynames[i] + '.tif'),
                           outpath_VH=os.path.join(save_path, 'VH', citynames[i] + '.tif'))
        del dataset_VVVH
    # print(f'mn VV: {np.min(mn_VVs)}, mx VV: {np.max(mx_VVs)}, mn_VH: {np.min(mn_VHs)}, mx_VH: {np.max(mx_VHs)})')
if __name__ == '__main__':
    get_VVHs()