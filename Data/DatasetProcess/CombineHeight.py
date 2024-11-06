"""
代码旨在使用GABLE, GEDI, CBRA, EA, 3DGloBFP
其中CBRA属于中分建筑物产品，使用的是哨兵影像，存在一定粘连问题
GEDI属于激光雷达产品，获取的是25m圆柱体内最大落差值
其他的产品都是由高分影像得到的，其在高层建筑物这一类别中存在明显的位置偏移
共同得到一个覆盖全国，结合高分和中分建筑物产品各自优势的融合建筑物高度产品
"""
import numpy as np

from tools import *

BACKGROUND = 0


class Combiner:
    """
    这个类应该被用于可以进行连通区域分析的小块patch数据上，而此patch大小也应该与之后的shadow analysis保持一致
    """

    def __init__(self, product_dict):
        self.products = product_dict  # [3DGloBFP, EA, CBRA, GABLE, GEDI]
        self.preprocess()
        self.footprint = None
        self.height = None

    def preprocess(self):
        """
        由于 EA有值区域可能包含0，1，2，而无值区域为255，因此需要将其0，1，2 全部转为 1
        GEDI 则需要将所有小于0的值视为背景
        """
        for product_name in self.products.keys():
            if product_name == "EA":
                EA = self.products[product_name]
                EA[(EA >= 0) & (EA < 255)] = 1
                self.products[product_name] = EA
            if product_name == "CBRA":
                CBRA = self.products[product_name]
                CBRA[CBRA == 255] = 1
                self.products[product_name] = CBRA
            if product_name == "GEDI":
                GEDI = self.products[product_name]
                GEDI[GEDI < 0] = BACKGROUND
                self.products[product_name] = GEDI

            data_ = self.products[product_name]
            data_[data_ == 255] = BACKGROUND
            self.products[product_name] = data_

    def height_combine(self, height_gt=None):
        """
        利用多种建筑物高度产品得到融合建筑物高度数据，此程序应当先于footprint refine执行
        :param height_gt: 如果有部分地区有建筑物的高度真值，则直接使用之，这个就是留给这种情况的接口
        :return: 返回一个融合建筑物高度数据，此数据之后也要被用于footprint refine中
        """
        height_data = np.zeros_like(self.products["CBRA"])
        GABLE = np.copy(self.products["GABLE"])
        GEDI = np.copy(self.products["GEDI"])
        height_data = np.where((GABLE != BACKGROUND) & (GABLE < 24), GABLE, height_data)
        height_data = np.where((GEDI != BACKGROUND) & (GEDI >= 24), GEDI, height_data)
        if height_gt is not None:
            height_data = np.where(height_gt != BACKGROUND, height_gt, height_data)
        self.height = height_data
        return height_data

    def footprint_refine(self, thd=50):
        """
        使用 CBRA为基础，以 3DGloBFP、GABLE、EA为优先级针对低层建筑物进行足迹再定位
        首先找到每个CBRA的联通区，一个联通区内如果有多个其他产品的情况，使用其他的产品替代此足迹
        """
        self.footprint = np.zeros_like(self.products["CBRA"])
        CBRA_targets = LabelTarget(label_data=self.products["CBRA"]).to_target_cpu()
        CBRA_masks, CBRA_areas, CBRA_noses = CBRA_targets["masks"], CBRA_targets["areas"], CBRA_targets["nos"]
        for ii in range(len(CBRA_masks)):  # 对每一个CBRA的建筑物对象，不论是否粘连，进入后续操作；
            CBRA_mask = CBRA_masks[ii]
            CBRA_area = CBRA_areas[ii]
            masked_height = self.height[CBRA_mask]
            if np.max(masked_height) == BACKGROUND:
                # 此处无任何高度数据 则直接从数据中剔除，此后使用尽量覆盖的高度数据时应该不会出现此情况
                CBRA_mask[ii] = None
            else:
                # height_area = len(masked_height[masked_height != BACKGROUND])
                # height_rate = height_area / CBRA_area
                height_max = np.max(masked_height)
                CBRA_noses[ii] = height_max
                if height_max > 20 and CBRA_area < thd:  # 若建筑物本身足够小且其本身高度较高
                    continue
                best_masks = []
                best_values = []

                for p_name in ["3DGloBFP", "GABLE", "EA"]:
                    masked_product = np.where(CBRA_mask, self.products[p_name], BACKGROUND)
                    masked_targets = LabelTarget(label_data=masked_product).to_target_cpu()
                    GF_masks, GF_areas = masked_targets["masks"], masked_targets["areas"]
                    if len(GF_masks) == 0:  # 该产品无数据时直接尝试下一种产品
                        continue
                    if len(best_masks) > 0:  # 之前产品已经有结果了，按照优先级，不再尝试此产品
                        continue
                    # if len(GF_masks) == 1 and (GF_areas[0] / CBRA_area) < 0.1:  # 有其他产品的足迹在此但是占比极少
                    #     continue
                    assert GF_masks[0].shape == CBRA_mask.shape  # 提示一下，这里形状应当是一致的

                    for jj in range(len(GF_masks)):
                        best_masks.append(GF_masks[jj])
                        h = np.max(self.height[GF_masks[jj]])
                        best_values.append(h)
                if len(best_masks) > 0:
                    # 若其他产品具有对应的足迹，使用其他产品数据落在CBRA内的数据，
                    # 由于此前已经规定只有低层建筑物足迹能进入此过程，因此偏移严重情况较少
                    assert len(best_masks) == len(best_values)  # 依然是一个提醒
                    CBRA_masks[ii] = None
                    CBRA_masks += best_masks
                    CBRA_noses += best_values
        New_target = {"mask": CBRA_masks, "nos": CBRA_noses}
        new_footprint_with_height = LabelTarget(target_data=New_target).from_target()
        return new_footprint_with_height






