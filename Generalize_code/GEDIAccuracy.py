from GEDISelect import *
from Data.empatches022 import *
from tools import *
import matplotlib as mpl

mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'NSimSun,Times New Roman'
NODATA = -9999


def get_metrics_in_shenzhen(GT, GEDI):
    assert GT.shape == GEDI.shape
    # print(np.max(GT), np.max(GEDI))
    # GT_data = GT[(GEDI != NODATA) & (GT > 10)]
    # GEDI_data = np.round(GEDI[(GEDI != NODATA) & (GT > 10)])
    GT_data = GT[(GEDI > 65) & (GEDI < 70) & (GT > 0)]
    GEDI_data = np.round(GEDI[(GEDI > 65) & (GEDI < 70) & (GT > 0)])

    # print(GT, GT_data, GEDI_data)

    mae = get_MAE(GT_data, GEDI_data)
    rmse = get_RMSE(GT_data, GEDI_data)
    return mae, rmse, GT_data, GEDI_data


def get_good_samples_in_shenzhen(GT, GEDI):
    assert GT.shape == GEDI.shape
    diff_data = np.abs(GT - GEDI)
    GT_data = GT[(diff_data <= 1) & (GT >= 5)]
    GEDI_data = GEDI[(diff_data <= 1) & (GT >= 5)]
    return GT_data, GEDI_data


def get_good_rate_in_shenzhen(GT, GEDI, thd_rate):
    assert GT.shape == GEDI.shape
    diff_data = np.abs(GT - GEDI)
    GEDI = np.round(GEDI)
    good_rates = {}
    good_map = np.zeros_like(GEDI)
    for height in range(2, 100):
        good_thd = thd_rate * height
        total_num = len(GEDI[GEDI == height])

        if total_num == 0:
            continue
        good_num = len(GEDI[(GEDI == height) & (diff_data <= good_thd)])
        good_rate = good_num / total_num
        good_rates[height] = good_rate

        good_map = np.where((GEDI == height) & (diff_data <= good_thd), 1, good_map)
    good_map = good_map.astype(np.uint8)
    return good_rates, good_map


def get_MAE(a, b):
    return np.mean(np.abs(a.flatten() - b.flatten()))


def get_RMSE(a, b):
    diff = a.flatten() - b.flatten()
    RMSE = np.sqrt(np.mean(diff * diff))
    return RMSE


def compare_the_strategy(GT, GEDI):
    print("在处理GEDI之前，直接使用GEDI作为高度，其结果为：")
    MAE, RMSE, _, _ = get_metrics_in_shenzhen(GT, GEDI)
    print(f"GEDI的数据的MAE为{MAE}，RMSE为{RMSE}")

    GT_all = np.array([])
    GEDI_all = np.array([])
    em = EMPatches()
    patches_gt, indices = em.extract_patches(GT, patchsize=128, overlap=0.0)
    patches_GEDI, _ = em.extract_patches(GEDI, patchsize=128, overlap=0.0)
    assert len(patches_GEDI) == len(patches_gt)
    for ii in range(len(patches_GEDI)):
        # print(f"{ii}/{len(patches_GEDI)}")
        patch_GEDI = patches_GEDI[ii]
        patch_gt = patches_gt[ii]

        GEDI_process = select_GEDI(patch_GEDI, patch_gt)
        if GEDI_process is None:
            continue
        _, _, gt_tmp, gedi_tmp = get_metrics_in_shenzhen(patch_gt, GEDI_process)

        GT_all = np.hstack((GT_all, gt_tmp))
        GEDI_all = np.hstack((GEDI_all, gedi_tmp))

    mae = get_MAE(GT_all, GEDI_all)
    rmse = get_RMSE(GT_all, GEDI_all)
    print("在处理GEDI之后，其结果为：")
    print(f"GEDI的数据的MAE为{mae}，RMSE为{rmse}")

    # compare_the_strategy(GT, GEDI)


