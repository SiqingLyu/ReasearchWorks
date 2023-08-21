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
import tifffile as tif
'''--------------------------Configs-------------------------'''
Nodata_lab = 0
Nodata_img = 0
Nodata_VVH = -1.797693e+308
folder = 'TEST_VVH'
paths = [rf'\Data\{folder}', rf'\Data\{folder}\image', rf'\Data\{folder}\image\season',
             rf'.\Data\{folder}\image\optical',  # 3
             rf'.\Data\{folder}\image\season\fall',  # 4
             rf'.\Data\{folder}\image\season\summer',  # 5
             rf'.\Data\{folder}\image\season\winter',  # 6
             rf".\Data\{folder}\image\VVVH",  # 7
             rf'.\Data\{folder}\label',  # 8
             rf'.\Data\{folder}\image\season\all' , # 9
             rf'.\Data\{folder}\image\season\spring' # 10
             ]


def make_dir(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)

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
            'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan']# 'Shenyang',
citynames = ['Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
             'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Changsha', 'Huizhou', 'Lanzhou', 'Luoyang']  # "Yantai"
# citynames = ["Shenzhen","Xiamen","Guiyang", "Chengdu"]
# citynames = [ 'Huizhou', 'Lanzhou', 'Luoyang']
# citynames = [ 'Changsha']
'''--------------------------Configs-------------------------'''


def Normalize(array, outpath):
    '''
    Normalize the array
    '''
    array[array > 1e10] = 0
    array[array < -1e10] = 0
    mx = np.nanmax(array)
    mn = np.nanmin(array)
    # assert mx!=mn
    if mx == mn:
        print(outpath, 'value is :', mx)
        t = np.zeros_like(array)
        t[t==0] = mx
    t = (array-mn)/((mx-mn))
    return t


def Normalize_VVH(array, outpath):
    '''
    Normalize the array
    '''

    mx = np.max(array)
    mn = np.min(array)
    if mx > 100:
        print(outpath, 'value is :', mx)
        # print('------', mn)
    array_temp = np.where(array>-100000, array, mx)
    mn = np.nanmin(array_temp)
    # print('======', mn)

    if mx == mn:
        print(outpath, 'value is :', mx)
        t = np.zeros_like(array)
        t[t==0] = mx

    array = np.where(array>-100000, array, mn)
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
                offset_y=0, block_xsize=128, block_ysize=128, if_get_height = False):
    in_band_VV = dataset_VVVH.GetRasterBand(1)
    in_band_VH = dataset_VVVH.GetRasterBand(2)
    out_band_VV = in_band_VV.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band_VH = in_band_VH.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    if np.any(out_band_VV < -10000):
        return False
    if np.any(out_band_VH < -10000):
        return False

    out_band_VV= Normalize_VVH(out_band_VV, outpath)
    out_band_VH = Normalize_VVH(out_band_VH, outpath)

    # VVH = VV * γ^VH (γ = 5)
    out_band = out_band_VV * pow(5,out_band_VH)

    # print(np.min(out_band))
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
    out_ds.GetRasterBand(1).SetNoDataValue(0.0)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def ClipVVVH_2dim_500(dataset_VVVH, outpath='VVVH.tif', offset_x=0,
                offset_y=0, block_xsize=128, block_ysize=128, if_get_height = False):
    in_band_VV = dataset_VVVH.GetRasterBand(1)
    in_band_VH = dataset_VVVH.GetRasterBand(2)
    out_band_VV = in_band_VV.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band_VH = in_band_VH.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band_VV = Normalize_VVH(out_band_VV, outpath)
    out_band_VH = Normalize_VVH(out_band_VH, outpath) * 0.5

    out_band_VV_500 = np.array([np.mean(out_band_VV[20:70, 20: 70]), np.mean(out_band_VV[70:120, 70:120]),
                        np.mean(out_band_VV[70:120, 20: 70]), np.mean(out_band_VV[20: 70, 70:120])])
    out_band_VH_500 = np.array([np.mean(out_band_VH[20:70, 20: 70]), np.mean(out_band_VH[70:120, 70:120]),
                                np.mean(out_band_VH[70:120, 20: 70]), np.mean(out_band_VH[20: 70, 70:120])])
    # VVH = VV * γ^VH (γ = 5)
    out_band = out_band_VV_500 * pow(5,out_band_VH_500)
    tif.imsave(outpath, out_band)

