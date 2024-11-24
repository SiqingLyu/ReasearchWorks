"""
Date: 2024/11/23
author: Lsq
Function: 这个程序用于将一张单景的融合建筑物高度+建筑物足迹数据
根据对应的地理纬度（单景中心纬度），以及对应需要得到的日期数据，
得到建筑物屋顶被阴影遮挡的分布
结果将会是栅格影像，背景值为0，建筑物区域的值则对应该建筑物的遮挡系数
遮挡系数：无遮挡时为 1，建筑物被遮挡时，建筑物对应的是未被遮挡区域占总区域的比例
Last coding date:2024/11/23
Updating Log:  改用python-dem-shadow的逐像素梯度算法
"""
import cv2
from empatches022 import *
import time
from tools import *
import python_dem_shadows.shadows as sh
import python_dem_shadows.solar as so
import datetime as dt
from tqdm import tqdm

BACKGROUND = 0.0


def make_dir(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)
    return path


def get_sun_vector(date, lat, lon, timezone):
    jd = so.to_juliandate(date)  # transform date to julian date
    sun_vector = so.sun_vector(jd, lat, lon, timezone)  # compute the sun position vector
    print("SUN Vector:", sun_vector)

    return sun_vector


class GetBuildingCoverCoefficient:
    def __init__(self, footprint_data: np.ndarray, buildingheight_data: np.ndarray,
                 x_resolution: float = 2.5, y_resolution=None,
                 lon=0.0, lat=0.0, timezone=0):
        """
        类初始化函数，主要进行参数的收集
        """

        self.footprint = footprint_data
        self.building_height = buildingheight_data
        assert self.footprint.shape == self.building_height.shape
        self.x_resolution = x_resolution
        self.y_resolution = y_resolution if y_resolution is not None else x_resolution
        self.img_size = self.footprint.shape[0]
        self.lon = lon
        self.lat = lat
        self.timezone = timezone
        self.result = None

    def shadow_mask(self, sun_vector):
        """
        关键技术函数，调用python-dem-shadows的梯度阴影算法，得到全图考虑建筑物遮挡关系的阳光阴影覆盖分布shad
        """

        # 返回的shad， 1是有阳光，0是被阴影遮挡
        # shad = np.zeros_like(self.building_height)
        shad = sh.project_shadows_graphical(self.building_height, sun_vector, self.x_resolution,
                                  self.y_resolution)  # compute cast shadow
        # shad[shad == 1] = np.nan  # make a mask (1 = shadow, nan elsewhere) OPTIONAL
        # shad[shad == 0] = 1
        return shad.astype(np.uint8)

    def get_shadow_cover_map(self, sun_vector):
        """
        可以理解为此类的主要执行程序
        """
        shadow_cover_map = self.shadow_mask(sun_vector)
        roofs, areas, rates = self.get_valid_roofs(shadow_cover_map)
        self.result = roofs
        return shadow_cover_map, roofs, areas, rates

    def get_valid_roofs(self, shadow_cover_map):
        """
        根据阴影的覆盖次数、建筑物本身的mask、以及其面积、阴影高度，得到建筑物被覆盖率
        """
        valid_roof = np.where((self.footprint != BACKGROUND) & (shadow_cover_map == 1), 1, 0).astype(np.uint8)
        # 单位：平方米
        valid_roof_area = float(len(valid_roof[valid_roof == 1])) * self.x_resolution * self.y_resolution
        valid_rate = float(len(valid_roof[valid_roof == 1])) / len(self.footprint[self.footprint != BACKGROUND])
        return valid_roof, valid_roof_area, valid_rate

    def get_result(self):
        if self.result is not None:
            return self.result
        else:
            return np.zeros_like(self.footprint).astype(np.float32)