if __name__ == '__main__':
    GT = r'D:\Dataset\0_Lidar\Shenzhen_BH_Lidar_10m_.tif'
    GEDI = r'D:\Dataset\0_Lidar\SHENZHEN_rh98_prj_clip.tif'
    GT = read_tif(GT)
    GEDI = read_tif(GEDI)
    GT[GT < 0] = 0

    # 比较使用策略前后GEDI的准确性变化
    # compare_the_strategy(GT, GEDI)

    # # 得到GEDI中质量较好的点
    # good_GT, good_GEDI = get_good_samples_in_shenzhen(GT, GEDI)
    # good_GT = list(good_GT)
    # good_GEDI = np.round(good_GEDI)
    # good_GEDI = list(good_GEDI)
    # bin_edges = np.arange(min(good_GEDI), max(good_GEDI) + 2)
    # plt.hist(good_GEDI, bins=bin_edges)
    # plt.show()

    # 得到GEDI中质量较好的比例，并且将各个高度上符合条件的位置记录下来
    thd_rate = 0.15
    GT_ = GT[(GEDI >= 1) & (GEDI < 100) & (GT > 0)]
    GEDI_ = np.round(GEDI[(GEDI >= 1) & (GEDI < 100) & (GT > 0)])
    # all_dict = {"LIDAR": GT_.tolist(), "GEDI": GEDI_.tolist()}
    # write_json("GEDI_all_data.json", all_dict)
    # print("over")
    rate_dict, good_map = get_good_rate_in_shenzhen(GT_, GEDI_, thd_rate)
    GEDI_ = list(GEDI_)
    GEDI_ = count_list(GEDI_)

    x = []
    y1 = []
    y2 = []
    for k in rate_dict.keys():
        x.append(k)
        y1.append(rate_dict[k])
        y2.append(GEDI_[k])

    # fig, ax2 = plt.subplots(figsize=(8, 5), dpi=400)
    # ax2.set_xlim(0, 100)
    # ax2.set_xlabel('GEDI height', fontsize=20)
    #
    # ax1 = ax2.twinx()  # 创建与ax1共享x轴的副本ax2
    # # ax1.bar(x, y1, color='blue')
    # ax1.fill_between(x, y1, color='red', alpha=0.5)
    # ax1.set_ylabel('Fine Data proportion', color='red', fontsize=16)
    # ax1.tick_params(axis='y', color='red')
    # ax1.set_ylim(0, 1)
    #
    # # 在ax2上绘制第二条曲线（使用ax2）
    # # ax2.bar(x, y2, color='red')
    # ax2.fill_between(x, y2, color='blue', alpha=0.5)
    # ax2.set_ylabel('Overall pixel counts', color='blue', fontsize=16)
    # ax2.tick_params(axis='y', color='blue')
    # ax2.set_ylim(0, 6000)
    #
    # # 设置图例
    # ax1.legend(["Fine Data proportion"], loc='upper right', fontsize=12)
    # ax2.legend(["Overall pixel counts"], loc='upper left', fontsize=12)
    #
    # # 显示图像
    # plt.show()

    # bin_edges = np.arange(min(GEDI_), max(GEDI_) + 10)
    # plt.hist(GEDI_, bins=bin_edges)
    # plt.show()

    plt.figure(figsize=(8, 5), dpi=400)
    plt.bar(x, y1, color="red")
    plt.xlabel('GEDI height', fontsize=20)
    plt.ylabel('Fine data proportion', fontsize=20)
    plt.title(f"Data proportion of pixels differ less than {thd_rate*100}% from Ground Truth")
    plt.show()
    tif.imsave(r'D:\Dataset\0_Lidar\SHENZHEN_rh98_prj_clip_good_pixels.tif', good_map)
    write_json(r'D:\Dataset\0_Lidar\SHENZHEN_GEDI_good_rates.json', rate_dict)
