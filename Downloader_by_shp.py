# coding:utf-8

import argparse
import json
import csv
import math
import time
from multiprocessing.dummy import Pool, Lock
import os
import datetime as DATETIME
import random
import geemap
# datetime.strptime(str(a),"%Y%m%d")
import warnings
from tools import *
import tifffile as tif

warnings.simplefilter('ignore', UserWarning)
import ee
import numpy as np
import urllib3
from http.client import IncompleteRead as http_incompleteRead
from urllib3.exceptions import IncompleteRead as urllib3_incompleteRead
import httplib2

dates = [2016,
         2017,
         2018,
         2019,
         2020,
         2021,
         2022,
         2023,
         2024]

SEASON_DATE_RANGE = {
    'spring': [90, 120],
    'summer': [180, 210],
    'autumn': [270, 300],
    'winter': [0, 30],
    'all': [0, 360]
}


def get_period(year):
    time_0 = DATETIME.date(year, 1, 1)
    time_1 = DATETIME.date(year, 12, 30)
    return [time_0.isoformat(), time_1.isoformat()]


def maskS2clouds(image):
    qa = image.select('QA60')

    # Bits 10 and 11 are clouds and cirrus, respectively.
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11

    # Both flags should be set to zero, indicating clear conditions.
    mask = qa.bitwiseAnd(cloudBitMask).eq(0)
    mask = mask.bitwiseAnd(cirrusBitMask).eq(0)
    return image.updateMask(mask).divide(10000)


def tif_file_check(file_path):
    data = tif.imread(file_path)
    data_pixels = data.shape[0] * data.shape[1]
    nodata_pixels = len(data[data <= NODATA])
    if nodata_pixels / data_pixels > 0.2:
        return 'too much nodata'
    elif nodata_pixels / data_pixels > 0.1:
        return 'much nodata'
    else:
        return 'acceptable'


class GEEDownloader:
    def __init__(self, cloud_pct: int = 20, save_name=''):
        self.cloud_pct = cloud_pct
        self.save_name = save_name

    def download_seasonal_s2(self, region, year, period_buffer=0, season='spring'):
        # period = get_period(year)
        print("processing ", season)
        from_date = SEASON_DATE_RANGE[season][0] - period_buffer if (SEASON_DATE_RANGE[season][
                                                                         0] - period_buffer) >= 0 else 0
        to_date = SEASON_DATE_RANGE[season][1] + period_buffer if (SEASON_DATE_RANGE[season][
                                                                       1] + period_buffer) <= 360 else 360
        print(f"At period {year}  From {from_date} To {to_date}")
        if len(YEAR) > 1:
            s2_collection = (
                ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
                # .filterDate(f'{year[0]}-1-1', f'{year[1]}-12-31')
                .filter(ee.Filter.calendarRange(year[0], year[1], 'year'))
                .filter(ee.Filter.calendarRange(from_date, to_date, 'day_of_year'))
                # .filter(ee.Filter.dayOfYear(from_date, to_date))
                .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', self.cloud_pct))
                .map(maskS2clouds)
            )
        else:
            s2_collection = (
                ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
                # .filterDate(f'{year[0]}-1-1', f'{year[1]}-12-31')
                .filter(ee.Filter.calendarRange(year[0], year[0], 'year'))
                .filter(ee.Filter.calendarRange(from_date, to_date, 'day_of_year'))
                # .filter(ee.Filter.dayOfYear(from_date, to_date))
                .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', self.cloud_pct))
                .map(maskS2clouds)
            )
        # print(s2_collection.median().bandNames())
        print(f"image accessed succeed")
        image = s2_collection.median().select(['B2', 'B3', 'B4', 'B8']).clip(region).unmask(NODATA)
        print(f"Ready to Download")
        # geemap.ee_export_image_collection(collection, out_dir=“文件夹路径”, scale = 1000)  # scale代表1000米分辨率
        geemap.ee_export_image_to_drive(image, description=self.save_name, folder=f"Cities_bin_0p5_{season}_{year[0]}", scale=10,
                                        region=region, crs="EPSG:4326")

        # geemap.download_ee_image(image, self.save_path + '.tif', scale=10, region=region, crs="EPSG:4326", max_tile_size = 8)
        print("File Save Succeed ")


def is_folder_empty(path):
    if len(os.listdir(path)) == 0:
        return True
    else:
        return False


def main(season='all', lon_lat_name='0_0', year_=2019, shp_file=r''):
    print(lon_lat_name)
    # print(region)
    # region = ee.FeatureCollection(shp_file).geometry()
    lon = float(lon_lat_name.replace("p", ".").split("_")[0])
    lat = float(lon_lat_name.replace("p", ".").split("_")[1])
    if len(YEAR) > 1:
        save_name = f'Sentinel2_{np.round(lon, 1)}_{np.round(lat, 1)}'
    else:
        save_name = f'Sentinel2_{np.round(lon, 1)}_{np.round(lat, 1)}'

    China_all_file = os.path.join(make_dir(rf'.\00028-DownloadLogs-Sentinel2-2023-10\Log\Capitals_Sentinel2_{season}_{year_}'), f'{save_name}.txt')

    if os.path.isfile(China_all_file):
        print("continue")
        pass
    else:
        # print(geemap.shp_to_ee(shp_file))
        region = geemap.shp_to_ee(shp_file).geometry()

        s2_downloader = GEEDownloader(cloud_pct=20, save_name=save_name)
        s2_downloader.download_seasonal_s2(region=region, year=YEAR, season=season)

        f = open(China_all_file, "w")  # 留存下载信息
        f.close()  # 关闭文件
        # time.sleep(5)


if __name__ == '__main__':
    # os.environ['HTTP_PROXY'] = 'http://127.0.0.1:4780'
    # os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:4780'
    debug = True
    NODATA = 0

    YEAR = [2019]
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_workers', type=int, default=0, help="Number of workers for multiprocessing")
    parser.add_argument('--cloud_pct', type=int, default=20)
    parser.add_argument('--debug', default=True)

    args = parser.parse_args()

    print('Main start ')
    # ee.Authenticate()

    ee.Initialize(project='ee-siqinglvbnu')
    print('Initialize Succeed')

    shp_root = rf'.\ValidDownloadShps_new_bin_0p5_{YEAR[0]}_cities_dissolved'

    file_paths, file_names = file_name_shp(shp_root)


    def worker(idx):
        # for season in ['all']:
        # for season in ['spring', 'summer', "autumn", 'winter']:
        for season in ['spring', 'summer', "autumn", 'winter']:
            # for season in ['all']:
            print(f"{season} begins")
            main(season=season, lon_lat_name=file_names[idx], shp_file=file_paths[idx], year_=YEAR[0])
            # return


    # worker(1)
    indices = range(len(file_names))
    # indices = range(2)
    # # indices = range(len(season))
    # indices = range(10)
    #
    # print(len(bboxes))  # Northern 60
    if args.num_workers == 0:
        for i in indices:
            # for i in range(1):
            worker(i)
    else:
        with Pool(processes=args.num_workers) as p:
            p.map(worker, indices)
