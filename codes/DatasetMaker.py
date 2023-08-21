'''
本代码用于从原始城市label图像、image图像、VVH图像、多季节图像分割数据集

Tips：
1. 如果需要对img进行超分，不需要将DN值归一化再×255，输出原始值即可
2. label的Nodata值经过一次训练之后，认为设置为0更方便训练（也可以在网络设置NoData值）
3. 相对路径os库可以读取/开头的路径，但是gdal库不能读取，要加.   比如'./Data/label'而不是'/Data/label'


'''

from osgeo import gdal
import numpy as np
import math
import time
from tqdm import tqdm
import os

def make_dir(path):
    if os.path.exists(path):
        pass
    else:
        os.mkdir(path)

'''--------------------------Configs-------------------------'''
Nodata_lab = 0
Nodata_img = -3.40282306074e+038

paths = [r'\Data', r'\Data\image', r'\Data\image\season',
             r'.\Data\image\optical',  # 3
             r'.\Data\image\season\fall',  # 4
             r'.\Data\image\season\summer',  # 5
             r'.\Data\image\season\winter',  # 6
             r".\Data\image\VVVH",  # 7
             r'.\Data\label_all_bkas0_height',  # 8
             r'.\Data\image\season\all'  # 9
             ]
cwd = os.getcwd()
for path in paths:
    path_ = cwd + path
    make_dir(path_)
# 操作将遵循以下顺序以及包含城市
citynames = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
             'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
             'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
             'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
             'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
             'Shenyang', 'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan']
'''--------------------------Configs-------------------------'''


def Normalize(array):
    '''
    Normalize the array
    '''
    mx = np.nanmax(array)
    mn = np.nanmin(array)
    t = (array-mn)/((mx-mn))
    return t


# 获取文件夹所有图片的路径和文件名
def file_name(file_dir):
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


