from tools import *
import json


def get_IoU_single(file1, file2, nodatas, floor_thd=7, if_height=False):
    print("processing ", file1)

    data1 = read_tif(file1)
    data2 = read_tif(file2)
    nodata1, nodata2 = nodatas
    data2[data2 < 0] = nodata2
    data1[data1 < 0] = nodata1

    if if_height:
        data2 = np.round(data2 / 3)

    assert data2.shape == data1.shape, f"{data1.shape}, {data2.shape}"

    # IoU
    data1[data2 != floor_thd] = nodata1
    data2[data2 != floor_thd] = nodata2

    union = np.where((data1 != nodata1) | (data2 != nodata2), 1, 0)
    inter = np.where((data1 != nodata1) & (data2 != nodata2), 1, 0)
    union_num = float(len(union[union == 1]))
    inter_num = float(len(inter[inter == 1]))
    if (union_num == 0) | (inter_num == 0):
        print(f"nodata in this level {floor_thd}")
        return
    IoU = inter_num / union_num

    print(f"file: {file1}, IoU: {IoU}")
    return IoU
    # # Recall
    # TP = np.where((data2 != nodata2) & (data1 != nodata1), 1, 0)
    # TN = np.where((data2 != nodata2) & (data1 != nodata1), 1, 0)
    # FP = np.where((data2 == nodata2) & (data1 != nodata1), 1, 0)
    # FN = np.where((data2 != nodata2) & (data1 == nodata1), 1, 0)
    # TP = float(len(TP[TP == 1]))
    # TN = float(len(TN[TN == 1]))
    # FP = float(len(FP[FP == 1]))
    # FN = float(len(FN[FN == 1]))
    # precision = TP / (TP + FP)
    # recall = TP / (TP + FN)
    # F1 = 2 * (precision * recall) / (precision + recall)


def get_IoU_dir(dir1, dir2, nodatas, save_json='Test.json', floor_thd=7, if_save=False):
    # dir2 默认真值
    filepaths1, filenames1 = file_name_tif(dir1)
    filepaths2, filenames2 = file_name_tif(dir2)
    IoUs = {}
    mertics = {}
    union_num_total = 0.0
    inter_num_total = 0.0
    pre_total = 0.0
    rec_total = 0.0
    F1_total = 0.0
    assert len(filenames1) == len(filenames2), f"{len(filenames1)} {len(filenames2)}"
    for ii in range(len(filenames1)):
        print("processing ", filenames1[ii])
        City_name = filenames1[ii].split('_')[0]
        if City_name != "Shenzhen":
            continue
        if City_name in name_change_dict.keys():
            City_name = name_change_dict[City_name]
        for jj in range(len(filenames2)):
            filename2 = filenames2[jj]
            if filename2 != City_name:
                continue
            filepath1 = filepaths1[ii]
            filepath2 = filepaths2[jj]
            data1 = read_tif(filepath1)
            data2 = read_tif(filepath2)

            assert data2.shape == data1.shape

            # IoU
            nodata1, nodata2 = nodatas
            data2[data2 < 0] = nodata2
            data1[data1 < 0] = nodata1
            data1[data2 != floor_thd] = nodata1
            data2[data2 != floor_thd] = nodata2

            union = np.where((data1 != nodata1) | (data2 != nodata2), 1, 0)
            inter = np.where((data1 != nodata1) & (data2 != nodata2), 1, 0)
            union_num = float(len(union[union == 1]))
            inter_num = float(len(inter[inter == 1]))
            if (union_num == 0) | (inter_num == 0):
                continue
            union_num_total += union_num
            inter_num_total += inter_num
            IoU = inter_num / union_num
            IoUs[City_name] = IoU

            print(f"City: {City_name}, IoU: {IoU}")

            # Recall
            TP = np.where((data2 != nodata2) & (data1 != nodata1), 1, 0)
            TN = np.where((data2 != nodata2) & (data1 != nodata1), 1, 0)
            FP = np.where((data2 == nodata2) & (data1 != nodata1), 1, 0)
            FN = np.where((data2 != nodata2) & (data1 == nodata1), 1, 0)
            TP = float(len(TP[TP == 1]))
            TN = float(len(TN[TN == 1]))
            FP = float(len(FP[FP == 1]))
            FN = float(len(FN[FN == 1]))
            precision = TP / (TP + FP)
            recall = TP / (TP + FN)
            F1 = 2 * (precision * recall) / (precision + recall)
            mertics[City_name] = [precision, recall, F1]
            pre_total += precision
            rec_total += recall
            F1_total += F1

    if union_num_total == 0:
        IoUs["Overall"] = 0
    else:
        IoUs["Overall"] = inter_num_total / union_num_total
    print(f"Overall IoU : {IoUs['Overall']}")

    if if_save:
        write_json(save_json, IoUs)

        mertics["Overall"] = [pre_total / len(filenames1), rec_total / len(filenames1), F1_total / len(filenames1)]
        write_json(save_json[:-5] + '_metric.json', mertics)
    return IoUs["Overall"]


