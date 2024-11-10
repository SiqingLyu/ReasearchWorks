# -*- coding: utf-8 -*-
import os
import shutil
import traceback


def move_file(src_path, dst_path, file):
    print('from : ', src_path)
    print('to : ', dst_path)
    try:
        # cmd = 'chmod -R +x ' + src_path
        # os.popen(cmd)
        f_src = os.path.join(src_path, file)
        if not os.path.exists(dst_path):
            os.mkdir(dst_path)
        f_dst = os.path.join(dst_path, file)
        shutil.move(f_src, f_dst)
    except Exception as e:
        print('move_file ERROR: ', e)
        traceback.print_exc()


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
    start_digit = len(str(start)) - 1 - str(start).index(".")  # 取开始参数小数位数
    stop_digit = len(str(stop)) - 1 - str(stop).index(".")  # 取结束参数小数位数
    step_digit = len(str(step)) - 1 - str(step).index(".")  # 取步进参数小数位数
    digit = max(start_digit, stop_digit, step_digit)  # 取小数位最大值
    return [(start * 10 ** digit + i * step * 10 ** digit) / 10 ** digit for i in
            range(int((stop - start) // step))]  # 是否+1取决于是否要用范围上限那个数


class CBRALocator:
    def __init__(self, file_root='', rectangle_pos=None, year=2018):
        self.root = file_root
        self.pos = rectangle_pos
        self.img_list = []  # 在不考虑切片临界情况时，此list只有一个路径

        # 以下参数，只对CBRA适用
        self.longitude_from = 73.5
        self.longitude_to = 136.0 + 5
        self.latitude_from = 16.3
        self.latitude_to = 53.8 + 5
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
        left_top(image_name)______________
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
        print(left_top[0])
        assert (left_top[0] >= self.longitude_from) & (left_top[0] <= self.longitude_to)
        assert (right_bottom[1] >= self.latitude_from) & (right_bottom[1] <= self.latitude_to)

        # TODO: 进一步检查这种计算方式是否合理，尝试使用GDAL等地理库计算offset而不是数学方法,缝隙间可能存在误差

        latitude_index_lt = int((left_top[1] * 10 - self.latitude_from * 10) / (self.bin * 10)) + 1
        longitude_index_lt = int((left_top[0] * 10 - self.longitude_from * 10) / (self.bin * 10))
        latitude_index_rb = int((right_bottom[1] * 10 - self.latitude_from * 10) / (self.bin * 10)) + 1
        longitude_index_rb = int((right_bottom[0] * 10 - self.longitude_from * 10) / (self.bin * 10))

        image_name = []
        # 左上角的对应图像是必然需要的
        print(latitude_index_lt, self.latitude_list[-1], len(self.latitude_list))
        image_name_lat = self.latitude_list[latitude_index_lt]
        image_name_lon = self.longitude_list[longitude_index_lt]
        image_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                       'CBRA_{}_E{}_N{}.tif'.format(self.year, image_name_lon, image_name_lat)))

        # 接下来定位超过边界的其他图像
        if (latitude_index_rb != latitude_index_lt) | (longitude_index_rb != longitude_index_lt):
            # 只要不同，就找到四个角的对应位置，然后根据情况append进image_name
            # 右上角对应的图像
            image_name_lat_rt = self.latitude_list[latitude_index_lt]
            image_name_lon_rt = self.longitude_list[longitude_index_lt + 1]
            # 右下角对应的图像
            image_name_lat_rb = self.latitude_list[latitude_index_lt - 1]
            image_name_lon_rb = self.longitude_list[longitude_index_lt + 1]
            # 左下角对应的图像
            image_name_lat_lb = self.latitude_list[latitude_index_lt - 1]
            image_name_lon_lb = self.longitude_list[longitude_index_lt]

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
                image_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                               'CBRA_{}_E{}_N{}.tif'.format(self.year, image_name_lon_rt,
                                                                            image_name_lat_rt)))
                image_name.append('')  # 3
                image_name.append('')  # 4


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
                image_name.append('')  # 2
                image_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                               'CBRA_{}_E{}_N{}.tif'.format(self.year, image_name_lon_lb,
                                                                            image_name_lat_lb)))
                image_name.append('')  # 4

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
                image_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                               'CBRA_{}_E{}_N{}.tif'.format(self.year, image_name_lon_rt,
                                                                            image_name_lat_rt)))
                image_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                               'CBRA_{}_E{}_N{}.tif'.format(self.year, image_name_lon_lb,
                                                                            image_name_lat_lb)))
                image_name.append(os.path.join(self.root, 'CBRA_{}'.format(self.year),
                                               'CBRA_{}_E{}_N{}.tif'.format(self.year, image_name_lon_rb,
                                                                            image_name_lat_rb)))

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
            image_name.append('')  # 2
            image_name.append('')  # 3
            image_name.append('')  # 4

        self.image_names = image_name
        return image_name


