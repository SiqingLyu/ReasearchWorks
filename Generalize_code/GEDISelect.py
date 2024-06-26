"""
本代码目的是将GEDI中像对确定可靠的数据赋值于对应的建筑物对象
从而使其可以用于泛化训练
排除的数据包括：
1. 完全落在某建筑物内部且数值小于5m的数据（针对GEDI的25m内全是屋顶的问题）
    GEDI（25m）转为10m时一般会对应6-9个像素，这里取7个像素
2. 未处于建成区数据（GHSL）内的GEDI数据

理想状态下，此代码将用于dataloader，使得输入模型的GEDI是处理过后的数据
"""
from tools import *
from Data.LabelTargetProcessor import LabelTarget


NODATA = 0


def box1_in_box2(box1, box2):
    """
    box1 和 box2应该是array格式, [x_min, y_min, x_max, y_max]
    """
    x_min1, y_min1, x_max1, y_max1 = box1
    x_min2, y_min2, x_max2, y_max2 = box2
    if (x_min2 < x_min1) & (x_max2 > x_max1) & (y_min2 < y_min1) & (y_max2 > y_max1):
        return True
    else:
        return False


def select_GEDI(GEDI_data, footprint, target=None):
    """
    此代码面向处理一个单个影像情况下选取GEDI的场景
    其中，target来自于footprint
    """
    if target is None:
        target = LabelTarget(label_data=footprint.astype(np.uint8)).to_target_cpu()
    if target is None:
        return None
    # 去掉落在不透水层以外的GEDI
    # GEDI_data[GHSL_data == NODATA] = NODATA
    masks, bboxes, noses = target["masks"], target["boxes"], target["nos"]

    # 去掉落在CBRA以外的的GEDI
    GEDI_data[footprint == NODATA] = NODATA

    # 处理落在建筑物内部的GEDI
    for ii in range(len(masks)):
        mask = masks[ii]
        box = bboxes[ii]
        inter = np.where((mask == 1) & (GEDI_data != NODATA), 1, 0)
        inter_target = LabelTarget(label_data=inter).to_target_cpu()
        masks_in, bboxes_in, heights = inter_target["masks"], inter_target["boxes"], inter_target["nos"]
        # 去掉落在建筑物内部的GEDI
        if box1_in_box2(bboxes_in[0], box) & len(bboxes_in) == 1:
            GEDI_data[masks_in[0] == 1] = NODATA
        # 多个GEDI落在同一个建筑物：将最大高度值赋予所有GEDI
        elif (len(bboxes_in) > 1) and np.max(heights) > 10:
            for mask_in in masks_in:
                GEDI_data[mask_in == 1] = np.max(heights)

    return GEDI_data