def SetGT_Nodata(dataset_GT, outpath='GT.tif'):

    in_band1 = dataset_GT.GetRasterBand(1)
    out_band1 = in_band1.ReadAsArray()
    block_xsize, block_ysize = out_band1.shape[1], out_band1.shape[0]
    out_band1[np.where( out_band1 == 255 )] = Nodata_lab
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
    top_left_x = top_left_x
    top_left_y = top_left_y

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

def ClipGT_1dim(dataset_GT, outpath='GT.tif', offset_x=0,
                offset_y=0, block_xsize=128, block_ysize=128, if_height = False, if_test=False):

    in_band1 = dataset_GT.GetRasterBand(1)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    # if not if_test:
    if np.all(out_band1 == 255):
        return False
    sum = 0
    for da in out_band1:
        for i in da:
            if i < 255:
                sum += 1
    if sum < 0.05 * block_xsize * block_ysize:
    # if sum == 0:
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
    out_band1[out_band1 < -1e+10] = 0
    if np.max(out_band1) == np.min(out_band1):
        print("这张图片存在问题：", outpath)
    out_band2[out_band2 < -1e+10] = 0
    if np.max(out_band2) == np.min(out_band2):
        print("这张图片存在问题：", outpath)
    out_band3[out_band3 < -1e+10] = 0
    if np.max(out_band3) == np.min(out_band3):
        print("这张图片存在问题：", outpath)
    out_band4[out_band4 < -1e+10] = 0
    if np.max(out_band4) == np.min(out_band4):
        print("这张图片存在问题：", outpath)

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