def foorprint_process(data):
    """
    对足迹数据进行腐蚀与膨胀处理
    :return: 返回处理后的足迹数据
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # ksize=5,5
    # erode
    img_temp = cv2.erode(data, kernel, iterations=2)
    # dilate
    return cv2.dilate(img_temp, kernel, iterations=2)


def main(footprint_data, buildingheight_data, sun_vector, **kwargs):
    CoverGetter = GetBuildingCoverCoefficient(footprint_data, buildingheight_data, **kwargs)
    CoverGetter.get_shadow_cover_map(sun_vector)
    return CoverGetter.get_result()


def start_process(footprint_path, height_path, save_path, patchsize=400, **kwargs):
    print('------------数据预处理中--------------\n')
    # footprint_data = cv2.imread(footprint_path,  cv2.IMREAD_UNCHANGED)
    footprint_data = read_tif(footprint_path)
    # footprint_data = Image.fromarray(footprint_data)
    # footprint_data = cv2.UMat(footprint_data)
    foorprint_process(footprint_data)
    # buildingheight_data = cv2.imread(height_path,  cv2.IMREAD_UNCHANGED)
    buildingheight_data = read_tif(height_path)
    # buildingheight_data = Image.fromarray(buildingheight_data)

    # buildingheight_data = cv2.UMat(buildingheight_data)
    # 确保两个数据形状完全一致
    assert footprint_data.shape == buildingheight_data.shape
    # footprint_data, buildingheight_data = make_shape_same(footprint_data, buildingheight_data)
    print('-------------数据分块中---------------\n')
    # patch processing
    Em = EMPatches()
    footprint_patches, indices = Em.extract_patches(footprint_data, patchsize=patchsize, overlap=0.0)
    height_patches, _ = Em.extract_patches(buildingheight_data, patchsize=patchsize, overlap=0.0)
    result_patches = []
    print('-------------主程序开始---------------\n')
    time.sleep(1)
    with tqdm(total=len(indices)) as pbar:
        pbar.set_description('Processing patches:')
        for ii in range(len(indices)):
            footprint_patch = footprint_patches[ii]
            height_patch = height_patches[ii]
            if len(footprint_patch[footprint_patch != BACKGROUND]) == 0:
                patch_result = np.zeros_like(footprint_patch)
            else:
                patch_result = main(footprint_data=footprint_patch, buildingheight_data=height_patch, **kwargs)
            result_patches.append(patch_result)
            pbar.update()
    final_result = Em.merge_patches(result_patches, indices)
    print(np.max(final_result))
    # final_result = np.round(final_result * 255).astype(np.uint8)
    print('-------------结果保存中---------------\n')
    make_dir(save_path)
    save_file = os.path.join(save_path, "TEST.tif")
    cv2.imwrite(save_file, final_result.astype(np.uint8))
    return final_result


def get_sunlight(sun_data, date, hour, lon, lat, LONMIN, LATMIN, BIN=0.05):
    """
    在使用此代码前，需要将 Sunlight 数据进行裁剪，以ChinaFishNet_0p5最小lonlat到最大lonlat为范围进行裁剪
    """
    lon_pixels = int((lon - LONMIN) / BIN)
    lat_pixels = int((lat - LATMIN) / BIN)
    hour_in_total = date * 24 + hour
    # TODO: 确定lon lat 和 x y对应关系
    sunlight_pixel = sun_data[lon_pixels, lat_pixels, hour_in_total]  # 前提时sundata是（H, W, C）
    return sunlight_pixel


def test():
    start_time = time.time()
    img_file = r'119p5_31p8.tif'
    save_path = r'Test'
    d = dt.datetime(2023, 12, 21, 15, 00, 30)  # acquisition date and time from im metadata
    tzone = 8  # time zone of the caquisition date (here Zulu = UTM 0)
    sun_vector = get_sun_vector(d, lat=31.8, lon=-119.5, timezone=tzone)
    if sun_vector[2] < 0:
        return
    start_process(footprint_path=img_file, height_path=img_file, save_path=save_path, patchsize=30000,
                  lat=31.8, lon=-119.5, timezone=tzone, sun_vector=sun_vector, x_resolution=2.5)
    over_time = time.time()
    print(f"单个patch时间为：{over_time - start_time}s")


if __name__ == '__main__':
    test()
    # sunlight_root = r'total.tif'
    # footprint_file = r'lon_lat.tif'
    # height_file = r'lon_lat.tif'
    # save_file = r'lon_lat.tif'
    # lon_v, lat_v = os.path.split(footprint_file)[1].split("_")[0], os.path.split(footprint_file)[1].split("_")[0]
    # lon_v = float(lon_v)
    # lat_v = float(lat_v)
    #
    # imaging_date = 360
    # eastwest_buffer = 80
    # time_hour_ = 12
    # # data preprocessing
    # start_process(footprint_file, height_file, save_file,
    #               latitude=lat_v, imaging_date=imaging_date,
    #               eastwest_buffer=eastwest_buffer, time_hour=time_hour_)
    #
    #
    # # get sunlight_data
