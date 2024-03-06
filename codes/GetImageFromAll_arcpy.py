# -*- coding: utf-8 -*-

"""
代码目的是从CBRA数据中快速返回自己需要的一个范围内的建筑物足迹数据
！！！索取数据范围不应超过2.5°！！！
使用本代码之前，需要自己生成一个索取范围的shp文件，WGS84投影
输入：list[[longitude1, latitude1], [longitude2, latitude2]]  #  左上角和右下角的经纬度坐标
输出：借助arcpy，直接得到裁剪之后的影像（索取范围的最小外包矩形区域内所有数据）
代码创建时间：2024.02.28
最后更新时间：2024.03.06
Lyu Siqing
"""

from tools import *
import numpy
import os
import arcpy


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


class CBRALocator:
    def __init__(self, file_root = '', rectangle_pos = None, year = 2018):
        self.root = file_root
        self.pos = rectangle_pos
        self.img_list = []  # 在不考虑切片临界情况时，此list只有一个路径

        # 以下参数，只对CBRA适用
        self.longitude_from = 73.5
        self.longitude_to = 136.0
        self.latitude_from = 16.3
        self.latitude_to = 53.8
        self.bin = 2.5
        self.year = year

        self.longitude_list = float_range(self.longitude_from, self.longitude_to, self.bin)
        self.latitude_list = float_range(self.latitude_from, self.latitude_to, self.bin)

    def get_pos(self):
        return self.pos

    def locate_image(self):
        self.locate_mode = None
        """
        定位所需要的image以及其对应的数据位置
        CBRA的经纬度范围起止：Longitude: 73.5 ~ 136.0 ; Latitude: 16.3 ~ 53.8
        left_top(CBRA_name)______________
        |                               |
        |       --> longitude -->       |
        |                               |
        |               ↑               |
        |            latitude           |
        |               ↑               |
        |                               |
        |                               |
        |                               |
        _____________________right_bottom
        :return:
        """
        left_top = self.pos[0]  # [longitude, latitude]
        right_bottom = self.pos[1]  # [longitude, latitude]
        assert (left_top[0] >= self.longitude_from) & (left_top[0] <= self.longitude_to)
        assert (right_bottom[1] >= self.latitude_from) & (right_bottom[1] <= self.latitude_to)

        # TODO: 进一步检查这种计算方式是否合理，尝试使用GDAL等地理库计算offset而不是数学方法,缝隙间可能存在误差

        latitude_index_lt = int((left_top[1] * 10 - self.latitude_from * 10) / (self.bin * 10)) + 1
        longitude_index_lt = int((left_top[0] * 10 - self.longitude_from * 10) / (self.bin * 10))
        latitude_index_rb = int((right_bottom[1] * 10 - self.latitude_from * 10) / (self.bin * 10)) + 1
        longitude_index_rb = int((right_bottom[0] * 10 - self.longitude_from * 10) / (self.bin * 10))

        CBRA_name = []
        # 左上角的对应图像是必然需要的
        CBRA_name_lat = self.latitude_list[latitude_index_lt]
        CBRA_name_lon = self.longitude_list[longitude_index_lt]
        CBRA_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                      'CBRA_{}_E{}_N{}.tif'.format(self.year, CBRA_name_lon, CBRA_name_lat)))

        # 接下来定位超过边界的其他图像
        if (latitude_index_rb != latitude_index_lt) | (longitude_index_rb != longitude_index_lt):
            # 只要不同，就找到四个角的对应位置，然后根据情况append进CBRA_name
            # 右上角对应的图像
            CBRA_name_lat_rt = self.latitude_list[latitude_index_lt]
            CBRA_name_lon_rt = self.longitude_list[longitude_index_lt + 1]
            # 右下角对应的图像
            CBRA_name_lat_rb = self.latitude_list[latitude_index_lt - 1]
            CBRA_name_lon_rb = self.longitude_list[longitude_index_lt + 1]
            # 左下角对应的图像
            CBRA_name_lat_lb = self.latitude_list[latitude_index_lt - 1]
            CBRA_name_lon_lb = self.longitude_list[longitude_index_lt]

            # 根据情况append
            if latitude_index_rb == latitude_index_lt:  # 右上角
                self.locate_mode = "RT"
                """
                ————————————|———————————>y(lon)
                |        ——-|-——        |
                |        |1 | 2|        |
                |        ——-|-——        |
                ————————————+———————————-
                |           |           |
                |           |           |
                ↓x(-lat)    |           |
                ————————————|———————————-
                """
                CBRA_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                              'CBRA_{}_E{}_N{}.tif'.format(self.year, CBRA_name_lon_rt, CBRA_name_lat_rt)))
                CBRA_name.append('')  # 3
                CBRA_name.append('')  # 4


            elif longitude_index_rb == longitude_index_lt:  # 左下角
                self.locate_mode = "LB"
                """
                ————————————|———————————>y(lon)
                |           |           |
                |   ——-——   |           |
                |   | 1 |   |           |
                ————————————+———————————-
                |   | 3 |   |           |
                |   ——-——   |           |
                ↓x(-lat)    |           |
                ————————————|———————————-
                """
                CBRA_name.append('')  # 2
                CBRA_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                              'CBRA_{}_E{}_N{}.tif'.format(self.year, CBRA_name_lon_lb, CBRA_name_lat_lb)))
                CBRA_name.append('')  # 4

            else:  # 右下角
                self.locate_mode = "RB"
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
                CBRA_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                              'CBRA_{}_E{}_N{}.tif'.format(self.year, CBRA_name_lon_rt, CBRA_name_lat_rt)))
                CBRA_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                              'CBRA_{}_E{}_N{}.tif'.format(self.year, CBRA_name_lon_lb, CBRA_name_lat_lb)))
                CBRA_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                              'CBRA_{}_E{}_N{}.tif'.format(self.year, CBRA_name_lon_rb, CBRA_name_lat_rb)))

        else:
            # 若索取范围在同一幅图内
            self.locate_mode = "Dome"
            """
            ————————————|————————————
            |    ——--—— |           |
            |    |    | |           |
            |    ——--—— |           |
            ————————————+———————————-
            |           |           |
            |           |           |
            |           |           |
            ————————————|———————————-
            """
            CBRA_name.append('')  # 2
            CBRA_name.append('')  # 3
            CBRA_name.append('')  # 4

        self.CBRA_names = CBRA_name
        return CBRA_name


