# -*- coding: utf-8 -*-

"""
代码目的是从已下载的河北数据中快速返回自己需要的一个范围内的建筑物足迹数据
！！！     索取数据范围不应超过1°     ！！！
使用本代码之前，需要自己生成一个索取范围的shp文件，WGS84投影
输入：list[[longitude1, latitude1], [longitude2, latitude2]]  #  左上角和右下角的经纬度坐标
输出：借助arcpy，直接得到裁剪之后的影像（索取范围的最小外包矩形区域内所有数据）
代码创建时间：2024.03.08
最后更新时间：2024.03.08
Lyu Siqing
"""

from tools import *
import numpy as np
import os
import arcpy

seasons = ['all', 'spring', 'summer', 'autumn', 'winter']


def path_seasons_append(paths, root, lon, lat):
    for i in range(len(paths)):
        file_pathroot = os.path.join(root, '{}'.format(seasons[i]), '{}_{}'.format(lon, lat))
        file_paths, file_names = file_name_tif(file_pathroot)
        paths[i] = paths[i] + file_paths
    return paths


def float_range(start, stop, step):
    ''' 支持 float 的步进函数

        输入 Input:
            start (float)  : 计数从 start 开始。默认是从 0 开始。
            end   (float)  : 计数到 stop 结束，但不包括 stop。
            step (float)  : 步长，默认为 1，如为浮点数，参照 steps 小数位数。

        输出 Output:
            浮点数列表

        例子 Example:
            # >>> print(float_range(3.612, 5.78, 0.22))
            [3.612, 3.832, 4.052, 4.272, 4.492, 4.712, 4.932, 5.152, 5.372]
    '''
    start_digit = len(str(start))-1-str(start).index(".")  # 取开始参数小数位数
    stop_digit = len(str(stop))-1-str(stop).index(".")    # 取结束参数小数位数
    step_digit = len(str(step))-1-str(step).index(".")    # 取步进参数小数位数
    digit = max(start_digit, stop_digit, step_digit)      # 取小数位最大值
    return [(start*10**digit+i*step*10**digit)/10**digit for i in range(int((stop-start)//step))]  # 是否+1取决于是否要用范围上限那个数


class S2Locator:
    def __init__(self, file_root = '', rectangle_pos = None):
        self.root = file_root
        self.pos = rectangle_pos
        self.img_list = []  # 在不考虑切片临界情况时，此list只有一个路径

        # 以下参数，只对河北数据适用
        self.longitude_from = 114.0
        self.longitude_to = 120.0
        self.latitude_from = 36.0
        self.latitude_to = 42.0
        self.bin = 1.0

        self.longitude_list = float_range(self.longitude_from, self.longitude_to, self.bin)
        self.latitude_list = float_range(self.latitude_from, self.latitude_to, self.bin)

    def get_pos(self):
        return self.pos

    def locate_image(self):
        self.locate_mode = None
        """
        定位所需要的image以及其对应的数据位置
        河北的经纬度范围起止：Longitude: 114.0 ~ 120.0 ; Latitude: 36.0 ~ 42.0
        _________________________right_top
        |                               |
        |       --> longitude -->       |
        |                               |
        |               ↑               |
        |            latitude           |
        |               ↑               |
        |                               |
        |                               |
        |                               |
        left_bottom(S2_name)____________|
        """
        left_bottom = self.pos[0]  # [longitude, latitude]
        right_top = self.pos[1]  # [longitude, latitude]
        assert (left_bottom[0] >= self.longitude_from) & (left_bottom[0] <= self.longitude_to)
        assert (left_bottom[1] >= self.latitude_from) & (left_bottom[1] <= self.latitude_to)

        latitude_index_lb = int((left_bottom[1] * 10 - self.latitude_from * 10) / (self.bin * 10))
        longitude_index_lb = int((left_bottom[0] * 10 - self.longitude_from * 10) / (self.bin * 10))
        latitude_index_rt = int((right_top[1] * 10 - self.latitude_from * 10) / (self.bin * 10))
        longitude_index_rt = int((right_top[0] * 10 - self.longitude_from * 10) / (self.bin * 10))

        S2_paths = [[]] * 5  # [[all], [spring], [summer], [autumn], [winter]]

        """
        ————————————|———————————>y(lon)
        |           |           |
        |        ——-|-——        |
        |        | 1|2 |        |
        —————————|——+——|————————-
        |        | 3|4 |        |
        |        ——-|-——        |
        |           |           |
        ↓x(-lat)    |           |
        ————————————|———————————-
        """
        lon_diff = longitude_index_rt - longitude_index_lb
        lon_bin_num = int(np.ceil(lon_diff / self.bin))
        lat_diff = latitude_index_rt - latitude_index_lb
        lat_bin_num = int(np.ceil(lat_diff / self.bin))
        for ii in range(0, lon_bin_num + 1):
            for jj in range(0, lat_bin_num + 1):
                lon_tmp = self.longitude_list[longitude_index_lb + ii]
                lat_tmp = self.latitude_list[latitude_index_lb + jj]
                S2_paths = path_seasons_append(S2_paths, self.root, int(lon_tmp), int(lat_tmp))

        self.S2_paths = S2_paths
        return S2_paths


if __name__ == '__main__':
    # Configs
    root_path = r'F:\Data\Sentinel-2\China\Hebei'  # S2 数据存储位置，内包含2016-2021所有文件夹和影像
    save_path = r'F:\Data\Sentinel-2\China\ROI_clip'  # 裁剪得到的影像的保存位置
    save_name = "Hebei"  # 裁剪得到的影像系列的名称, 最终结果默认存在 save_name0.tif 中
    in_temp = r'D:\Desktop\ZepingData\ROI\Beijing.shp'  # 对应要裁剪的范围的shp文件

    desc = arcpy.Describe(in_temp)
    # 获取 shp 文件的边界范围
    extent = desc.extent

    Lon_min, Lon_max, Lat_min, Lat_max = extent.XMin, extent.XMax, extent.YMin, extent.YMax
    # 输出经纬度范围信息
    print("Min Lon :", extent.XMin)
    print("Max Lat :", extent.YMax)
    print("Min Lat :", extent.YMin)
    print("Max Lon :", extent.XMax)

    S2_locator = S2Locator(root_path, rectangle_pos=[[Lon_min, Lat_min], [Lon_max, Lat_max]])
    S2_paths = S2_locator.locate_image()
    # print S2_paths[0]

    # S2_locator = S2Locator(root_path, rectangle_pos=[[Lon_min, Lat_max], [Lon_max, Lat_min]])
    # S2_names = S2Locator.locate_image(S2_locator)
    out_path = make_dir(os.path.join(save_path, save_name))

    print S2_paths  # 对应区域裁剪时所需要的所有的S2影像
    print "================NOW CLIPPING================"
    for S2_path in S2_paths:
        for ii in range(len(S2_path)):
            file_path = S2_path[ii]
            if len(S2_path) == 0:  # 如果对应的影像不存在
                continue
            out_raster = os.path.join(out_path, save_name+'{}.tif'.format(ii))
            if os.path.isfile(out_raster) is not True:  # 若已经有对应的影像，则跳过
                print "=======----processing: {}----=======".format(file_path)
                arcpy.Clip_management(file_path, in_template_dataset=in_temp, out_raster=out_raster,
                                      nodata_value=0, maintain_clipping_extent="MAINTAIN_EXTENT")

    #  获取所有的图像名称
    clipped_file_paths, clipped_file_names = file_name_tif(os.path.join(save_path, str()))
    inputs = ''
    for path in clipped_file_paths:
        inputs += path + ';'
    # print inputs[: -1], os.path.join(out_path, save_name+'0.tif')
    print "================NOW IN MOSAIC================"
    arcpy.Mosaic_management(inputs[: -1], os.path.join(out_path, save_name+'0.tif'), mosaic_type="MAXIMUM")