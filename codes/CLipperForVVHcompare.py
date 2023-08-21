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
folder = 'VVH_from_VVVH'
paths = [rf'\Data\{folder}', rf'\Data\{folder}\image',
             rf".\Data\{folder}\image\VVVH",  # 2
             rf'.\Data\{folder}\label',  # 3
            rf'.\Data\{folder}\VVVH\VV',  # 4
            rf'.\Data\{folder}\VVVH\VH',  # 5

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
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan',  #]  # 'Shenyang',
             'Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
             'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Changsha', 'Huizhou', 'Lanzhou', 'Luoyang'
             ]
# citynames = ['Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
#              'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Changsha', 'Huizhou', 'Lanzhou', 'Luoyang']  # "Yantai"
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


def ClipVVVH_1dim(dataset_VVH, outpath='VVH.tif', offset_x=0,
                offset_y=0, block_xsize=128, block_ysize=128):
    in_band_VVH = dataset_VVH.GetRasterBand(1)
    out_band_VVH = in_band_VVH.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    # print(np.min(out_band))
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 1, in_band_VVH.DataType)
    # print("create new tif file succeed")
    geomat = dataset_VVH.GetGeoTransform()
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
    out_ds.SetProjection(dataset_VVH.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(0.0)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band_VVH)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def ClipVV_1dim(dataset_VV, outpath='VVH.tif', offset_x=0,
                offset_y=0, block_xsize=128, block_ysize=128):
    in_band_VVH = dataset_VV.GetRasterBand(1)
    out_band_VVH = in_band_VVH.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    # print(np.min(out_band))
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 1, in_band_VVH.DataType)
    # print("create new tif file succeed")
    geomat = dataset_VV.GetGeoTransform()
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
    out_ds.SetProjection(dataset_VV.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(0.0)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band_VVH)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds


def ClipVH_1dim(dataset_VH, outpath='VVH.tif', offset_x=0,
                offset_y=0, block_xsize=128, block_ysize=128):
    in_band_VVH = dataset_VH.GetRasterBand(1)
    out_band_VVH = in_band_VVH.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    # print(np.min(out_band))
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(outpath, block_xsize, block_ysize, 1, in_band_VVH.DataType)
    # print("create new tif file succeed")
    geomat = dataset_VH.GetGeoTransform()
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
    out_ds.SetProjection(dataset_VH.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(0.0)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band_VVH)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    # print("FlushCache succeed")
    del out_ds



def ClipGT_1dim(dataset_GT, outpath='GT.tif', offset_x=0,
                offset_y=0, block_xsize=128, block_ysize=128, if_height = False, if_test=False):

    in_band1 = dataset_GT.GetRasterBand(1)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    # if not if_test:
    if np.all(out_band1 == 0):
        return False
    sum = 0
    for da in out_band1:
        for i in da:
            if i > 0:
                sum += 1
    # if sum < 0.03 * block_xsize * block_ysize:
    if sum <= 1:
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

def make_city_dataset(VVVH_img, VV_img, VH_img, city_gt, VVVH_outpath, VV_outpath, VH_outpath, gt_outpath, block_size):

    dataset_VVVH = gdal.Open(VVVH_img, gdal.GA_Update)
    dataset_VVVH.FlushCache()
    dataset_VV = gdal.Open(VV_img, gdal.GA_Update)
    dataset_VV.FlushCache()
    dataset_VH = gdal.Open(VH_img, gdal.GA_Update)
    dataset_VH.FlushCache()
    dataset_GT = gdal.Open(city_gt, gdal.GA_Update)
    dataset_GT.FlushCache()

    gt_width = dataset_GT.RasterXSize
    gt_height = dataset_GT.RasterYSize

    xnum = math.floor(gt_width / block_size)
    ynum = math.floor(gt_height / block_size)

    x_gap_VVVH, y_gap_VVVH = cal_gaps(dataset_VVVH, dataset_GT)
    x_gap_VV, y_gap_VV = cal_gaps(dataset_VV, dataset_GT)
    x_gap_VH, y_gap_VH = cal_gaps(dataset_VH, dataset_GT)
    assert x_gap_VV==x_gap_VV and y_gap_VV==y_gap_VH

    with tqdm(total=int(xnum * ynum)) as pbar:
        for i in range(xnum):
            for j in range(ynum):
                x, y = i * block_size, j * block_size
                try:
                    if ( ClipGT_1dim(dataset_GT, outpath=gt_outpath + "_{0}_{1}.tif".format(i, j), offset_x=x,
                                    offset_y=y,
                                    block_xsize=block_size, block_ysize=block_size, if_height=False, if_test=False)
                    ):
                        pass
                        # ClipVVVH_1dim(dataset_VVVH, outpath=VVVH_outpath + "_{0}_{1}.tif".format(i, j),         #VVH
                        #               offset_x= x + x_gap_VVVH,
                        #               offset_y= y + y_gap_VVVH, block_xsize=block_size, block_ysize=block_size)
                        ClipVV_1dim(dataset_VV, outpath=VV_outpath + "_{0}_{1}.tif".format(i, j),  # VVH
                                      offset_x=x + x_gap_VV,
                                      offset_y=y + y_gap_VV, block_xsize=block_size, block_ysize=block_size)
                        ClipVH_1dim(dataset_VH, outpath=VH_outpath + "_{0}_{1}.tif".format(i, j),  # VVH
                                      offset_x=x + x_gap_VH,
                                      offset_y=y + y_gap_VH, block_xsize=block_size, block_ysize=block_size)

                except(ValueError):
                    print("Value Error")
                except(IOError):
                    print("IOE Error")
                pbar.update()
    del dataset_GT
    del dataset_VVVH


def main():
    GT_path = []
    VVVH_path = []
    VV_path = []
    VH_path = []
    for i in range(len(citynames)):
        gt = r"D:\Dataset\@62allcities\Label_bk0_nodata0" + '\\' + citynames[i] + '.tif'
        VVVH = r"D:\Dataset\@62allcities\VVHs_nodata0" + '\\' + citynames[i] + '.tif'
        VV = r"D:\Dataset\@62allcities\VVHs_nodata0\VV_nodata0" + '\\' + citynames[i] + '.tif'
        VH = r"D:\Dataset\@62allcities\VVHs_nodata0\VH_nodata0" + '\\' + citynames[i] + '.tif'
        GT_path.append(gt)
        VV_path.append(VV)
        VH_path.append(VH)
        VVVH_path.append(VVVH)
    print("生在生成数据集——————————————")
    time.sleep(1)
    for i in range(len(citynames)):
        print("{0}".format(citynames[i]))
        time.sleep(1)
        make_city_dataset(
                          city_gt=GT_path[i],
                          VVVH_img=VVVH_path[i],
                          VV_img=VV_path[i],
                          VH_img=VH_path[i],
                          VVVH_outpath =paths[2] + '\\' + citynames[i],
                          VV_outpath =paths[4] + '\\' + citynames[i],
                          VH_outpath =paths[5] + '\\' + citynames[i],
                          gt_outpath=paths[3] + '\\' + citynames[i],
                          block_size=50
                          )


if __name__ == '__main__':
    main()
