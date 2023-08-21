import gdal
import numpy as np


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


def Read_tif(tif_path):
    dataset = gdal.Open(tif_path, gdal.GA_Update)
    dataset.FlushCache()
    return dataset


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


if __name__ == '__main__':
    filepath = r''
    savename = r''
    data = Read_tif(filepath)
    Upsampletif_1dim(data, savename)

