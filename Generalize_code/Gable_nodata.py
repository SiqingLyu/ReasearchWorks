"""
GABLE 数据的年份是2023年, 但是当前只有2018有0.5°的数据，因此在2024.6.15使用2018年CBRA数据进行实验
得到的json中，形式是：{"lon_lat": [file size, total area], ......}
后续可以把get_total_area整合进tools里面
"""
import sys

sys.path.append(r'D:/PythonProjects/DataProcess/codes')
from tools import *
from osgeo import ogr, osr
from empatches022 import EMPatches

NODATA = 0
NODATA_IMG = 255
BUILDING = 255


def get_nodata_area(cbra_root):
    nodata_dict = read_json(r'GABLE_NODATA_JSON.json')
    paths, names = file_name_tif(cbra_root)
    nodata_building_pixels_all = 0.
    building_pixels_all = 0.
    building_area_all_GABLE = 0.0
    for ii in range(len(paths)):
        print(f"processing {ii}/{len(paths)}")
        path_ = paths[ii]
        name_ = names[ii]
        lon_lat = f"{name_.split('_')[-2]}_{name_.split('_')[-1]}"
        # print(lon_lat)
        data_ = read_tif(path_)
        building_pixels = len(data_[data_ == BUILDING])

        if nodata_dict[lon_lat] == "Nodata":
            nodata_building_pixels_all += building_pixels
            building_pixels_all += building_pixels
        else:
            building_pixels_all += building_pixels
            building_area_all_GABLE += nodata_dict[lon_lat][1]

    nodata_area = nodata_building_pixels_all * 100
    total_area = building_pixels_all * 100
    nodata_rate = nodata_area / total_area
    GABLE_rate = nodata_area / building_area_all_GABLE
    print(f"GABLE 缺失建筑物面积约为：{nodata_area}m^2, 即{float(nodata_area) / 1000000}km^2,"
          f" 占CBRA总面积比 {np.round(100 * nodata_rate, 2)}%， 占GABLE总面积比：{np.round(100 * GABLE_rate, 2)}%")
    return nodata_area, nodata_rate, GABLE_rate


def get_total_area(shpPath):
    '''计算面积'''
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shpPath, 1)
    layer = dataSource.GetLayer()

    src_srs = layer.GetSpatialRef()  # 获取原始坐标系或投影
    tgt_srs = osr.SpatialReference()
    tgt_srs.ImportFromEPSG(32649)  # WGS_1984_UTM_Zone_49N投影的ESPG号，需要改自己的要去网上搜下，这个不难
    transform = osr.CoordinateTransformation(src_srs, tgt_srs)  # 计算投影转换参数
    # geosr.SetWellKnownGeogCS("WGS_1984_UTM_Zone_49N")

    # new_field = ogr.FieldDefn("Area", ogr.OFTReal)  # 创建新的字段
    # new_field.SetWidth(32)
    # new_field.SetPrecision(16)
    # layer.CreateField(new_field)
    area_total = 0.0
    for feature in layer:
        geom = feature.GetGeometryRef()
        geom2 = geom.Clone()
        geom2.Transform(transform)

        area_in_sq_m = geom2.GetArea()  # 默认为平方米
        area_total += area_in_sq_m
        # area_in_sq_km = area_in_sq_m / 1000000 #转化为平方公里

        # feature.SetField("Area", area_in_sq_m)
        # layer.SetFeature(feature)
    # print(f"总面积是：{area_total} m^2", f"{area_total == 0.0}")
    return area_total