def Upsampletif_4dim(dataset, outpath='Upsample.tif', offset_x=0, offset_y=0,
                 block_xsize=128, block_ysize=128, level=4):
    in_band1 = dataset.GetRasterBand(1)
    in_band2 = dataset.GetRasterBand(2)
    in_band3 = dataset.GetRasterBand(3)
    in_band4 = dataset.GetRasterBand(4)

    geomat = list(dataset.GetGeoTransform())

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
    geomat = list(dataset.GetGeoTransform())

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
    out_band = Normalize(out_band), outpath
    out_ds.SetProjection(dataset.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(-1.797693e+308)
    # 写入目标文件  1234 = B G R N
    out_ds.GetRasterBand(1).WriteArray(out_band)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def Cliptif_4dim2gray(dataset_spring, dataset_fall, dataset_summer, dataset_winter, outpath='test.tif',
                      offset_x=0, offset_y=0, block_xsize=128, block_ysize=128):
    # Spring
    in_band1 = dataset_spring.GetRasterBand(1)
    in_band2 = dataset_fall.GetRasterBand(2)
    in_band3 = dataset_fall.GetRasterBand(3)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band1[out_band1 < -1e+10] = 0
    if np.max(out_band1) == np.min(out_band1):
        print("这张图片存在问题：", outpath)
    out_band2[out_band2 < -1e+10] = 0
    if np.max(out_band2) == np.min(out_band2):
        print("这张图片存在问题：", outpath)
    out_band3[out_band3 < -1e+10] = 0
    if np.max(out_band3) == np.min(out_band3):
        print("这张图片存在问题：", outpath)
    # out_band4[out_band4 < -1e+10] = 0
    # if np.max(out_band4) == np.min(out_band4):
    #     print("这张图片存在问题：", outpath)
    out_band_spring = []
    for i in range(len(out_band1)):
        gray = (out_band1[i] + out_band2[i] + out_band3[i]) / 3
        out_band_spring.append(gray)
    out_band_spring = np.array(out_band_spring)

    # Fall
    in_band1 = dataset_fall.GetRasterBand(1)
    in_band2 = dataset_fall.GetRasterBand(2)
    in_band3 = dataset_fall.GetRasterBand(3)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band1[out_band1 < -1e+10] = 0
    if np.max(out_band1) == np.min(out_band1):
        print("这张图片存在问题：", outpath)
    out_band2[out_band2 < -1e+10] = 0
    if np.max(out_band2) == np.min(out_band2):
        print("这张图片存在问题：", outpath)
    out_band3[out_band3 < -1e+10] = 0
    if np.max(out_band3) == np.min(out_band3):
        print("这张图片存在问题：", outpath)
    # out_band4[out_band4 < -1e+10] = 0
    # if np.max(out_band4) == np.min(out_band4):
    #     print("这张图片存在问题：", outpath)

    out_band_fall = []
    for i in range(len(out_band1)):
        gray = (out_band1[i] + out_band2[i] + out_band3[i]) / 3
        out_band_fall.append(gray)
    out_band_fall = np.array(out_band_fall)
    # out_band_fall = Normalize(out_band_, outpathfall)

    # summer
    in_band1 = dataset_summer.GetRasterBand(1)
    in_band2 = dataset_summer.GetRasterBand(2)
    in_band3 = dataset_summer.GetRasterBand(3)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band1[out_band1 < -1e+10] = 0
    if np.max(out_band1) == np.min(out_band1):
        print("这张图片存在问题：", outpath)
    out_band2[out_band2 < -1e+10] = 0
    if np.max(out_band2) == np.min(out_band2):
        print("这张图片存在问题：", outpath)
    out_band3[out_band3 < -1e+10] = 0
    if np.max(out_band3) == np.min(out_band3):
        print("这张图片存在问题：", outpath)
    # out_band4[out_band4 < -1e+10] = 0
    # if np.max(out_band4) == np.min(out_band4):
    #     print("这张图片存在问题：", outpath)
    out_band_summer = []
    for i in range(len(out_band1)):
        gray = (out_band1[i] + out_band2[i] + out_band3[i]) / 3
        out_band_summer.append(gray)
    out_band_summer = np.array(out_band_summer)

    # winter
    in_band1 = dataset_winter.GetRasterBand(1)
    in_band2 = dataset_winter.GetRasterBand(2)
    in_band3 = dataset_winter.GetRasterBand(3)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band1[out_band1 < -1e+10] = 0
    if np.max(out_band1) == np.min(out_band1):
        print("这张图片存在问题：", outpath)
    out_band2[out_band2 < -1e+10] = 0
    if np.max(out_band2) == np.min(out_band2):
        print("这张图片存在问题：", outpath)
    out_band3[out_band3 < -1e+10] = 0
    if np.max(out_band3) == np.min(out_band3):
        print("这张图片存在问题：", outpath)
    # out_band4[out_band4 < -1e+10] = 0
    # if np.max(out_band4) == np.min(out_band4):
    #     print("这张图片存在问题：", outpath)
    out_band_winter = []
    for i in range(len(out_band1)):
        gray = (out_band1[i] + out_band2[i] + out_band3[i]) / 3
        out_band_winter.append(gray)
    out_band_winter = np.array(out_band_winter)

    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（3代表3个不都按，最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 4, in_band1.DataType)
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
    out_ds.GetRasterBand(1).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(2).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(3).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(4).SetNoDataValue(Nodata_img)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band_spring)
    out_ds.GetRasterBand(2).WriteArray(out_band_summer)
    out_ds.GetRasterBand(3).WriteArray(out_band_fall)
    out_ds.GetRasterBand(4).WriteArray(out_band_winter)


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
    x_gap = (geomat[5] * (x1 - geomat[0]) - geomat[2] * (y1 - geomat[3])) / dTemp
    y_gap = (geomat[1] * (y1 - geomat[3]) - geomat[4] * (x1 - geomat[3])) / dTemp
    # print("dataset_a: x0:{0}, y0:{1}\ndataset_gt: x0:{2}, y0:{3}".format(geomat[0], geomat[3], geomat_GT[0], geomat_GT[3]))

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


