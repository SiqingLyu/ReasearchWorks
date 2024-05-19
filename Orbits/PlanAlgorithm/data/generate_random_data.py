import pandas as pd
import numpy as np
import random
from GetProblemsConditions import SatellitePosition
from get_TLEs import *
import datetime as dt
from shapely.geometry import Point, Polygon, LineString
import math
import matplotlib.pyplot as plt


satellite_names = ["GAOFEN", "TIANHUI", "JILIN", "SUPERVIEW"]
json_file = r'./satellite_list.json'


def random_data(**kwargs):
    target_infos, satellite_infos = random_raw_data(**kwargs)
    windows_infos = get_windows_K(target_infos, satellite_infos)

    return


def get_windows_K(target_infos, satellites: dict = None):
    windows_K = {}
    target_J = {}

    for sate_name in satellites.keys():
        if sate_name == "label":
            continue

        sate_info = satellites[sate_name]
        positions = sate_info[0]
        width = sate_info[1]

        if sate_name not in windows_K.keys():
            windows_K[sate_name] = {}
        if sate_name not in target_J.keys():
            target_J[sate_name] = {}

        for ii in range(1, len(positions)):
            pre_pos = positions[ii - 1]
            cur_pos = positions[ii]
            buffer = generate_polygon_by_two_points([pre_pos, cur_pos], width)

            for tar_name in target_infos.keys():
                if tar_name == "label":
                    continue

                tar_info = target_infos[tar_name]
                tar_pos = Point(tar_info[1])

                if tar_name not in windows_K[sate_name].keys():
                    windows_K[sate_name][tar_name] = 0

                if buffer.contains(tar_pos):
                    windows_K[sate_name][tar_name] += 1
                    if tar_name in target_J[sate_name].keys():
                        pass
                    else:
                        target_J[sate_name][tar_name] = len(target_J[sate_name].keys())

    return windows_K, target_J


def generate_polygon_by_two_points(points, width):
    """
    为一段线段生成一个垂直于它的矩形，用于计算卫星j在任务i上的时间窗口
    此处并未考虑球面投影
    :param points: 两个时间点上卫星的星下点位置
    :param width: 卫星的幅宽
    :return:
    """
    point1, point2 = points
    line = LineString([point1, point2])
    polygon = line.buffer((width/2))
    # x1, y1 = line.xy
    # x2, y2 = polygon.boundary.xy
    # plt.figure()
    # plt.plot(x1, y1)
    # plt.plot(x2, y2)
    # plt.show()
    # inside = polygon.contains(Point(0, 0.5))
    # print(inside)
    return polygon


def update_tle_list():
    update_tles(satellite_names, json_file)


def random_raw_data(target_num: int = 500, satellite_num: int = 10, interval: int = 1, period: int = 24):
    """
    这个函数生成随机的卫星和任务，返回为字典类型，随机产生的卫星是由json_file中的信息打乱选取的
    :param target_num: 任务数量
    :param satellite_num: 卫星数量
    :param time_window:  默认切分的时间窗口长短
    :param period:  任务规划时长
    :return: target_infos: [优先级（int）, 位置（[lon, lat]）]
            satellite_infos: ["track positions", "width", "angle", "angle_speed_per_second", "minute_in_single_round",
                                "mb_per_second", "max_space", "max_energy", "energy_sway_per_second", "energy_image_per_second"]
    """
    update_tle_list()
    target_infos, satellite_infos = {}, {}
    satellite_infos["label"] = ["track positions", "width", "angle", "angle_speed_per_second", "minute_in_single_round",
                                "mb_per_second", "max_space", "max_energy", "energy_sway_per_second", "energy_image_per_second",
                                "max_image_time"]
    target_infos["label"] = ["priority", "position"]

    start_dt = dt.datetime.today()
    with open(json_file, 'r') as tle_file:
        tle_data = json.load(tle_file)
        assert satellite_num <= len(tle_data), "没有这么多数量的卫星可供选择"

        random_index = np.random.permutation(len(tle_data))
        random_index = np.array(random_index, dtype='int32')

        for ii in range(target_num):
            name = f"JOB{ii}"
            priority = random.randint(1, 10)
            position = [random.random()*360-180, random.random()*180-90]
            target_infos[name] = [priority, position]
        for ii in range(satellite_num):
            sate_tle = tle_data[random_index[ii]]
            sate_name = sate_tle["satellite_name"]
            SP = SatellitePosition(sate_tle)
            SP.set_from_to(start_dt, start_dt + dt.timedelta(hours=period))

            sate_poses = SP.get_tracks(interval=interval)           # °
            sate_width = random.randint(10, 200)                    # km
            sate_angle = random.randint(0, 30)                      # °
            sate_angle_speed_per_second = random.randint(1, 10)     # second
            sate_minute_in_single_round = random.randint(10, 720)   # minute
            sate_mb_per_second = random.randint(1, 100)             # mb
            sate_max_space = random.randint(1024 * 8, 1024*512)     # mb
            sate_max_energy = random.randint(10, 100)               # kw*h
            sate_energy_sway_per_second = random.random()*0.02      # kw*h
            sate_energy_image_per_second = random.random()*0.5      # kw*h
            sate_max_image_time = random.randint(30, 600)           # second

            satellite_infos[sate_name] = [sate_poses, sate_width, sate_angle, sate_angle_speed_per_second,
                                          sate_minute_in_single_round, sate_mb_per_second, sate_max_space,
                                          sate_max_energy, sate_energy_sway_per_second, sate_energy_image_per_second]

    return target_infos, satellite_infos


if __name__ == '__main__':
    generate_polygon_by_two_points([[0, 1], [1, 2]], 1)
