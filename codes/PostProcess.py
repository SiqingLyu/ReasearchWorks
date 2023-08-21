from osgeo import gdal
import numpy as np
import math
import time
from tqdm import tqdm
import os
from tools import *

Nodata_lab = 0
Nodata_img = -3.40282306074e+038

def mask_array(array, mask):
    block_xsize = array.shape[0]
    block_ysize = array.shape[1]
    for i in range(block_xsize):
        for j in range(block_ysize):
            if mask[i][j]:
                array[i][j] = array[i][j]
            else:
                array[i][j] = 0
    return array


def post_process_tif(dataset_GT, dataset, dataset_vvh, dataset_ori, outpath='GT.tif', offset_x=0,
                offset_y=0, block_xsize=128, block_ysize=128):
    in_band0 = dataset_GT.GetRasterBand(1)
    out_band0 = in_band0.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    gt_min, gt_max = get_range(out_band0)
    gt_max = gt_max

    mask = out_band0[:, :] > 0
    in_band1 = dataset.GetRasterBand(1)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    out_band1 = Normalize(out_band1) * (gt_max - gt_min)
    out_band1 = np.where(out_band1 > 3 , out_band1, 0)
    out_band1 = mask_array(out_band1, mask)
    out_band1 = Normalize(out_band1) * (gt_max - gt_min)

    out_band1 = np.fix(out_band1)

    in_band3 = dataset_vvh.GetRasterBand(1)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    out_band3 = Normalize(out_band3) * (gt_max - gt_min)
    out_band3 = np.where(out_band3 > 3, out_band1, 0)
    out_band3 = mask_array(out_band3, mask)
    out_band3 = Normalize(out_band3) * (gt_max - gt_min)

    out_band3 = np.fix(out_band3)
    # out_band1 = Normalize(out_band1) * gt_max

    # out_band1 = np.fix(out_band1)
    # out_band1 = Normalize(out_band1) * gt_max

    print(gt_max, gt_min)
    in_band2 = dataset_ori.GetRasterBand(1)

    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 1, in_band1.DataType)
    out_ds1 = gtif_driver.Create(outpath[:-4] + '_gt.tif', block_xsize, block_ysize, 1, in_band1.DataType)
    out_ds2 = gtif_driver.Create(outpath[:-4] + '_vvh.tif', block_xsize, block_ysize, 1, in_band3.DataType)
    # print("create new tif file succeed")
    geomat = dataset_ori.GetGeoTransform()
    # if geomat:
    #     print(geomat)
    #     print("Origin = ({}, {})".format(geomat[0], geomat[3]))
    #     print("Pixel Size = ({}, {})".format(geomat[1], geomat[5]))

    # 读取原图仿射变换参数值
    top_left_x = geomat[0]  # 左上角x坐标
    w_e_pixel_resolution = geomat[1]  # 东西方向像素分辨率
    top_left_y = geomat[3]  # 左上角y坐标
    n_s_pixel_resolution = geomat[5]  # 南北方向像素分辨率

    # 根据反射变换参数计算新图的原点坐标
    top_left_x = top_left_x + offset_x * w_e_pixel_resolution
    top_left_y = top_left_y + offset_y * n_s_pixel_resolution

    # 将计算后的值组装为一个元组，以方便设置
    dst_transform = (top_left_x, geomat[1], geomat[2], top_left_y, geomat[4], geomat[5])

    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(dst_transform)

    # 设置SRS属性（投影信息）
    out_ds.SetProjection(dataset_ori.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(0)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band1)
    # 设置裁剪出来图的原点坐标
    out_ds1.SetGeoTransform(dst_transform)

    # 设置SRS属性（投影信息）
    out_ds1.SetProjection(dataset_ori.GetProjection())
    out_ds1.GetRasterBand(1).SetNoDataValue(0)
    # 写入目标文件
    out_ds1.GetRasterBand(1).WriteArray(out_band0)

    out_ds2.SetGeoTransform(dst_transform)

    # 设置SRS属性（投影信息）
    out_ds2.SetProjection(dataset_ori.GetProjection())
    out_ds2.GetRasterBand(1).SetNoDataValue(0)
    # 写入目标文件
    out_ds2.GetRasterBand(1).WriteArray(out_band3)
    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds
    del out_ds1
    del out_ds2
    return True


def main():
    names = ['Beijing_14_6', 'Xianggang_9_5']
    path = r'D:\Desktop\result'
    for name in names:
        in_raster =path + '\pred' + name + '.tif'
        gt_raster = path+ '\\ref' + name + '.tif'
        vvh_raster = path+ '\\vvh' + name + '.tif'
        ori_raster = r'D:\PythonProjects\DataProcess\Data\SR'+'\\'+name+'.tif'
        out_raster = name+'.tif'
        in_data = Read_tif(in_raster)
        gt_data = Read_tif(gt_raster)
        vvh_data = Read_tif(vvh_raster)
        ori_data = Read_tif(ori_raster)
        post_process_tif(gt_data,in_data,vvh_data,ori_data, out_raster,0,0,512,512)
        del in_data
        del gt_data
        del ori_data
        del vvh_data


if __name__ == '__main__':
    main()