def Mixtif_4dim2gray(dataset_spring, dataset_fall, dataset_summer, dataset_winter, outpath='test.tif',
                      offset_x=0, offset_y=0, block_xsize=128, block_ysize=128):
    # Spring
    in_band1 = dataset_spring.GetRasterBand(1)
    in_band2 = dataset_spring.GetRasterBand(2)
    in_band3 = dataset_spring.GetRasterBand(3)
    in_band4 = dataset_spring.GetRasterBand(4)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band4 = in_band4.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band1 = Normalize(out_band1, outpath) * 255
    out_band2 = Normalize(out_band2, outpath) * 255
    out_band3 = Normalize(out_band3, outpath) * 255
    out_band4 = Normalize(out_band3, outpath) * 255
    out_band_spring = (out_band1 + out_band2 + out_band3) // 3.0
    out_band_spring = np.array(out_band_spring)
    # Fall
    in_band1 = dataset_fall.GetRasterBand(1)
    in_band2 = dataset_fall.GetRasterBand(2)
    in_band3 = dataset_fall.GetRasterBand(3)
    out_band4 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band5 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band6 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band4 = Normalize(out_band4, outpath)*255
    out_band5 = Normalize(out_band5, outpath)*255
    out_band6 = Normalize(out_band6, outpath)*255
    out_band_fall = (out_band4+out_band5+out_band6) // 3.0
    out_band_fall = np.array(out_band_fall)
    # out_band_fall = Normalize(out_band_, outpathfall)

    # summer
    in_band1 = dataset_summer.GetRasterBand(1)
    in_band2 = dataset_summer.GetRasterBand(2)
    in_band3 = dataset_summer.GetRasterBand(3)
    out_band7 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band8 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band9 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band7 = Normalize(out_band7, outpath)*255
    out_band8 = Normalize(out_band8, outpath)*255
    out_band9 = Normalize(out_band9, outpath)*255
    out_band_summer = (out_band7+out_band8+out_band9) // 3.0
    out_band_summer = np.array(out_band_summer)
    # out_band_summer = Normalize(out_band_, outpathsummer)

    # winter
    in_band1 = dataset_winter.GetRasterBand(1)
    in_band2 = dataset_winter.GetRasterBand(2)
    in_band3 = dataset_winter.GetRasterBand(3)
    out_band10 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band11 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band12 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band10 = Normalize(out_band1, outpath0)*255
    out_band11 = Normalize(out_band1, outpath1)*255
    out_band12 = Normalize(out_band1, outpath2)*255
    out_band_winter = (out_band10+out_band11+out_band12) // 3.0
    out_band_winter = np.array(out_band_winter)
    # out_band_winter = Normalize(out_band_, outpathwinter)
    # print(out_band1)
    # breakpoint()
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（3代表3个不都按，最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 4, in_band1.DataType)
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
    out_ds.GetRasterBand(1).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(2).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(3).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(4).SetNoDataValue(Nodata_img)
    # out_ds.GetRasterBand(5).SetNoDataValue(Nodata_img)
    # out_ds.GetRasterBand(6).SetNoDataValue(Nodata_img)
    # out_ds.GetRasterBand(7).SetNoDataValue(Nodata_img)
    # out_ds.GetRasterBand(8).SetNoDataValue(Nodata_img)
    # out_ds.GetRasterBand(9).SetNoDataValue(Nodata_img)
    # out_ds.GetRasterBand(10).SetNoDataValue(Nodata_img)
    # out_ds.GetRasterBand(11).SetNoDataValue(Nodata_img)
    # out_ds.GetRasterBand(12).SetNoDataValue(Nodata_img)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band_spring)
    out_ds.GetRasterBand(2).WriteArray(out_band_summer)
    out_ds.GetRasterBand(3).WriteArray(out_band_fall)
    out_ds.GetRasterBand(4).WriteArray(out_band_winter)
    # out_ds.GetRasterBand(5).WriteArray(out_band5)
    # out_ds.GetRasterBand(6).WriteArray(out_band6)
    # out_ds.GetRasterBand(7).WriteArray(out_band7)
    # out_ds.GetRasterBand(8).WriteArray(out_band8)
    # out_ds.GetRasterBand(9).WriteArray(out_band9)
    # out_ds.GetRasterBand(10).WriteArray(out_band10)
    # out_ds.GetRasterBand(11).WriteArray(out_band11)
    # out_ds.GetRasterBand(12).WriteArray(out_band12)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def Mixtif_4season(dataset_spring, dataset_summer, dataset_fall, dataset_winter, outpath='test.tif',
                      offset_x=0, offset_y=0, block_xsize=128, block_ysize=128):
    # Spring
    in_band1 = dataset_spring.GetRasterBand(1)
    in_band2 = dataset_spring.GetRasterBand(2)
    in_band3 = dataset_spring.GetRasterBand(3)
    in_band4 = dataset_spring.GetRasterBand(4)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band4 = in_band4.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    # Summer
    in_band1 = dataset_summer.GetRasterBand(1)
    in_band2 = dataset_summer.GetRasterBand(2)
    in_band3 = dataset_summer.GetRasterBand(3)
    in_band4 = dataset_summer.GetRasterBand(4)
    out_band5 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band6 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band7 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band8 = in_band4.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    # fall
    in_band1 = dataset_fall.GetRasterBand(1)
    in_band2 = dataset_fall.GetRasterBand(2)
    in_band3 = dataset_fall.GetRasterBand(3)
    in_band4 = dataset_fall.GetRasterBand(4)
    out_band9 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band10 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band11 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band12 = in_band4.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    # winter
    in_band1 = dataset_winter.GetRasterBand(1)
    in_band2 = dataset_winter.GetRasterBand(2)
    in_band3 = dataset_winter.GetRasterBand(3)
    in_band4 = dataset_winter.GetRasterBand(4)
    out_band13 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band14 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band15 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band16 = in_band4.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（3代表3个不都按，最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 16, in_band1.DataType)
    # print("create new tif file succeed")
    geomat = dataset_fall.GetGeoTransform()

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
    out_ds.GetRasterBand(1).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(2).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(3).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(4).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(5).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(6).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(7).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(8).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(9).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(10).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(11).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(12).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(13).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(14).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(15).SetNoDataValue(Nodata_img)
    out_ds.GetRasterBand(16).SetNoDataValue(Nodata_img)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band1)
    out_ds.GetRasterBand(2).WriteArray(out_band2)
    out_ds.GetRasterBand(3).WriteArray(out_band3)
    out_ds.GetRasterBand(4).WriteArray(out_band4)
    out_ds.GetRasterBand(5).WriteArray(out_band5)
    out_ds.GetRasterBand(6).WriteArray(out_band6)
    out_ds.GetRasterBand(7).WriteArray(out_band7)
    out_ds.GetRasterBand(8).WriteArray(out_band8)
    out_ds.GetRasterBand(9).WriteArray(out_band9)
    out_ds.GetRasterBand(10).WriteArray(out_band10)
    out_ds.GetRasterBand(11).WriteArray(out_band11)
    out_ds.GetRasterBand(12).WriteArray(out_band12)
    out_ds.GetRasterBand(13).WriteArray(out_band13)
    out_ds.GetRasterBand(14).WriteArray(out_band14)
    out_ds.GetRasterBand(15).WriteArray(out_band15)
    out_ds.GetRasterBand(16).WriteArray(out_band16)

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

    out_band1 = Normalize(out_band1, outpath)*255
    out_band2 = Normalize(out_band2, outpath)*255
    out_band3 = Normalize(out_band3, outpath)*255
    out_band4 = Normalize(out_band4, outpath)*255

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

        Mix_2tif(data, data_nir,128,128,savename)
        del data
        del data_nir


