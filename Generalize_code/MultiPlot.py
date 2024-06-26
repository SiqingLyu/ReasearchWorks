import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
from tools import *
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'NSimSun,Times New Roman'


def get_leveled_MAE(gt, pred, if_height=''):
    metrics = {}
    if if_height == 'Transfer':
        gt /= 3
        pred /= 3
        r = range(1, 31)
    else:
        r = range(1, 91) if if_height else range(1, 31)
    for ii in r:
        gt_tmp = gt[gt == ii]
        pred_tmp = pred[gt == ii]
        if len(gt_tmp) == 0:
            # metrics[ii] = "Nodata"
            continue
        MAE = get_MAE(gt_tmp, pred_tmp)
        # RMSE = get_RMSE(gt_tmp, pred_tmp)
        metrics[ii] = MAE
    return metrics


def get_leveled_RMSE(gt, pred, if_height=False):
    metrics = {}
    r = range(1, 91) if if_height else range(1, 31)
    for ii in r:
        gt_tmp = gt[gt == ii]
        pred_tmp = pred[gt == ii]
        if len(gt_tmp) == 0:
            # metrics[ii] = "Nodata"
            continue
        # MAE = get_MAE(gt_tmp, pred_tmp)
        RMSE = get_RMSE(gt_tmp, pred_tmp)
        metrics[ii] = RMSE
    return metrics


def get_xy_from_dict(dict_data):
    x = []
    y = []
    for k in dict_data.keys():
        x.append(k)
        y.append(dict_data[k])
    return x, y


def plot_gedi():
    GEDI_data = read_json(
        r'D:\Codes\V100\1_HebeiGeneralization\SEASON-T-Generalization\Data\GEDI_process\GEDI_all_data_shenzhen.json')
    GEDI_shenzhen = np.array(GEDI_data["GEDI"]) / 3
    Lidar_shenzhen = np.array(GEDI_data["LIDAR"]) / 3
    GEDI_MAEs = get_leveled_MAE(gt=Lidar_shenzhen, pred=GEDI_shenzhen, if_height=False)
    GEDI_RMSEs = get_leveled_RMSE(gt=Lidar_shenzhen, pred=GEDI_shenzhen, if_height=False)
    print(GEDI_MAEs, '\n', GEDI_RMSEs)

    GABLE_data = read_json(r'G:\ProductData\GABLE_61cities_join_byAmap_json\all_data.json')
    GABLE_61city = np.array(GABLE_data["GABLE/3"])
    AMAP_61city = np.array(GABLE_data["AMAP"])
    GABLE_MAEs = get_leveled_MAE(gt=AMAP_61city, pred=GABLE_61city, if_height=False)
    GABLE_RMSEs = get_leveled_RMSE(gt=AMAP_61city, pred=GABLE_61city, if_height=False)
    print(GABLE_MAEs, '\n', GABLE_RMSEs)

    plt.figure(dpi=400)
    GEDI_MAE_x, GEDI_MAE_y = get_xy_from_dict(GEDI_MAEs)
    # GEDI_MAE_x, GEDI_MAE_y = get_xy_from_dict(GEDI_MAEs)
    # GEDI_MAE_x, GEDI_MAE_y = get_xy_from_dict(GEDI_MAEs)
    GABLE_MAE_x, GABLE_MAE_y = get_xy_from_dict(GABLE_MAEs)
    plt.plot(GEDI_MAE_x, GEDI_MAE_y, color='red', label="GEDI(Shenzhen)", alpha=0.8)
    plt.plot(GABLE_MAE_x, GABLE_MAE_y, color='blue', label="GABLE(61City)", alpha=0.8)
    plt.xlabel("Number of stories", fontsize=20)
    plt.ylabel("MAE", fontsize=20)
    plt.legend(fontsize=14)
    plt.show()


