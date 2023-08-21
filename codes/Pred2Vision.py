from tools import *
import numpy as np
from osgeo import gdal
import math
import time
from tqdm import tqdm
import os
import shapefile

Nodata_lab = 2147483647
Nodata_img = -3.40282346639e+038


def convert_truevalue_255_1(tif_data, reference_data, output_path, block_size = 256):
    in_band1 = tif_data.GetRasterBand(1)
    out_band1 = in_band1.ReadAsArray()
    out_band1 = np.where(out_band1 == 255, 1, out_band1)
    gtif_driver = gdal.GetDriverByName("GTiff")
    # 创建切出来的要存的文件（最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create(output_path, block_size, block_size, 1, in_band1.DataType)
    geomat = reference_data.GetGeoTransform()
    # 读取参考图像仿射变换参数值
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
    out_ds.SetProjection(reference_data.GetProjection())
    out_ds.GetRasterBand(1).SetNoDataValue(Nodata_lab)
    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band1)
    # 将缓存写入磁盘
    out_ds.FlushCache()

    del out_ds


def convert_allpred():
    file_path = r'D:\Desktop\prediction_after_war\home\dell\lzp\ReWrite\UKR_LUUnetpp-ukr'
    reference_path = r'D:\Homework\SecondTerm\farm\Dataset256_v2\gt'
    output_path = r'D:\Desktop\prediction_after_war\home\dell\lzp\ReWrite\UKR_LUUnetpp-ukr_1'
    Listfile, allFilename = file_name_tif(file_path)
    print("converting pred file to tif file with projection")
    with tqdm(total=len(allFilename)) as pbar:
        for i in range(len(allFilename)):
            file_id = allFilename[i]
            file_path = Listfile[i]
            reference_file_path = reference_path + '\\' + file_id + '.tif'
            data_prd = Read_tif(file_path)
            data_ref = Read_tif(reference_file_path)
            outputfile_path = output_path + '\\' + file_id + '.tif'

            convert_truevalue_255_1(data_prd, data_ref, outputfile_path, 256)
            pbar.update()


def get_shp_infos(shp_path):
    file = shapefile.Reader(shp_path)
    shapes = file.shapes()  # read all the features
    records = file.records()
    fields = file.fields
    return records, fields


def get_filelist_keywords(data_path, keywords):
    FileList, allFileid = file_name(data_path, suffix = 'shp')
    #keywords = ['after','upper']
    for keyword in keywords:
        FileList_keyword = []
        for file_path in FileList:
            if keyword in file_path:
                FileList_keyword.append(file_path)
        FileList = FileList_keyword
    return FileList


def file_name(file_dir, suffix):
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
                if file.split('.')[-1] != suffix:
                    continue
                formatName = os.path.splitext(file)[1]
                fileName = os.path.splitext(file)[0]
                allFilename.append(fileName)
                if (formatName == ('.' + suffix)):
                    tempPath = os.path.join(root, file)
                    L.append(tempPath)
        return L, allFilename
    else:
        print('must be folder path')


def main(data_path, keywords):
    beforewar_path = get_filelist_keywords(data_path, keywords=keywords)
    beforewar_file = beforewar_path[0]
    records, fields = get_shp_infos(beforewar_file)
    records = np.array(records)
    total_area = 0
    crop_area = 0
    for record in records:

        geoid = record[2]
        shape_area = record[4]
        total_area += shape_area
        if geoid > 0:
            crop_area += shape_area
    print("The crop Area of ", keywords , ":\n"
        ' Crop Area:', crop_area, '\n',
          'Total Area:', total_area, '\n',
          'Rate:  ', crop_area/total_area+1e-10)


if __name__ == '__main__':
    data_path = r'D:\PythonProjects\DataProcess\UkrineAnalysis'
    #keywords = ['beforewar'] # keywords[0]  should be 'beforewar' or 'afterwar'
    keywords_list = [
        ['beforewar'],['afterwar'],
        ['beforewar', 'bottom'],['afterwar', 'bottom'],
        ['beforewar', 'botsmall'],['afterwar', 'botsmall'],
        ['beforewar', 'upper'],['afterwar', 'upper'],
        ['beforewar', 'upsmall'], ['afterwar', 'upsmall']
    ]
    for keywords in keywords_list:
        main(data_path, keywords)