def Mix_season(path):
    spring_path = path + '\\' + 'spring_'
    summer_path = path + '\\' + 'summer_'
    fall_path = path + '\\' + 'fall_'
    winter_path = path + '\\' + 'winter_'

    Listfile, allFilename = file_name(spring_path)
    predOutDir = path + '\\' + 'all_16channel_'
    if not os.path.exists(predOutDir):
        os.makedirs(predOutDir)
    with tqdm(total=len(allFilename)) as pbar:
        for ii in range(len(allFilename)):
            spring_file = Listfile[ii]
            summer_file = summer_path + '\\' + allFilename[ii] + '.tif'
            fall_file = fall_path + '\\' + allFilename[ii] + '.tif'
            winter_file = winter_path + '\\' + allFilename[ii] + '.tif'
            savename = os.path.join(predOutDir, allFilename[ii] + '.tif')
            # print(spring_file,'\n',summer_file,'\n', fall_file, '\n', winter_file, '\n', savename)
            data_spring = Read_tif(spring_file)
            data_summer = Read_tif(summer_file)
            data_fall = Read_tif(fall_file)
            data_winter = Read_tif(winter_file)


            Mixtif_4season(dataset_spring=data_spring, dataset_summer=data_summer, dataset_fall=data_fall,dataset_winter=data_winter,
                             outpath=savename, block_ysize=128,block_xsize=128)
            del data_spring
            del data_summer
            del data_fall
            del data_winter
            pbar.update()