if __name__ == '__main__':
    # Configs
    year = 2018  # 索取的数据年份
    root_path = r'G:\ProductData\CBRA'  # CBRA 数据存储位置，内包含2016-2021所有文件夹和影像
    save_path = r'G:\ProductData\CBRA\CBRA_clip'  # 裁剪得到的影像的保存位置
    save_name = "Beijing"  # 裁剪得到的影像系列的名称, 最终结果默认存在save_name0.tif中
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

    CBRA_locator = CBRALocator(root_path, rectangle_pos=[[Lon_min, Lat_max], [Lon_max, Lat_min]], year=year)
    CBRA_names = CBRALocator.locate_image(CBRA_locator)
    out_path = make_dir(os.path.join(save_path, str(year), save_name))

    print CBRA_names  # 对应区域裁剪时所需要的所有的CBRA影像
    print "================NOW CLIPPING================"
    for ii in range(len(CBRA_names)):
        CBRA_path = CBRA_names[ii]
        if len(CBRA_path) == 0:  # 如果对应的影像不存在
            continue
        out_raster = os.path.join(out_path, save_name+'{}.tif'.format(ii))
        if os.path.isfile(out_raster) is not True:  # 若已经有对应的影像，则跳过
            print "=======----processing: {}----=======".format(CBRA_path)
            arcpy.Clip_management(CBRA_path, in_template_dataset=in_temp, out_raster=out_raster,
                                  nodata_value=0, maintain_clipping_extent="MAINTAIN_EXTENT")

    #  获取所有的图像名称
    clipped_file_paths, clipped_file_names = file_name_tif(os.path.join(save_path, str(year)))
    inputs = ''
    for path in clipped_file_paths:
        inputs += path + ';'
    # print inputs[: -1], os.path.join(out_path, save_name+'0.tif')
    print "================NOW IN MOSAIC================"
    arcpy.Mosaic_management(inputs[: -1], os.path.join(out_path, save_name+'0.tif'), mosaic_type="MAXIMUM")