def plot_json(json_file, color='red', lable='Test', if_height=False):
    data = read_json(json_file)
    pred = np.array(data["pred"])
    gt = np.array(data["gt"])
    MAEs = get_leveled_MAE(gt=gt, pred=pred, if_height=if_height)
    RMSEs = get_leveled_RMSE(gt=gt, pred=pred, if_height=if_height)
    print(MAEs, '\n', RMSEs)
    MAE_x, MAE_y = get_xy_from_dict(MAEs)
    plt.plot(MAE_x, MAE_y, color=color, label=lable, alpha=0.8)


def main():
    plt.figure(dpi=400)
    plot_json(r'SEASONet.json', 'red', 'SEASONet', "Transfer")
    plot_json(r'WSF3D.json', 'orange', 'WSF3D', "Transfer")
    plot_json(r'GABLE_Metric_META.json', 'green', 'GABLE', "Transfer")
    plot_json(r'CNBH.json', 'blue', 'CNBH', "Transfer")
    plot_json(r'GEDI_all_data.json', 'purple', 'GEDI', "Transfer")

    plt.xlabel("Number of stories", fontsize=20)
    plt.ylabel("MAE", fontsize=20)
    plt.xlim(0, 30)
    plt.grid(alpha=0.5)
    plt.legend(fontsize=14)
    plt.show()


if __name__ == '__main__':
    main()


    # # j_data = read_json(r'G:\ProductData\CBRA\CBRA_data_dict\61CityIoU_in_difFloorThds_Shenzhen.json')
    # # j_data1 = read_json(r'G:\ProductData\CBRA\CBRA_data_dict\LidarIoU_in_difFloorThds_Shenzhen.json')
    # j_data = read_json(r'G:\ProductData\GABLE_TIF_10m\61CityIoU_in_difFloorThds.json')
    # j_data1 = read_json(r'G:\ProductData\East_Asian_buildings\61CityIoU_in_difFloorThds.json')
    # j_data2 = read_json(r'G:\ProductData\CBRA\CBRA_data_dict\61CityIoU_in_difFloorThds.json')
    # plt.figure(figsize=(7, 5), dpi=400)
    #
    # x, y = [], []
    # for k in j_data.keys():
    #     x.append(k)
    #     y.append(j_data[k])
    # plt.plot(x, y, color='blue', label='GABLE')
    #
    # x, y = [], []
    # for k in j_data1.keys():
    #     x.append(k)
    #     y.append(j_data1[k])
    # plt.plot(x, y, color='green', label='EastAsian')
    #
    # x, y = [], []
    # for k in j_data2.keys():
    #     x.append(k)
    #     y.append(j_data2[k])
    # plt.plot(x, y, color='red', label='CBRA')
    #
    # # x, y = [], []
    # # for k in j_data.keys():
    # #     x.append(k)
    # #     y.append(j_data[k])
    # # plt.plot(x, y, color='orange', label='CBRA metric by AMAP')
    # #
    # # x, y = [], []
    # # for k in j_data1.keys():
    # #     x.append(k)
    # #     y.append(j_data1[k])
    # # plt.plot(x, y, color='red', label='CBRA metric by LiDAR')
    # #
    # # j_data = read_json(r'G:\ProductData\East_Asian_buildings\61CityIoU_in_difFloorThds_Shenzhen.json')
    # # j_data1 = read_json(r'G:\ProductData\East_Asian_buildings\LidarIoU_in_difFloorThds_Shenzhen.json')
    # # x, y = [], []
    # # for k in j_data.keys():
    # #     x.append(k)
    # #     y.append(j_data[k])
    # # plt.plot(x, y, color='green', label='EastAsian metric by AMAP')
    # #
    # # x, y = [], []
    # # for k in j_data1.keys():
    # #     x.append(k)
    # #     y.append(j_data1[k])
    # # plt.plot(x, y, color='blue', label='EastAsian metric by LiDAR')
    #
    # plt.xlabel("Number of stories", fontsize=18)
    # plt.ylabel("IoU", fontsize=18)
    # plt.ylim(0.2, 0.9)
    # plt.grid(alpha=0.5)
    # plt.legend(fontsize=12)
    # plt.show()