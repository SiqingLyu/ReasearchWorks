import numpy as np
import ephem
import datetime as dt
from fastkml import kml
from shapely.geometry import Point, LineString, Polygon
import json
import os


def make_dir(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)
    return path


def tle_kml(name: str = None, line1: str = None, line2: str = None,
            start_dt=None, end_dt=None, save_file=r'test.kml'):
    """
    将TLE文件根据日期区间转换为KML文件
    :param name: TLE文件中的卫星名称
    :param line1: TLE文件中的第一行
    :param line2: TLE文件中的第二行
    :param start_dt: 卫星轨迹计算开始时间
    :param end_dt: 卫星轨迹计算结束时间
    :param save_file:  KML文件保存位置
    """
    tle_rec = ephem.readtle(name, line1, line2)

    date_gap = end_dt - start_dt
    minutes_total = int(date_gap.total_seconds() / 60)  # get total minutes

    interval = dt.timedelta(minutes=1)  # use 1 minute as the interval

    timelist = []
    for i in range(minutes_total):
        timelist.append(start_dt + i * interval)

    positions = []
    for t in timelist:
        tle_rec.compute(t)
        positions.append((tle_rec.sublong / ephem.degree,
                          tle_rec.sublat / ephem.degree,
                          tle_rec.elevation))

    k = kml.KML()
    ns = '{http://www.opengis.net/kml/2.2}'
    p = kml.Placemark(ns, 'Sattrack', f'{name}', f'Time: From {start_dt} to {end_dt}')
    p.geometry = LineString(positions)
    k.append(p)

    with open(os.path.join(save_file, f"{name.replace(' ', '')}.kml"), 'w') as kmlfile:
        kmlfile.write(k.to_string())


def tle_kmls(json_file, start_date, last_days, kml_root):
    with open(json_file, 'r') as tle_file:
        tle_data = json.load(tle_file)
        start_dt = dt.datetime(start_date[0], start_date[1], start_date[2], start_date[3])  # 日期，list格式，到小时
        for day_num in last_days:
            end_dt = start_dt + dt.timedelta(days=day_num)
            kml_save_path = make_dir(os.path.join(kml_root, f"{start_dt.date()}_{end_dt.date()}"))
            for tle in tle_data:
                sat_name = tle['satellite_name']
                line1 = tle['tle_1']
                line2 = tle['tle_2']
                tle_kml(name=sat_name, line1=line1, line2=line2, start_dt=start_dt, end_dt=end_dt,
                        save_file=kml_save_path)