def Mix_season_tif(path):
    spring_path = path + '\\' + 'spring'
    summer_path = path + '\\' + 'summer'
    fall_path = path + '\\' + 'fall'
    winter_path = path + '\\' + 'winter'

    Listfile, allFilename = file_name(spring_path)
    predOutDir = path + '\\' + 'all_16channel'
    if not os.path.exists(predOutDir):
        os.makedirs(predOutDir)
    with tqdm(total=len(allFilename)) as pbar:
        for ii in range(len(allFilename)):
            spring_file = Listfile[ii]
            summer_file = summer_path + '\\' + allFilename[ii] + '.tif'
            fall_file = fall_path + '\\' + allFilename[ii] + '.tif'
            winter_file = winter_path + '\\' + allFilename[ii] + '.tif'
            savename = os.path.join(predOutDir, allFilename[ii] + '.tif')
            # print(spring_file,'\n',summer_file,'\n', fall_file, '\n', winter_file, '\n', savename)
            spring = tif.imread(spring_file)
            spring[spring < -3e+20] = 0
            # print(np.max(spring), np.min(spring))
            summer = tif.imread(summer_file)
            summer[summer < -3e+20] = 0
            fall = tif.imread(fall_file)
            fall[fall < -3e+20] = 0
            winter = tif.imread(winter_file)
            winter[winter < -3e+20] = 0
            all = np.concatenate((spring, summer, fall, winter), axis=2)
            tif.imsave(savename, all)
            pbar.update()