def main():
    paths, names = file_name_tif(r'G:\Data\Sentinel-2\China_0p5\all')
    paths_, names_ = file_name_tif(r'F:\Data\Sentinel-2\China_0p5\all')
    all_paths = paths + paths_
    all_names = names + names_

    gable_dict = {}
    gable_paths, gable_names = file_name_shp('G:\ProductData\GABLE_CLIP')
    print("统计格网内总面积---------")
    for ii in range(len(gable_names)):
        gable_name = gable_names[ii]
        gable_path = gable_paths[ii]
        lon_min = gable_name.split('_')[-4].replace('p', '.')
        lat_min = gable_name.split('_')[-3].replace('p', '.')
        cor_name = f"{lon_min}_{lat_min}"
        print(f"processing {gable_name}")
        file_size = os.path.getsize(gable_path) / 1024  # kb
        area_total = get_total_area(gable_path)
        # print(cor_name, file_size)
        if cor_name not in gable_dict.keys():
            gable_dict[cor_name] = [file_size, 1, area_total]
        else:
            gable_dict[cor_name][0] += file_size
            gable_dict[cor_name][1] += 1
            gable_dict[cor_name][2] += area_total
    print("统计nodata，记录为json文件---------")
    nodata_dict = {}
    nodata_num = 0
    for jj in range(len(all_names)):
        name_ = all_names[jj]
        path_ = all_paths[jj]
        cor_name = f"{name_.split('_')[-2]}_{name_.split('_')[-1]}"
        if cor_name not in gable_dict.keys():
            nodata_dict[cor_name] = "Nodata"
            nodata_num += 1
            continue
        # assert cor_name in gable_dict.keys(), f"{cor_name}, {gable_dict.keys()}"

        if gable_dict[cor_name][2] == 0.0:  # 面积为0
            nodata_dict[cor_name] = "Nodata"
            nodata_num += 1
        else:
            nodata_dict[cor_name] = [gable_dict[cor_name][0], gable_dict[cor_name][2]]
    write_json('GABLE_NODATA_JSON.json', nodata_dict)
    print(f"0.5°尺度上，{np.round(100 * (nodata_num / len(all_names)), 2)}%的GABLE数据存在缺失")


def get_all_area(dir, name_):
    shp_paths, shp_names = file_name_shp(dir)
    area_all = 0.0
    data_dict = {}
    for ii in range(len(shp_paths)):
        print(f"{ii + 1}/{len(shp_paths)}")
        shp_path = shp_paths[ii]
        shp_name = shp_names[ii]
        area_tmp = get_total_area(shp_path)
        if shp_name not in data_dict.keys():
            data_dict[shp_name] = area_tmp
        area_all += area_tmp
    write_json(rf'{name_}_area.json', data_dict)
    return area_all


def find_lost_area_single(img, gt, patch_size=64):
    img_lost_num = 0.
    img_lost_area = 0.
    gt_extra_num = 0.
    gt_extra_area = 0.
    gt_glue_area = 0.
    em = EMPatches()
    img_patches, img_indices = em.extract_patches(img, patchsize=patch_size, overlap=0)
    gt_patches, gt_indices = em.extract_patches(gt, patchsize=patch_size, overlap=0)
    assert len(img_patches) == len(gt_patches)
    total_num = len(gt_patches)
    total_area = 0.

    for ii in range(len(gt_patches)):
        img_tmp = img_patches[ii]
        gt_tmp = gt_patches[ii]
        img_area = len(img_tmp[img_tmp != NODATA_IMG])
        gt_area = len(gt_tmp[gt_tmp != NODATA])
        union_area = len(gt_tmp[(gt_tmp != NODATA) | (img_tmp != NODATA_IMG)])

        if (img_area == 0) and (gt_area != 0):
            img_lost_num += 1
            img_lost_area += gt_area
        if (gt_area == 0) and (img_area != 0):
            gt_extra_num += 1
            gt_extra_area += img_area
        if (gt_area != 0) and (img_area != 0):
            gt_glue_area += (union_area - img_area)

        total_area += union_area  # 单位是像素

    return total_num, img_lost_num, gt_extra_num, total_area, img_lost_area, gt_extra_area, gt_glue_area


def find_lost_area_dir(img_root, gt_root, patch_size=128, res=10):
    def process_CBRA_name(name_):
        _, year, lon_min, lat_min = name_.split('_')
        loc_name = f"{lon_min.replace('.', 'p')}_{lat_min.replace('.', 'p')}"
        return loc_name

    # img 是其他产品， gt是CBRA
    lost_area_total = 0.
    extra_area_total = 0.
    total_area = 0.
    glue_area_total = 0.
    # img_paths, img_names = file_name_tif(img_root)
    gt_paths, gt_names = file_name_tif(gt_root)
    # assert img_names <= gt_names
    for ii in range(len(gt_names)):
        gt_name = gt_names[ii]
        loc_name = process_CBRA_name(gt_name)
        img_path = os.path.join(img_root, loc_name + '.tif')
        gt = read_tif(gt_paths[ii])
        if not os.path.isfile(img_path):
            img = np.zeros_like(gt)
            img[img == 0] = NODATA_IMG
        else:
            img = read_tif(img_path)
        print(img_path, gt_name)
        _, _, _, total, lost, extra, glue = find_lost_area_single(img, gt, patch_size)
        total_area += total
        lost_area_total += lost
        extra_area_total += extra
        glue_area_total += glue

    lost_rate = lost_area_total / total_area
    extra_rate = extra_area_total / total_area
    glue_rate = glue_area_total / total_area

    lost_area = lost_area_total * res * res
    extra_area = extra_area_total * res * res
    glue_arae = glue_area_total * res * res
    print(img_root)
    print(f"img 缺失建筑物面积比例为：{lost_rate}， 共缺失{lost_area}m^2")  # let img = Product, gt = CBRA
    print(f"gt  多出建筑物面积比例为：{extra_rate}， 共缺失{extra_area}m^2")
    print(f"gt  粘连建筑物面积比例为：{glue_rate}， 共缺失{glue_arae}m^2")
    return lost_rate, extra_rate, lost_area, extra_area


