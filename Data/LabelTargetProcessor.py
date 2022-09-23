"""
Date: 2022.9.22
Author: Lv
this class aims to create a class which contains all the operation on Labels
Last coded date: 2022.9.23
"""
import bbox_visualizer as bbv
from skimage.measure import label, regionprops
import numpy as np
from numpy import ndarray
import torch
import os
from typing import Optional
import cv2
# import sys
# sys.path.append('/media/dell/shihaoze/lsq/LSQNetModel')
from pytorch_tools import detach_all
from tools import make_dir


class LabelTarget:
    def __init__(self,
                 label_data: Optional[ndarray, list] = None,
                 target_data: Optional[ndarray, list] = None):
        super(LabelTarget, self).__init__()
        assert label_data is None and target_data is None, 'Must input some Data!'
        self.label = label_data
        self.target = target_data

    def from_target(self, background: int = 0):
        """
        get label data from a target
        :param background: default as 0
        :return: mask_all: label as numpy.ndarray
        """
        assert self.target is not None, 'Must input target data to get label'
        target_data = detach_all(self.target)
        data = np.copy(target_data)
        labels = data['labels']
        masks = data['masks']
        imgsize = masks[0].shape[0]
        mask_all = np.zeros((imgsize, imgsize))
        for i in range(len(masks)):
            mask_data = masks[i]
            label_data = labels[i]
            mask_all = np.where(mask_data != background, label_data, mask_all)
        return mask_all

    def to_target(self,
                  file_name: str = '',
                  image_id: Optional[ndarray, list] = None,
                  **kwargs):
        assert self.label is not None, 'Must input label data to get target'
        boxes, masks, labels, areas, noses = self.get_box_mask_value_area(**kwargs)
        assert len(boxes) > 0
        target = {
            'boxes': torch.FloatTensor(boxes),
            'labels': torch.tensor(labels, dtype=torch.int64),
            'masks': torch.tensor(masks, dtype=torch.uint8),
            'area': torch.FloatTensor(areas),
            'iscrowd': torch.tensor([0] * len(boxes)),
            'image_id': torch.tensor(image_id),
            'nos': torch.FloatTensor(noses),
            'file_name': file_name,
        }
        return target

    def target_to_device(self):
        assert self.target is not None, 'No target data found!'
        
    def get_box_mask_value_area(self,
                                area_thd: int = 4,
                                mask_mode: str = 'value',
                                background: int = 0,
                                label_is_value: bool = False):
        """
        use skimage.measure to get boxes, masks and the values, the areas of them
        :param label_is_value:
        :param background: background value of the image
        :param area_thd: objects whose area is below area_thd will be discard
        :param mask_mode: whether to connect pixels by 'is not background' or values
        :return: Boxes, Masks, Labels, Areas, all in array type
        """
        assert mask_mode in ['value', '01'], 'mask_mode must in [value, 01]'
        data = np.copy(self.label)
        value_region = label(data, connectivity=2, background=background)
        boxes, masks, labels, areas, nos_list = [], [], [], [], []
        for region in regionprops(value_region):
            if region.area < area_thd: continue
            # region.bbox垂直方向为x， 而目标检测中水平方向为x
            y_min, x_min, y_max, x_max = region.bbox
            boxes.append([x_min, y_min, x_max, y_max])
            m = value_region == region.label
            # 取众数
            value = np.bincount(data[m]).argmax()
            nos_list.append(value)
            masks.append(m)
            labels.append(value if label_is_value else 1)
            areas.append(region.area)
        if len(boxes) == 0:
            return None, None, None, None
        assert background not in labels
        masks = np.array(masks)
        if mask_mode is '01':
            masks = np.where(masks, 1, 0)
        return np.array(boxes), masks, np.array(labels), np.array(areas), np.array(nos_list)

    def draw_target_on_image(self,
                             values_pred: ndarray,
                             img_path: str = ''):
        assert os.path.isfile(img_path) is True, 'img_path must be a file path!'
        assert self.target is not None, 'Must initial with a target!'
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        target_data = detach_all(self.target)
        boxes = target_data['boxes']
        values_gt = target_data['nos']
        box_color = (255, 0, 255)
        plot_labels = []
        for i in range(len(boxes)):
            gt = str(values_gt[i])
            pred = str(values_pred[i])
            plot_label = ' ' + gt + ' | ' + pred + ' '
            plot_labels.append(plot_label)
        img = bbv.draw_multiple_rectangles(img,
                                           boxes,
                                           bbox_color=box_color,
                                           thickness=3)
        img = bbv.add_multiple_labels(img,
                                      plot_labels,
                                      boxes,
                                      text_bg_color=box_color,
                                      text_color=(0, 0, 0))
        return img

    def save_targetdraw_image(self,
                              save_path: str,
                              **kwargs):
        make_dir(save_path)
        img = self.draw_target_on_image(**kwargs)
        cv2.imwrite(save_path, img)