def ClipVVVH_2dim(dataset_VVVH, outpath='VVVH.tif', offset_x=0,
                offset_y=0, block_xsize=128, block_ysize=128):
    in_band_VV = dataset_VVVH.GetRasterBand(1)
    in_band_VH = dataset_VVVH.GetRasterBand(2)
    out_band_VV = in_band_VV.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band_VH = in_band_VH.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band_VV = Normalize(out_band_VV)
    out_band_VH = 0.5 * Normalize(out_band_VH)
    # VVH = VV * γ^VH (γ = 5)
    out_band = out_band_VV * pow(5,out_band_VH)
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 1, in_band_VV.DataType)
    # print("create new tif file succeed")
    geomat = dataset_VVVH.GetGeoTransform()
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
    out_ds.SetProjection(dataset_VVVH.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(-1.797693e+308)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


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
    # out_band1[np.where( out_band1 < 255 )] = 1
    #改变Nodata值
    out_band1[np.where( out_band1 == 255 )] = Nodata_lab
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


def Cliptif_4dim(dataset, outpath='Clip.tif', offset_x=0, offset_y=0,
                 block_xsize=128, block_ysize=128):
    in_band1 = dataset.GetRasterBand(1)
    in_band2 = dataset.GetRasterBand(2)
    in_band3 = dataset.GetRasterBand(3)
    in_band4 = dataset.GetRasterBand(4)

    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band4 = in_band4.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    # out_band1 = Normalize(out_band1)
    # out_band2 = Normalize(out_band2)
    # out_band3 = Normalize(out_band3)
    # out_band4 = Normalize(out_band4)

    # out_band1 = np.array((np.round(out_band1 * 255)), dtype='uint8')
    # out_band2 = np.array((np.round(out_band2 * 255)), dtype='uint8')
    # out_band3 = np.array((np.round(out_band3 * 255)), dtype='uint8')
    # out_band4 = np.array((np.round(out_band4 * 255)), dtype='uint8')

    # print(out_band1)
    # breakpoint()
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 4, in_band1.DataType)
    # print("create new tif file succeed")
    geomat = dataset.GetGeoTransform()
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
    out_ds.SetProjection(dataset.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(-3.40282306074e+038)
    out_ds.GetRasterBand(2).SetNoDataValue(-3.40282306074e+038)
    out_ds.GetRasterBand(3).SetNoDataValue(-3.40282306074e+038)
    out_ds.GetRasterBand(4).SetNoDataValue(-3.40282306074e+038)
    # 写入目标文件  1234 = B G R N
    out_ds.GetRasterBand(1).WriteArray(out_band1)
    out_ds.GetRasterBand(2).WriteArray(out_band2)
    out_ds.GetRasterBand(3).WriteArray(out_band3)
    out_ds.GetRasterBand(4).WriteArray(out_band4)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def Upsampletif_4dim(dataset, outpath='Upsample.tif', offset_x=0, offset_y=0,
                 block_xsize=128, block_ysize=128, level=4):
    in_band1 = dataset.GetRasterBand(1)
    in_band2 = dataset.GetRasterBand(2)
    in_band3 = dataset.GetRasterBand(3)
    in_band4 = dataset.GetRasterBand(4)

    # out_band1 = Normalize(out_band1)
    # out_band2 = Normalize(out_band2)
    # out_band3 = Normalize(out_band3)
    # out_band4 = Normalize(out_band4)

    # out_band1 = np.array((np.round(out_band1 * 255)), dtype='uint8')
    # out_band2 = np.array((np.round(out_band2 * 255)), dtype='uint8')
    # out_band3 = np.array((np.round(out_band3 * 255)), dtype='uint8')
    # out_band4 = np.array((np.round(out_band4 * 255)), dtype='uint8')

    # print(out_band1)
    # breakpoint()

    geomat = list(dataset.GetGeoTransform())
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

    geomat[1] /= level
    geomat[5] /= level

    # 将计算后的值组装为一个元组，以方便设置
    dst_transform = (top_left_x, geomat[1], geomat[2], top_left_y, geomat[4], geomat[5])

    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize*level, block_ysize*level, 1, in_band1.DataType)
    # print("create new tif file succeed")
    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(dst_transform)
    # 读入波段信息
    out_band1 = in_band1.ReadAsArray(buf_xsize=block_xsize * level, buf_ysize=block_ysize * level)
    out_band2 = in_band2.ReadAsArray(buf_xsize=block_xsize * level, buf_ysize=block_ysize * level)
    out_band3 = in_band3.ReadAsArray(buf_xsize=block_xsize * level, buf_ysize=block_ysize * level)
    out_band4 = in_band4.ReadAsArray(buf_xsize=block_xsize * level, buf_ysize=block_ysize * level)
    # 设置SRS属性（投影信息）
    out_ds.SetProjection(dataset.GetProjection())
    # 设置Nodata值
    out_ds.GetRasterBand(1).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(2).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(3).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(4).SetNoDataValue(Nodata_img)
    # 写入目标文件  1234 = B G R N
    out_ds.GetRasterBand(1).WriteArray(out_band1)
    out_ds.GetRasterBand(2).WriteArray(out_band2)
    out_ds.GetRasterBand(3).WriteArray(out_band3)
    out_ds.GetRasterBand(4).WriteArray(out_band4)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def Upsampletif_1dim(dataset, outpath='Upsample.tif', offset_x=0, offset_y=0,
                 block_xsize=128, block_ysize=128, level=4):
    in_band1 = dataset.GetRasterBand(1)
    # in_band2 = dataset.GetRasterBand(2)
    # in_band3 = dataset.GetRasterBand(3)
    # in_band4 = dataset.GetRasterBand(4)



    # out_band1 = Normalize(out_band1)
    # out_band2 = Normalize(out_band2)
    # out_band3 = Normalize(out_band3)
    # out_band4 = Normalize(out_band4)

    # out_band1 = np.array((np.round(out_band1 * 255)), dtype='uint8')
    # out_band2 = np.array((np.round(out_band2 * 255)), dtype='uint8')
    # out_band3 = np.array((np.round(out_band3 * 255)), dtype='uint8')
    # out_band4 = np.array((np.round(out_band4 * 255)), dtype='uint8')

    # print(out_band1)
    # breakpoint()

    geomat = list(dataset.GetGeoTransform())
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

    geomat[1] /= level
    geomat[5] /= level

    # 将计算后的值组装为一个元组，以方便设置
    dst_transform = (top_left_x, geomat[1], geomat[2], top_left_y, geomat[4], geomat[5])

    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize*level, block_ysize*level, 1, in_band1.DataType)
    # print("create new tif file succeed")
    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(dst_transform)

    out_band = in_band1.ReadAsArray(buf_xsize=block_xsize * level, buf_ysize=block_ysize * level)
    # 设置SRS属性（投影信息）
    out_ds.SetProjection(dataset.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(0)
    # 写入目标文件  1234 = B G R N
    out_ds.GetRasterBand(1).WriteArray(out_band)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def Cliptif_4dim2gray(dataset_fall, dataset_summer, dataset_winter, outpath='test.tif',
                      offset_x=0, offset_y=0, block_xsize=128, block_ysize=128):
    # Fall
    in_band1 = dataset_fall.GetRasterBand(1)
    in_band2 = dataset_fall.GetRasterBand(2)
    in_band3 = dataset_fall.GetRasterBand(3)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)


    out_band_fall = []
    for i in range(len(out_band1)):
        gray = (out_band1[i] + out_band2[i] + out_band3[i]) / 3
        out_band_fall.append(gray)
    out_band_fall = np.array(out_band_fall)
    # out_band_fall = Normalize(out_band_fall)

    # summer
    in_band1 = dataset_summer.GetRasterBand(1)
    in_band2 = dataset_summer.GetRasterBand(2)
    in_band3 = dataset_summer.GetRasterBand(3)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    out_band_summer = []
    for i in range(len(out_band1)):
        gray = (out_band1[i] + out_band2[i] + out_band3[i]) / 3
        out_band_summer.append(gray)
    out_band_summer = np.array(out_band_summer)
    # out_band_summer = Normalize(out_band_summer)

    # winter
    in_band1 = dataset_winter.GetRasterBand(1)
    in_band2 = dataset_winter.GetRasterBand(2)
    in_band3 = dataset_winter.GetRasterBand(3)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    out_band_winter = []
    for i in range(len(out_band1)):
        gray = (out_band1[i] + out_band2[i] + out_band3[i]) / 3
        out_band_winter.append(gray)
    out_band_winter = np.array(out_band_winter)
    # out_band_winter = Normalize(out_band_winter)
    # print(out_band1)
    # breakpoint()
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（3代表3个不都按，最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 3, in_band1.DataType)
    # print("create new tif file succeed")
    geomat = dataset_fall.GetGeoTransform()
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
    out_ds.SetProjection(dataset_fall.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(-3.40282306074e+038)
    out_ds.GetRasterBand(2).SetNoDataValue(-3.40282306074e+038)
    out_ds.GetRasterBand(3).SetNoDataValue(-3.40282306074e+038)
    out_band_summer1 = np.zeros(out_band_summer.shape)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band_summer)
    out_ds.GetRasterBand(2).WriteArray(out_band_fall)
    out_ds.GetRasterBand(3).WriteArray(out_band_winter)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def cal_gaps(dataset, dataset_GT):
    geomat = dataset.GetGeoTransform()
    geomat_GT = dataset_GT.GetGeoTransform()
    x1 = geomat_GT[0]
    y1 = geomat_GT[3]
    dTemp = geomat[1] * geomat[5] - geomat[2] * geomat[4]
    x_gap = (geomat[5] * (x1 - geomat[0]) - geomat[2] * (y1 - geomat[3])) / dTemp + 0.5
    y_gap = (geomat[1] * (y1 - geomat[3]) - geomat[4] * (x1 - geomat[3])) / dTemp + 0.5
    return x_gap, y_gap