def get_area_diff_in_61city(roots, res, nodatas):
    total_area_dict = {}
    lost_area = 0.
    city_area_dict = {}
    city_rate_dict = {}

    for k in ["GT", "GABLE", "CBRA"]:
        root_path = roots[k]
        nodata = nodatas[k]
        res_ = res[k]
        paths, names = file_name_tif(root_path)
        print(len(paths))  # confirm the length
        area_total = 0.
        city_areas = {}

        for ii in range(len(paths)):
            path = paths[ii]
            name_ = names[ii]
            city = name_.split('_')[0]

            data = read_tif(path)
            data[data < 0] = nodata
            building_pixels = len(data[data != nodata])
            building_area = building_pixels * res_ * res_
            area_total += building_area
            city_areas[city] = building_area

        city_area_dict[k] = city_areas
        total_area_dict[k] = area_total

        if (k != "GT") and ("GT" in total_area_dict.keys()):
            city_rates = {}
            for city in city_areas.keys():
                lost_rate = city_areas[city] / city_area_dict["GT"][city]
                lost_rate = 1 - lost_rate if (1 - lost_rate) >= 0 else 0.0
                city_rates[city] = lost_rate
            city_rate_dict[k] = city_rates
    return total_area_dict, city_rate_dict


if __name__ == '__main__':
    # find_lost_area_dir(img_root=r'G:\ProductData\East_Asian_buildings\China_0p5_inLoc_10m_confirm',
    #                    gt_root=r'G:\ProductData\CBRA\CBRA_building_10m_0p5\2018')

    find_lost_area_dir(img_root=r'G:\ProductData\GABLE_0p5_10m_confirm',
                       gt_root=r'G:\ProductData\CBRA\CBRA_building_10m_0p5\2018')

    # res_dict = {"GABLE": 10., "CBRA": 2.5, "GT": 10.}
    # nodata_dict = {"GABLE": 255, "CBRA": 0, "GT": 0}
    # root_dict = {"GABLE": r'G:\ProductData\GABLE_TIF_10m\61City',
    #              "CBRA": r'G:\ProductData\CBRA_61cities_2p5m',
    #              "GT": r'D:\Dataset\@62allcities\Label_bk0_nodata0_wgs84'}
    # total_area, rate_dict = get_area_diff_in_61city(roots=root_dict, res=res_dict, nodatas=nodata_dict)
    # print(total_area)
    # print(rate_dict)
    # write_json("GABLE_61City_area_rate.json", rate_dict["GABLE"])
    # write_json("CBRA_61City_area_rate.json", rate_dict["CBRA"])
    # main()
    # get_nodata_area(r'G:\ProductData\CBRA\CBRA_building_10m_0p5\2018')

    # EASTASIA_AREA = get_all_area(r'G:\ProductData\East_Asian_buildings\China_0p5', name_='EAST_ASIA')
    # CBRA_AREA = get_all_area(r'G:\ProductData\CBRA\CBRA_2021_10m_shp', name_='CBRA')
    # GABLE_AREA = get_all_area(r'G:\ProductData\GABLE_CLIP', name_='GABLE')
    #
    # print(f"GABLE总面积: {GABLE_AREA}")  # 84379,139837.84188 m^2
    # print(f"CBRA总面积: {CBRA_AREA}")  # 101680,014668.3583
    # print(f"EASTASIAN 总面积: {EASTASIA_AREA}")  # 48077,784135.14713

    # get_total_area(r'G:\ProductData\GABLE_CLIP\河南省_part5_115p0_34p8_115p5_35p3.shp')

    # dict_data = read_json(r'GABLE_NODATA_JSON.json')
    # GABLE_AREA = 0.
    # for k in dict_data.keys():
    #     GABLE_AREA += dict_data[k][1] if dict_data[k] != "Nodata" else 0
    # print(f"GABLE总面积: {GABLE_AREA / 1000000} km^2")  # 84379.13983784188 km^2