name_change_dict = {
    "Harbin": "Haerbin",
    "Macau": "Aomen",
    "Hongkong": "Xianggang",
    "Ordos": "Eerduosi",
    "Hohhot": "Huhehaote",
    "Lhasa": "Lasa"
}

import pandas as pd


def json_to_excel(json_file):
    with open(json_file, 'r') as json_f:
        json_data = json.load(json_f)
        print(json_data)
        df = pd.DataFrame(json_data, index=[0, 0, 0])
        df.to_excel(rf'{json_file[:-5]}.xls', index=False)


if __name__ == '__main__':
    # get_IoU_dir(dir1=r'G:\ProductData\CBRA_61cities_2p5m',
    #             dir2=r'G:\ProductData\61cities_AMAP_Raster_wgs84_2p5m',
    #             nodatas=[0, 255],
    #             save_json=r'G:\ProductData\CBRA\61CityIoU.json')
    #
    # json_to_excel(r'G:\ProductData\CBRA\61CityIoU_metric.json')
    #
    # get_IoU_dir(dir1=r'G:\ProductData\CBRA_61cities_2p5m',
    #             dir2=r'G:\ProductData\61cities_AMAP_Raster_wgs84_2p5m',
    #             nodatas=[0, 255],
    #             save_json=r'G:\ProductData\CBRA\61CityIoU.json')
    #
    # json_to_excel(r'G:\ProductData\CBRA\61CityIoU_metric.json')
    #
    # get_IoU_dir(dir1=r'G:\ProductData\East_Asian_buildings\61cities_2p5m_',
    #             dir2=r'G:\ProductData\61cities_AMAP_Raster_49N_2p5m',
    #             nodatas=[255, 255],
    #             save_json=r'G:\ProductData\East_Asian_buildings\61CityIoU.json')
    #
    # json_to_excel(r'G:\ProductData\East_Asian_buildings\61CityIoU_metric.json')

    # floor_thd = 7
    iou_dict = {}
    for floor_thd in range(1, 31):
        # iou_tmp = get_IoU_dir(dir1=r'G:\ProductData\GABLE_TIF_10m',
        #                       dir2=r'G:\ProductData\AMAP_10m_wgs84_for_GABLE_in_61city',
        #                       nodatas=[255, 0],
        #                       save_json=rf'G:\ProductData\GABLE_TIF_10m\61CityIoU_floorthd{floor_thd}.json',
        #                       floor_thd=floor_thd)
        # iou_tmp = get_IoU_single(file1=r'G:\ProductData\GABLE_TIF_10m\Shenzhen.tif',
        #                          file2=r'D:\Dataset\0_Lidar\Shenzhen_BH_Lidar_10m_wgs84_smallregion_forGABLE.tif',
        #                          nodatas=[255, 0], if_height=True, floor_thd=floor_thd
        #                          )
        # iou_tmp = get_IoU_dir(dir1=r'G:\ProductData\CBRA_61cities_2p5m',
        #         dir2=r'G:\ProductData\61cities_AMAP_Raster_wgs84_2p5m',
        #         nodatas=[0, 255],
        #         save_json=rf'G:\ProductData\CBRA\CBRA_data_dict\61CityIoU_floorthd{floor_thd}.json', floor_thd=floor_thd)
        # iou_tmp = get_IoU_single(file1=r'D:\Dataset\0_Lidar\Shenzhen_CBRA_2018_10m.tif',
        #                          file2=r'D:\Dataset\0_Lidar\Shenzhen_BH_Lidar_10m_wgs84_smallregion111.tif',
        #                          nodatas=[0, 0], if_height=True, floor_thd=floor_thd
        #                          )
        # iou_tmp = get_IoU_dir(dir1=r'G:\ProductData\East_Asian_buildings\61cities_2p5m_',
        #         dir2=r'G:\ProductData\61cities_AMAP_Raster_49N_2p5m',
        #         nodatas=[255, 255],
        #         save_json=rf'G:\ProductData\East_Asian_buildings\61CityIoU_floorthd{floor_thd}.json', floor_thd=floor_thd)
        iou_tmp = get_IoU_single(file1=r'D:\Dataset\0_Lidar\Shenzhen_EastAsian_10m_clip.tif',
                                 file2=r'D:\Dataset\0_Lidar\Shenzhen_BH_Lidar_10m_wgs84_smallregion111.tif',
                                 nodatas=[255, 0], if_height=True, floor_thd=floor_thd
                                 )

        iou_dict[floor_thd] = iou_tmp
    write_json(rf'G:\ProductData\East_Asian_buildings\LidarIoU_in_difFloorThds_Shenzhen.json', iou_dict)
