#!/usr/bin/python
# -*- coding: UTF-8 -*-
from tools import *
from TifClipper import *
from osgeo import gdal
import math
from tqdm import tqdm

citynames = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
             'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
             'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
             'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
             'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
             'Shenyang', 'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan']
# citynames = ['Beijing', 'Nanjing']


def clip_dem_dsm(dem_path, dsm_path, gt_path, block_size=128, out_path= './nDSM', city='Beijing'):
    dataset_gt = gdal.Open(gt_path, gdal.GA_Update)
    dataset_gt.FlushCache()
    dataset_dem = gdal.Open(dem_path, gdal.GA_Update)
    dataset_dem.FlushCache()
    dataset_dsm = gdal.Open(dsm_path, gdal.GA_Update)
    dataset_dsm.FlushCache()
    gt_width = dataset_gt.RasterXSize
    gt_height = dataset_gt.RasterYSize
    xnum = math.floor(gt_width / block_size)
    ynum = math.floor(gt_height / block_size)
    x_gap_dem, y_gap_dem = cal_gaps(dataset_dem, dataset_gt)
    x_gap_dsm, y_gap_dsm = cal_gaps(dataset_dsm, dataset_gt)
    make_dir(out_path)
    gt_outpath = out_path+'/gts/'
    make_dir(gt_outpath)
    dsm_outpath = out_path+'/dsm/'
    make_dir(dsm_outpath)
    dem_outpath = out_path+'/dem/'
    make_dir(dem_outpath)

    with tqdm(total=int(xnum * ynum)) as pbar:
        for i in range(xnum):
            for j in range(ynum):
                x, y = i * block_size, j * block_size
                try:
                    if (
                            ClipGT_1dim(dataset_gt, outpath=gt_outpath + "{2}_{0}_{1}.tif".format(i, j, city), offset_x=x, offset_y=y,
                                block_xsize=block_size, block_ysize=block_size, if_height = False)):
                        clip_1dim(dataset_dem, outpath=dem_outpath + "{2}_{0}_{1}.tif".format(i, j, city), offset_x=x + x_gap_dem,
                                    offset_y=y+y_gap_dem,
                                    block_xsize=block_size, block_ysize=block_size)
                        clip_1dim(dataset_dsm, outpath=dsm_outpath + "{2}_{0}_{1}.tif".format(i, j, city),
                                    offset_x=x + x_gap_dsm,
                                    offset_y=y + y_gap_dsm,
                                    block_xsize=block_size, block_ysize=block_size)
                except(ValueError):
                    print("Value Error")
                except(IOError):
                    print("IOE Error")
                pbar.update()
    del dataset_gt
    del dataset_dsm
    del dataset_dem


def ClipGT_1dim(dataset_GT, outpath='GT.tif', offset_x=0,
                offset_y=0, block_xsize=128, block_ysize=128, if_height = False):

    in_band1 = dataset_GT.GetRasterBand(1)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    if np.all(out_band1 == 255):
        return False
    sum = 0
    for da in out_band1:
        for i in da:
            if i < 255:
                sum += 1
    if sum < 0.05 * block_xsize * block_ysize:
        return False
    # out_band1[np.where( out_band1 < 0 )] = 1
    #改变Nodata值
    out_band1[np.where( out_band1 == 255 )] = 0
    if if_height:
        out_band1 = out_band1 * 3

    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 1, in_band1.DataType)
    # print("create new tif file succeed")
    geomat = dataset_GT.GetGeoTransform()
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
    out_ds.SetProjection(dataset_GT.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(Nodata_lab)
    # 写入目标文件
    # out_band1 = out_band1 * 3
    out_ds.GetRasterBand(1).WriteArray(out_band1)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds
    return True


def Mix_demdsm(dem, dsm, block_xsize, block_ysize, outpath='test.tif'):
    in_band1 = dem.GetRasterBand(1)
    in_band2 = dsm.GetRasterBand(1)
    geomat = list(dem.GetGeoTransform())
    top_left_x = geomat[0]  # 左上角x坐标
    w_e_pixel_resolution = geomat[1]  # 东西方向像素分辨率
    top_left_y = geomat[3]  # 左上角y坐标
    n_s_pixel_resolution = geomat[5]  # 南北方向像素分辨率
    # 将计算后的值组装为一个元组，以方便设置
    dst_transform = (top_left_x, geomat[1], geomat[2], top_left_y, geomat[4], geomat[5])
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 1, in_band1.DataType)
    # print("create new tif file succeed")
    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(dst_transform)
    out_band1 = in_band1.ReadAsArray()
    out_band2 = in_band2.ReadAsArray()
    out_band = out_band2 - out_band1
    # 设置SRS属性（投影信息）
    out_ds.SetProjection(dsm.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(0)

    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    del out_ds


def get_ndsm(dem_path, dsm_path, block_size=128, out_path= './nDSM', save_name = ''):

    dataset_dem = gdal.Open(dem_path, gdal.GA_Update)
    dataset_dem.FlushCache()
    dataset_dsm = gdal.Open(dsm_path, gdal.GA_Update)
    dataset_dsm.FlushCache()

    ndsm_outpath = out_path+'/ndsm'
    make_dir(ndsm_outpath)
    ndsm_outpath = ndsm_outpath + '/' + save_name + '.tif'
    Mix_demdsm(dataset_dem,dataset_dsm,block_size,block_size,outpath=ndsm_outpath)
    del dataset_dsm
    del dataset_dem

def main():
    DEMPATH = r'D:\Dataset\DEM_UTM'
    DSMPATH = r'D:\Dataset\DSM_UTM'
    GTPATH = r'D:\Dataset\52Cities\Label'
    OUTPATH = r'./nDSM'
    make_dir(OUTPATH)
    for cityname in citynames:
        gt_path = GTPATH+'\\'+cityname+'.tif'
        dem_path = DEMPATH+'\\'+cityname+'.tif'
        dsm_path = DSMPATH+'\\'+cityname+'.tif'
        clip_dem_dsm(dem_path, dsm_path, gt_path, 128, OUTPATH, city=cityname)

    Filepaths, Filenames = file_name_tif(OUTPATH+'/gts')
    pbar = tqdm(Filenames,total=len(Filenames),colour="red")
    for ii in range(len(Filenames)):
        filename = Filenames[ii]
        pbar.set_description(f"processing filename", filename)
        dem_path = OUTPATH + '/dem' + '/' + filename + '.tif'
        dsm_path = OUTPATH + '/dsm' + '/' + filename + '.tif'
        get_ndsm(dem_path, dsm_path, 128, out_path=OUTPATH, save_name=filename)
        pbar.update()


if __name__ == '__main__':
    main()