class CNBHLocator:
    def __init__(self, file_root='', rectangle_pos=None):
        self.root = file_root
        self.pos = rectangle_pos
        self.img_list = []  # 在不考虑切片临界情况时，此list只有一个路径

        # 以下参数，只对CBRA适用
        self.longitude_from = 72.0
        self.longitude_to = 140.0
        self.latitude_from = 16.0
        self.latitude_to = 58.0
        self.bin = 2.0
        self.margin = 1.0

        self.longitude_list = float_range(self.longitude_from, self.longitude_to, self.bin)
        self.latitude_list = float_range(self.latitude_from, self.latitude_to, self.bin)
        # self.pos = self.get_pos()

    # def get_pos(self):
    #     center_lon, center_lat = self.center
    #     left_top = [center_lon - self.margin, center_lat + self.margin]
    #     right_bottom = [center_lon + self.margin, center_lat - self.margin]
    #     pos = [left_top, right_bottom]
    #     return pos

    def locate_image(self):
        self.locate_mode = None
        """
        定位所需要的image以及其对应的数据位置
        left_top________________________
        |                               |
        |       --> longitude -->       |
        |                               |
        |               ↓               |
        |      Center(image_name)       |
        |               ↑               |
        |                               |
        |                               |
        |                               |
        _____________________right_bottom
        :return:
        """

        left_top = self.pos[0]  # [longitude, latitude]
        right_bottom = self.pos[1]  # [longitude, latitude]
        print(left_top[0])
        assert (left_top[0] >= self.longitude_from) & (left_top[0] <= self.longitude_to)
        assert (right_bottom[1] >= self.latitude_from) & (right_bottom[1] <= self.latitude_to)

        # TODO: 进一步检查这种计算方式是否合理，尝试使用GDAL等地理库计算offset而不是数学方法,缝隙间可能存在误差

        latitude_index_lt = int((left_top[1] * 10 - self.latitude_from * 10) / (self.bin * 10)) + 1
        longitude_index_lt = int((left_top[0] * 10 - self.longitude_from * 10) / (self.bin * 10))
        latitude_index_rb = int((right_bottom[1] * 10 - self.latitude_from * 10) / (self.bin * 10)) + 1
        longitude_index_rb = int((right_bottom[0] * 10 - self.longitude_from * 10) / (self.bin * 10))

        image_name = []
        # 左上角的对应图像是必然需要的
        print(latitude_index_lt, self.latitude_list[-1], len(self.latitude_list))
        image_name_lat_center = self.latitude_list[latitude_index_lt] - self.margin
        image_name_lon_center = self.longitude_list[longitude_index_lt] + self.margin
        image_name.append(os.path.join(self.root,
                                       'CNBH10m_X{}Y{}.tif'.format(int(image_name_lon_center),
                                                                   int(image_name_lat_center))))

        # 接下来定位超过边界的其他图像
        if (latitude_index_rb != latitude_index_lt) | (longitude_index_rb != longitude_index_lt):
            # 只要不同，就找到四个角的对应位置，然后根据情况append进image_name
            # 右上角对应的图像
            image_name_lat_rt = self.latitude_list[latitude_index_lt]
            image_name_lon_rt = self.longitude_list[longitude_index_lt + 1]
            # 右下角对应的图像
            image_name_lat_rb = self.latitude_list[latitude_index_lt - 1]
            image_name_lon_rb = self.longitude_list[longitude_index_lt + 1]
            # 左下角对应的图像
            image_name_lat_lb = self.latitude_list[latitude_index_lt - 1]
            image_name_lon_lb = self.longitude_list[longitude_index_lt]

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
                image_name.append(os.path.join(self.root,
                                               'CNBH10m_X{}Y{}.tif'.format(int(image_name_lon_rt + self.margin),
                                                                           int(image_name_lat_rt - self.margin))))
                # image_name.append(os.path.join(self.root,
                #                               'CBRA_{}_E{}_N{}.tif'.format(image_name_lon_rt, image_name_lat_rt)))
                image_name.append('')  # 3
                image_name.append('')  # 4


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
                image_name.append('')  # 2

                image_name.append(os.path.join(self.root,
                                               'CNBH10m_X{}Y{}.tif'.format(int(image_name_lon_lb + self.margin),
                                                                           int(image_name_lat_lb - self.margin))))
                image_name.append('')  # 4

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
                image_name.append(os.path.join(self.root,
                                               'CNBH10m_X{}Y{}.tif'.format(int(image_name_lon_rt + self.margin),
                                                                           int(image_name_lat_rt - self.margin))))
                image_name.append(os.path.join(self.root,
                                               'CNBH10m_X{}Y{}.tif'.format(int(image_name_lon_lb + self.margin),
                                                                           int(image_name_lat_lb - self.margin))))
                image_name.append(os.path.join(self.root,
                                               'CNBH10m_X{}Y{}.tif'.format(int(image_name_lon_rb + self.margin),
                                                                           int(image_name_lat_rb - self.margin))))

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
            image_name.append('')  # 2
            image_name.append('')  # 3
            image_name.append('')  # 4

        self.image_names = image_name
        return image_name