def Read_tif(tif_path):
    dataset = gdal.Open(tif_path, gdal.GA_Update)
    dataset.FlushCache()
    return dataset


def Upsample(path,output_path, dim = 1):
    Listfile, allFilename = file_name(path)
    predOutDir = output_path
    if not os.path.exists(predOutDir):
        os.makedirs(predOutDir)
    with tqdm(len(allFilename)) as pbar:
        for ii in range(len(allFilename)):
            savename = os.path.join(predOutDir, allFilename[ii] + '.tif')
            data = Read_tif(Listfile[ii])
            if dim == 1:
                Upsampletif_1dim(data,savename)
            else:
                Upsampletif_4dim(data,savename)

            del data
            pbar.update()


def Mixtif_4dim2gray(dataset_fall, dataset_summer, dataset_winter, outpath='test.tif',
                      offset_x=0, offset_y=0, block_xsize=512, block_ysize=512):
    # Fall
    in_band1 = dataset_fall.GetRasterBand(1)
    in_band2 = dataset_fall.GetRasterBand(2)
    in_band3 = dataset_fall.GetRasterBand(3)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band1 = Normalize(out_band1)*255
    out_band2 = Normalize(out_band2)*255
    out_band3 = Normalize(out_band3)*255

    out_band_fall = (out_band1+out_band2+out_band3) // 3.0
    out_band_fall = np.array(out_band_fall)
    # out_band_fall = Normalize(out_band_fall)

    # summer
    in_band1 = dataset_summer.GetRasterBand(1)
    in_band2 = dataset_summer.GetRasterBand(2)
    in_band3 = dataset_summer.GetRasterBand(3)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band1 = Normalize(out_band1)*255
    out_band2 = Normalize(out_band2)*255
    out_band3 = Normalize(out_band3)*255

    out_band_summer = (out_band1+out_band2+out_band3) // 3.0
    out_band_summer = np.array(out_band_summer)
    # out_band_summer = Normalize(out_band_summer)

    # winter
    in_band1 = dataset_winter.GetRasterBand(1)
    in_band2 = dataset_winter.GetRasterBand(2)
    in_band3 = dataset_winter.GetRasterBand(3)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band1 = Normalize(out_band1)*255
    out_band2 = Normalize(out_band2)*255
    out_band3 = Normalize(out_band3)*255
    out_band_winter = (out_band1+out_band2+out_band3) // 3.0

    out_band_winter = np.array(out_band_winter)
    # out_band_winter = Normalize(out_band_winter)
    # print(out_band1)
    # breakpoint()
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（3代表3个不都按，最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 3, in_band1.DataType)
    # print("create new tif file succeed")
    geomat = dataset_fall.GetGeoTransform()
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
    out_ds.SetProjection(dataset_fall.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(255)
    out_ds.GetRasterBand(2).SetNoDataValue(255)
    out_ds.GetRasterBand(3).SetNoDataValue(255)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band_summer)
    out_ds.GetRasterBand(2).WriteArray(out_band_fall)
    out_ds.GetRasterBand(3).WriteArray(out_band_winter)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def Mix_2tif(tif1, tif2, block_xsize, block_ysize, outpath='test.tif'):
    in_band1 = tif1.GetRasterBand(1)
    in_band2 = tif1.GetRasterBand(2)
    in_band3 = tif1.GetRasterBand(3)

    in_band4 = tif2.GetRasterBand(1)
    geomat = list(tif1.GetGeoTransform())

    top_left_x = geomat[0]  # 左上角x坐标
    w_e_pixel_resolution = geomat[1]  # 东西方向像素分辨率
    top_left_y = geomat[3]  # 左上角y坐标
    n_s_pixel_resolution = geomat[5]  # 南北方向像素分辨率
    # 将计算后的值组装为一个元组，以方便设置
    dst_transform = (top_left_x, geomat[1], geomat[2], top_left_y, geomat[4], geomat[5])
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 4, in_band1.DataType)
    # print("create new tif file succeed")
    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(dst_transform)

    out_band1 = in_band1.ReadAsArray()
    out_band2 = in_band2.ReadAsArray()
    out_band3 = in_band3.ReadAsArray()
    out_band4 = in_band4.ReadAsArray()

    out_band1 = Normalize(out_band1)*255
    out_band2 = Normalize(out_band2)*255
    out_band3 = Normalize(out_band3)*255
    out_band4 = Normalize(out_band4)*255

    # 设置SRS属性（投影信息）
    out_ds.SetProjection(tif2.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(-3.40282306074e+038)
    out_ds.GetRasterBand(2).SetNoDataValue(-3.40282306074e+038)
    out_ds.GetRasterBand(3).SetNoDataValue(-3.40282306074e+038)
    out_ds.GetRasterBand(4).SetNoDataValue(-3.40282306074e+038)
    # 写入目标文件  1234 = B G R N
    out_ds.GetRasterBand(1).WriteArray(out_band1)
    out_ds.GetRasterBand(2).WriteArray(out_band2)
    out_ds.GetRasterBand(3).WriteArray(out_band3)
    out_ds.GetRasterBand(4).WriteArray(out_band4)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def Mix():
    path_sr = r'D:\PythonProjects\DataProcess\Data\SR'
    path_nir = r'D:\PythonProjects\DataProcess\Upsample'
    Listfile, allFilename = file_name(path_sr)
    predOutDir = r'./SRMux'
    if not os.path.exists(predOutDir):
        os.makedirs(predOutDir)
    for ii in range(len(allFilename)):
        savename = os.path.join(predOutDir, allFilename[ii] + '.tif')
        print(savename)
        data_nir = os.path.join(path_nir, allFilename[ii] + '.tif')
        data_nir = Read_tif(data_nir)
        data = Read_tif(Listfile[ii])

        Mix_2tif(data, data_nir,512,512,savename)
        del data
        del data_nir


def make_city_dataset(city_img, fall_img, summer_img, winter_img, VVVH_img, city_gt, img_outpath,
                      fall_outpath, summer_outpath, winter_outpath, VVVH_outpath, all_path, gt_outpath, block_size):

    dataset = gdal.Open(city_img, gdal.GA_Update)
    dataset.FlushCache()
    dataset_fall = gdal.Open(fall_img, gdal.GA_Update)
    dataset_fall.FlushCache()
    dataset_summer = gdal.Open(summer_img, gdal.GA_Update)
    dataset_summer.FlushCache()
    dataset_winter = gdal.Open(winter_img, gdal.GA_Update)
    dataset_winter.FlushCache()
    dataset_VVVH = gdal.Open(VVVH_img, gdal.GA_Update)
    dataset_VVVH.FlushCache()
    dataset_GT = gdal.Open(city_gt, gdal.GA_Update)
    dataset_GT.FlushCache()

    gt_width = dataset_GT.RasterXSize
    gt_height = dataset_GT.RasterYSize

    xnum = math.floor(gt_width / block_size)
    ynum = math.floor(gt_height / block_size)
    # x_gap, y_gap = 0, 0
    x_gap, y_gap = cal_gaps(dataset, dataset_GT)
    x_gap_fall, y_gap_fall = cal_gaps(dataset_fall, dataset_GT)
    x_gap_summer, y_gap_summer = cal_gaps(dataset_summer, dataset_GT)
    x_gap_winter, y_gap_winter = cal_gaps(dataset_winter, dataset_GT)
    x_gap_VVVH, y_gap_VVVH = cal_gaps(dataset_VVVH, dataset_GT)

    with tqdm(total=int(xnum * ynum)) as pbar:
        for i in range(xnum):
            for j in range(ynum):
                x, y = i * block_size, j * block_size
                try:
                    if (
                    ClipGT_1dim(dataset_GT, outpath=gt_outpath + "_{0}_{1}.tif".format(i, j), offset_x=x, offset_y=y,
                                block_xsize=block_size, block_ysize=block_size, if_height = True)):
                        pass
                        # Cliptif_4dim(dataset, outpath=img_outpath + "_{0}_{1}.tif".format(i, j), offset_x=x + x_gap,
                        #              offset_y=y + y_gap, block_xsize=block_size, block_ysize=block_size)
                        # Cliptif_4dim(dataset_fall, outpath=fall_outpath + "_{0}_{1}.tif".format(i, j),
                        #              offset_x=x + x_gap_fall,
                        #              offset_y=y + y_gap_fall, block_xsize=block_size, block_ysize=block_size)
                        # Cliptif_4dim(dataset_summer, outpath=summer_outpath + "_{0}_{1}.tif".format(i, j),
                        #              offset_x=x + x_gap_summer,
                        #              offset_y=y + y_gap_summer, block_xsize=block_size, block_ysize=block_size)
                        # Cliptif_4dim(dataset_winter, outpath=winter_outpath + "_{0}_{1}.tif".format(i, j),
                        #              offset_x=x + x_gap_winter,
                        #              offset_y=y + y_gap_winter, block_xsize=block_size, block_ysize=block_size)
                        # ClipVVVH_2dim(dataset_VVVH, outpath=VVVH_outpath + "_{0}_{1}.tif".format(i, j),
                        #               offset_x= x + x_gap_VVVH,
                        #               offset_y= y + y_gap_VVVH, block_xsize=block_size, block_ysize=block_size)
                        # Cliptif_4dim2gray(dataset_fall, dataset_summer, dataset_winter,
                        #                   outpath=all_path + "_{0}_{1}.tif".format(i, j),
                        #                   offset_x=x + x_gap,
                        #                   offset_y=y + y_gap, block_xsize=block_size, block_ysize=block_size)
                except(ValueError):
                    print("Value Error")
                except(IOError):
                    print("IOE Error")
                pbar.update()
    del dataset
    del dataset_winter
    del dataset_fall
    del dataset_summer
    del dataset_GT


def main():

    Img_path = []
    GT_path = []
    fall_path = []
    summer_path = []
    winter_path = []
    VVVH_path = []
    for i in range(len(citynames)):
        img = r"D:\Dataset\52Cities\Image" + '\\' + citynames[i] + '.tif'
        gt = r"D:\Dataset\52Cities\Label" + '\\' + citynames[i] + '.tif'
        fall = r"D:\Dataset\52Cities\Image\fall\UTM" + '\\' + citynames[i] + '.tif'
        summer = r"D:\Dataset\52Cities\Image\summer\UTM" + '\\' + citynames[i] + '.tif'
        winter = r"D:\Dataset\52Cities\Image\winter\UTM" + '\\' + citynames[i] + '.tif'
        VVVH = r"D:\Dataset\52Cities\VVVH51N" + '\\' + citynames[i] + '.tif'
        Img_path.append(img)
        GT_path.append(gt)
        fall_path.append(fall)
        summer_path.append(summer)
        winter_path.append(winter)
        VVVH_path.append(VVVH)
    print("生在生成数据集——————————————")
    time.sleep(1)



    for i in range(len(citynames)):
        print("{0}".format(citynames[i]))
        time.sleep(1)
        make_city_dataset(city_img=Img_path[i],
                          fall_img=fall_path[i],
                          summer_img=summer_path[i],
                          winter_img=winter_path[i],
                          city_gt=GT_path[i],
                          VVVH_img=VVVH_path[i],
                          img_outpath=paths[3] + '\\'+ citynames[i],
                          fall_outpath=paths[4] + '\\'+ citynames[i],
                          summer_outpath=paths[5] + '\\'+ citynames[i],
                          winter_outpath=paths[6] + '\\'+ citynames[i],
                          VVVH_outpath =paths[7] + '\\'+ citynames[i],
                          gt_outpath=paths[8] + '\\'+ citynames[i],
                          all_path=paths[9] + '\\'+ citynames[i],
                          block_size=128
                          )


if __name__ == '__main__':
    main()
    input_path = paths[8]
    output_path = input_path + '_SR'
    Upsample(input_path, output_path, dim = 1)
    # Mix()
    # for season in ['summer']:
    #     Listfile, allFilename = file_name(r'D:/Desktop/season/' + season + '/ESPCN/SR/ESPCN')
    #
    #     predOutDir = r'./season/all'
    #     if not os.path.exists(predOutDir):
    #         os.makedirs(predOutDir)
    #     for ii in range(len(allFilename)):
    #         Listfile_winter = Listfile[ii].replace('summer','winter')
    #         # print(Listfile_winter)
    #         Listfile_fall = Listfile[ii].replace('summer', 'fall')
    #         # print(Listfile_fall)
    #         savename = os.path.join(predOutDir, allFilename[ii] + '.tif')
    #         print(savename)
    #
    #         summer_data = Read_tif(Listfile[ii])
    #         winter_data = Read_tif(Listfile_winter)
    #         fall_data = Read_tif(Listfile_fall)
    #         Mixtif_4dim2gray(fall_data,summer_data,winter_data,savename)