def make_city_dataset(city_img, fall_img, summer_img,spring_img, winter_img, VVVH_img, city_gt, img_outpath, spring_outpath,
                      fall_outpath, summer_outpath, winter_outpath, VVVH_outpath, all_path, gt_outpath, block_size):

    dataset = gdal.Open(city_img, gdal.GA_Update)
    dataset.FlushCache()
    dataset_spring = gdal.Open(spring_img, gdal.GA_Update)
    dataset_spring.FlushCache()
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
    # print(x_gap,y_gap)
    x_gap_spring, y_gap_spring = cal_gaps(dataset_fall, dataset_GT)
    x_gap_fall, y_gap_fall = cal_gaps(dataset_fall, dataset_GT)
    x_gap_summer, y_gap_summer = cal_gaps(dataset_summer, dataset_GT)
    x_gap_winter, y_gap_winter = cal_gaps(dataset_winter, dataset_GT)
    x_gap_VVVH, y_gap_VVVH = cal_gaps(dataset_VVVH, dataset_GT)

    with tqdm(total=int(xnum * ynum)) as pbar:
        for i in range(xnum):
            for j in range(ynum):
                x, y = i * block_size, j * block_size
                try:
                    if ( ClipVVVH_2dim(dataset_VVVH, outpath=VVVH_outpath + "_{0}_{1}.tif".format(i, j),         #VVH
                                      offset_x= x + x_gap_VVVH,
                                      offset_y= y + y_gap_VVVH, block_xsize=block_size, block_ysize=block_size)

                    ):
                        pass

                        ClipGT_1dim(dataset_GT, outpath=gt_outpath + "_{0}_{1}.tif".format(i, j), offset_x=x,
                                    offset_y=y,
                                    block_xsize=block_size, block_ysize=block_size, if_height=False, if_test=False)

                except(ValueError):
                    print("Value Error")
                except(IOError):
                    print("IOE Error")
                pbar.update()
    del dataset
    del dataset_spring
    del dataset_winter
    del dataset_fall
    del dataset_summer
    del dataset_GT
    del dataset_VVVH


def main():

    Img_path = []
    GT_path = []
    spring_path = []
    fall_path = []
    summer_path = []
    winter_path = []
    VVVH_path = []
    for i in range(len(citynames)):
        img = r"D:\Dataset\@62allcities\MUXs_UTM" + '\\' + citynames[i] + '.tif'
        gt = r"D:\Dataset\@62allcities\Label" + '\\' + citynames[i] + '.tif'
        spring = r'D:\Dataset\@62allcities\SSNs_UTM\spring' + '\\' + citynames[i] + '.tif'
        fall = r"D:\Dataset\@62allcities\SSNs_UTM\fall" + '\\' + citynames[i] + '.tif'
        summer = r"D:\Dataset\@62allcities\SSNs_UTM\summer" + '\\' + citynames[i] + '.tif'
        winter = r"D:\Dataset\@62allcities\SSNs_UTM\winter" + '\\' + citynames[i] + '.tif'
        VVVH = r"D:\Dataset\@62allcities\SARs_UTM" + '\\' + citynames[i] + '.tif'

        Img_path.append(img)
        GT_path.append(gt)
        spring_path.append(spring)
        fall_path.append(fall)
        summer_path.append(summer)
        winter_path.append(winter)
        VVVH_path.append(VVVH)
    print("生在生成数据集——————————————")
    time.sleep(1)
    for i in range(len(citynames)):
        print("{0}".format(citynames[i]))

        # dataset_GT = gdal.Open(GT_path[i], gdal.GA_Update)
        # dataset_GT.FlushCache()
        # SetGT_Nodata(dataset_GT, outpath= paths[8] + '\\' + citynames[i] + '.tif')
        time.sleep(1)
        make_city_dataset(city_img=Img_path[i],
                          spring_img= spring_path[i],
                          fall_img=fall_path[i],
                          summer_img=summer_path[i],
                          winter_img=winter_path[i],
                          city_gt=GT_path[i],
                          VVVH_img=VVVH_path[i],
                          img_outpath=paths[3] + '\\'+ citynames[i],
                          spring_outpath = paths[10] + '\\'+ citynames[i],
                          fall_outpath=paths[4] + '\\' + citynames[i],
                          summer_outpath=paths[5] + '\\' + citynames[i],
                          winter_outpath=paths[6] + '\\' + citynames[i],
                          VVVH_outpath =paths[7] + '\\' + citynames[i],
                          gt_outpath=paths[8] + '\\' + citynames[i],
                          all_path=paths[9] + '\\' + citynames[i],
                          block_size=128
                          )


if __name__ == '__main__':
    main()
    # input_path = paths[7]
    # output_path = input_path + '_SR'
    # Upsample(input_path, output_path, dim = 1)
    # Mix_season(r'D:\Dataset\Mydata_all\SSN_UTM')
    # Mix_season(r'D:\PythonProjects\DataProcess\Data\image\season')
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



