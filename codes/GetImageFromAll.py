"""
代码目的是从CBRA数据中快速返回自己需要的一个范围内的建筑物足迹数据
本代码将分为两步进行：不考虑切片临界处数据和考虑切片临界处数据
索取数据范围不应超过2.5°
输入：list[[longitude1, latitude1], [longitude2, latitude2]]  #  左上角和右下角的经纬度坐标，保留至5位小数
输出：array  # 对应位置的足迹数据
代码创建时间：2024.02.28
最后更新时间：2024.02.28
Lyu Siqing
"""

import tifffile as tif
import os
import numpy as np
from geopy.distance import geodesic as gd
from CheckTheEmpty import CBRA_Checker


def float_range(start, stop, step):
    ''' 支持 float 的步进函数

        输入 Input:
            start (float)  : 计数从 start 开始。默认是从 0 开始。
            end   (float)  : 计数到 stop 结束，但不包括 stop。
            step (float)  : 步长，默认为 1，如为浮点数，参照 steps 小数位数。

        输出 Output:
            浮点数列表

        例子 Example:
            >>> print(float_range(3.612, 5.78, 0.22))
            [3.612, 3.832, 4.052, 4.272, 4.492, 4.712, 4.932, 5.152, 5.372]
    '''
    start_digit = len(str(start))-1-str(start).index(".") # 取开始参数小数位数
    stop_digit = len(str(stop))-1-str(stop).index(".")    # 取结束参数小数位数
    step_digit = len(str(step))-1-str(step).index(".")    # 取步进参数小数位数
    digit = max(start_digit, stop_digit, step_digit)      # 取小数位最大值
    return [(start*10**digit+i*step*10**digit)/10**digit for i in range(int((stop-start)//step))]  # 是否+1取决于是否要用范围上限那个数


class CBRALocator:
    def __init__(self, file_root: str = '', rectangle_pos: list = None, year:int = 2018):
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
        self.resolution = 2.5

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

        latitude_index_lt = int((left_top[1] - self.latitude_from) / self.bin)
        longitude_index_lt = int((left_top[0] - self.longitude_from) / self.bin)
        latitude_index_rb = int((right_bottom[1] - self.latitude_from) / self.bin)
        longitude_index_rb = int((right_bottom[0] - self.longitude_from) / self.bin)

        lat_size = gd(left_top, (left_top[0], right_bottom[1])).m  # 图像的纵向宽度
        lon_size = gd(right_bottom, (left_top[0], right_bottom[0])).m  # 图像的横向宽度， 以偏赤道的同一纬度为准

        CBRA_name = []
        img_pos = []
        # 左上角的对应图像是必然需要的
        CBRA_name_lat = self.latitude_list[latitude_index_lt]
        CBRA_name_lon = self.longitude_list[longitude_index_lt]
        CBRA_name.append(os.path.join(self.root, f'CBRA_{self.year}', f'CBRA_{self.year}_E{CBRA_name_lon}_N{CBRA_name_lat}.tif'))
        lon_distance = gd(left_top, (CBRA_name_lon, left_top[1])).m  # 计算CBRA左上角到索取范围左上角的横向距离
        lat_distance = gd(left_top, (left_top[0], CBRA_name_lat)).m  # 计算CBRA左上角到索取范围左上角的纵向距离
        lat_index_inside = int(np.floor(lat_distance / self.resolution))  # 换算成像素行列数
        lon_index_inside = int(np.floor(lon_distance / self.resolution))  # 换算成像素行列数

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
                CBRA_name.append(os.path.join(self.root, f'CBRA_{self.year}', f'CBRA_{self.year}_E{CBRA_name_lon_rt}_N{CBRA_name_lat_rt}.tif'))
                CBRA_name.append('') # 3
                CBRA_name.append('') # 4

                #  先计算留在左上角图像中的数据大小，再计算新的CBRA左上角到索取范围右上角的距离
                lon_distance_lt2mid = gd(left_top, (CBRA_name_lon_rt, left_top[1])).m  # 计算CBRA左上角到索取范围边界的横向距离
                lon_index_inside_lt2mid = int(np.floor(lon_distance_lt2mid / self.resolution))  # 换算成像素行列数

                image_pixels_y_lt = -1    # -1代表取到对应图像最大值，即取[lon_index_inside： ]
                image_pixels_x_lt = int(np.ceil(lat_size / self.resolution))
                img_pos.append([lat_index_inside, image_pixels_x_lt, lon_index_inside, image_pixels_y_lt])

                lat_index_inside_rt = lat_index_inside
                lon_index_inside_rt = 0
                image_pixels_y_rt = lon_size - lon_index_inside_lt2mid  # -1代表取到对应图像最大值，即取[lon_index_inside： ]
                image_pixels_x_rt = int(np.ceil(lat_size / self.resolution))
                img_pos.append([lat_index_inside_rt, image_pixels_x_rt, lon_index_inside_rt, image_pixels_y_rt])

                img_pos.append([])
                img_pos.append([])


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
                CBRA_name.append(os.path.join(self.root, f'CBRA_{self.year}', f'CBRA_{self.year}_E{CBRA_name_lon_lb}_N{CBRA_name_lat_lb}.tif'))
                CBRA_name.append('')  # 4

                #  先计算留在左上角图像中的数据大小，再计算新的CBRA左上角到索取范围左下角的距离
                lat_distance_lt2mid = gd(left_top, (left_top[0], CBRA_name_lat_lb)).m  # 计算CBRA左上角到索取范围边界的纵向距离
                lat_index_inside_lt2mid = int(np.floor(lat_distance_lt2mid / self.resolution))  # 换算成像素行列数

                image_pixels_y_lt = int(np.ceil(lon_size / self.resolution))
                image_pixels_x_lt = -1  # -1代表取到对应图像最大值，即取[lat_index_inside： ]
                img_pos.append([lat_index_inside, image_pixels_x_lt, lon_index_inside, image_pixels_y_lt])

                img_pos.append([])  # 2

                lat_index_inside_lb = 0
                lon_index_inside_lb = lon_index_inside
                image_pixels_y_lb = int(np.ceil(lon_size / self.resolution))
                image_pixels_x_lb = lat_size - lat_index_inside_lt2mid
                img_pos.append([lat_index_inside_lb, image_pixels_x_lb, lon_index_inside_lb, image_pixels_y_lb])

                img_pos.append([])  # 4

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
                CBRA_name.append(os.path.join(self.root, f'CBRA_{self.year}', f'CBRA_{self.year}_E{CBRA_name_lon_rt}_N{CBRA_name_lat_rt}.tif'))
                CBRA_name.append(os.path.join(self.root, f'CBRA_{self.year}', f'CBRA_{self.year}_E{CBRA_name_lon_lb}_N{CBRA_name_lat_lb}.tif'))
                CBRA_name.append(os.path.join(self.root, f'CBRA_{self.year}', f'CBRA_{self.year}_E{CBRA_name_lon_rb}_N{CBRA_name_lat_rb}.tif'))

                #  先计算留在左上角图像中的数据大小
                lon_distance_lt2mid = gd(left_top, (CBRA_name_lon_rt, left_top[1])).m  # 计算CBRA左上角到索取范围边界的横向距离
                lon_index_inside_lt2mid = int(np.floor(lon_distance_lt2mid / self.resolution))  # 换算成像素行列数
                lat_distance_lt2mid = gd(left_top, (left_top[0], CBRA_name_lat_lb)).m  # 计算CBRA左上角到索取范围边界的纵向距离
                lat_index_inside_lt2mid = int(np.floor(lat_distance_lt2mid / self.resolution))  # 换算成像素行列数

                image_pixels_y_lt = -1  # -1代表取到对应图像最大值，即取[lon_index_inside： ]
                image_pixels_x_lt = -1  # -1代表取到对应图像最大值，即取[lat_index_inside： ]
                img_pos.append([lat_index_inside, image_pixels_x_lt, lon_index_inside, image_pixels_y_lt])

                #  右上角
                lat_index_inside_rt = lat_index_inside
                lon_index_inside_rt = 0
                image_pixels_y_rt = lon_size - lon_index_inside_lt2mid
                image_pixels_x_rt = -1  # -1代表取到对应图像最大值，即取[lat_index_inside： ]
                img_pos.append([lat_index_inside_rt, image_pixels_x_rt, lon_index_inside_rt, image_pixels_y_rt])

                #  左下角
                lat_index_inside_lb = 0
                lon_index_inside_lb = lon_index_inside
                image_pixels_y_lb = -1  # -1代表取到对应图像最大值，即取[lon_index_inside： ]
                image_pixels_x_lb = lat_size - lat_index_inside_lt2mid
                img_pos.append([lat_index_inside_lb, image_pixels_x_lb, lon_index_inside_lb, image_pixels_y_lb])

                #  右下角
                lat_index_inside_rb = 0
                lon_index_inside_rb = 0
                image_pixels_y_rb = lon_size - lon_index_inside_lt2mid
                image_pixels_x_rb = lat_size - lat_index_inside_lt2mid
                img_pos.append([lat_index_inside_rb, image_pixels_x_rb, lon_index_inside_rb, image_pixels_y_rb])

        else:  # 若索取范围在同一幅图内
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
            # python读取图像为array导致纬度代表x轴位置、经度代表y轴位置
            image_pixels_y = int(np.ceil(lon_size / self.resolution))
            image_pixels_x = int(np.ceil(lat_size / self.resolution))

            img_pos.append([lat_index_inside, image_pixels_x, lon_index_inside, image_pixels_y])
            img_pos.append([])  # 2
            img_pos.append([])  # 3
            img_pos.append([])  # 4

        # CBRA_data = tif.imread(CBRA_name)
        # img_data = CBRA_data[lat_index_inside:lat_index_inside+image_pixels_x, lon_index_inside:lon_index_inside+image_pixels_y]
        self.CBRA_names = CBRA_name
        self.img_pos = img_pos
        self.lat_size = lat_size
        self.lon_size = lon_size
        return CBRA_name, img_pos

    def get_img_data(self):
        # TODO: 根据提供的影像名称以及坐标位置得到对应的数据
        CBRA_names = self.CBRA_names
        img_pos = self.img_pos
        img_data = np.zeros((self.lat_size, self.lon_size))

        if self.locate_mode == 'Dome':
            CBRA_data = tif.imread(CBRA_names[0])
            lat_index_inside, image_pixels_x, lon_index_inside, image_pixels_y = img_pos[0]
            img_data = CBRA_data[lat_index_inside:lat_index_inside+image_pixels_x, lon_index_inside:lon_index_inside+image_pixels_y]

        if self.locate_mode == 'RT':
            CBRA_data = tif.imread(CBRA_names[0])
            lat_size_CBRA, lon_size_CBRA = CBRA_data.shape
            lat_index_inside, image_pixels_x, lon_index_inside, _ = img_pos[0]
            img_data[0:image_pixels_x, 0:(lon_size_CBRA - lon_index_inside)]\
                = CBRA_data[lat_index_inside: lat_index_inside+image_pixels_x, lon_index_inside:]

            CBRA_data = tif.imread(CBRA_names[1])
            lat_index_inside, image_pixels_x, _, image_pixels_y = img_pos[1]
            img_data[0:image_pixels_x, (lon_size_CBRA - lon_index_inside):] \
                = CBRA_data[lat_index_inside:lat_index_inside + image_pixels_x, 0: image_pixels_y]

        if self.locate_mode == 'LB':
            CBRA_data = tif.imread(CBRA_names[0])
            lat_size_CBRA, lon_size_CBRA = CBRA_data.shape
            lat_index_inside, _, lon_index_inside, image_pixels_y = img_pos[0]
            img_data[0:(lat_size_CBRA - lat_index_inside), 0:image_pixels_y] \
                = CBRA_data[lat_index_inside: , lon_index_inside: lon_index_inside + image_pixels_y]

            CBRA_data = tif.imread(CBRA_names[2])
            _, image_pixels_x, lon_index_inside, image_pixels_y = img_pos[2]
            img_data[(lat_size_CBRA - lat_index_inside):, 0:image_pixels_y] \
                = CBRA_data[0: image_pixels_x, lon_index_inside: lon_index_inside + image_pixels_y]

        if self.locate_mode == 'RB':
            CBRA_data = tif.imread(CBRA_names[0])
            lat_size_CBRA, lon_size_CBRA = CBRA_data.shape
            lat_index_inside, _, lon_index_inside, _ = img_pos[0]
            img_data[0:(lat_size_CBRA - lat_index_inside), 0:(lon_size_CBRA - lon_index_inside)] \
                = CBRA_data[lat_index_inside:, lon_index_inside:]

            CBRA_data = tif.imread(CBRA_names[1])
            lat_index_inside, _, _, image_pixels_y = img_pos[1]
            img_data[0:(lat_size_CBRA - lat_index_inside), (lon_size_CBRA - lon_index_inside):] \
                = CBRA_data[lat_index_inside:, 0: image_pixels_y]

            CBRA_data = tif.imread(CBRA_names[2])
            _, image_pixels_x, lon_index_inside, _ = img_pos[2]
            img_data[(lat_size_CBRA - lat_index_inside):, 0:(lon_size_CBRA - lon_index_inside)] \
                = CBRA_data[0: image_pixels_x, lon_index_inside:]

            CBRA_data = tif.imread(CBRA_names[3])
            _, image_pixels_x, _, image_pixels_y = img_pos[3]
            img_data[(lat_size_CBRA - lat_index_inside):, (lon_size_CBRA - lon_index_inside):] \
                = CBRA_data[0: image_pixels_x, 0: image_pixels_y]