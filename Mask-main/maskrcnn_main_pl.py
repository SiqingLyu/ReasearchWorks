# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import os
# os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID" # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"]="0,1"
GPU = [0]

# %% run_control={"marked": false} code_folding=[9, 13]
import matplotlib
matplotlib.use('agg')
import sys
import torchvision
import torch
from torch.utils.data import DataLoader
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
from torchvision.utils import make_grid

import pytorch_lightning as pl
from pytorch_lightning import loggers
from pytorch_lightning import trainer
sys.path.append('/home/dell/lsq/LSQNetModel')
sys.path.append('/home/dell/lsq/LSQNetModel/Mask-main')

from models.detection import *
from models.detection.faster_rcnn import FastRCNNPredictor
from models.detection.mask_rcnn import MaskRCNNPredictor
from detection_utils import *

# %% code_folding=[5, 16, 20, 31, 44]
from torchvision.ops import MultiScaleRoIAlign
import torch.nn as nn
import torch.nn.functional as F
from types import MethodType

class nos_head(nn.Module):
    def __init__(self, in_channels, representation_size):
        super(nos_head, self).__init__()
        self.fc6 = nn.Linear(in_channels, representation_size)
        self.fc7 = nn.Linear(representation_size, representation_size)
    def forward(self, x):
        x = x.flatten(start_dim=1)
        x = F.relu(self.fc6(x))
        x = F.relu(self.fc7(x))
        return x

class nos_predictor(nn.Module):
    def __init__(self, in_channels):
        super(nos_predictor, self).__init__()
        self.nos_predict_end = nn.Linear(in_channels, 1)
    def forward(self, x, nos_proposals):
        if x.dim() == 4:
            assert list(x.shape[2:]) == [1, 1]
        x = x.flatten(start_dim=1)
        nos = self.nos_predict_end(x)
        boxes_per_image = [len(l) for l in nos_proposals]
        nos_list = nos.split(boxes_per_image, dim=0)
        return nos_list

def metadata_block(self, predict, fname):
    return predict
def nos_loss(self, gt_nos, nos_predict, fname):
    nos_list = [self.metadata_block(n, f) for n, f in zip(nos_predict, fname)]
    gt_nos = torch.cat(gt_nos)
    pre_nos = torch.cat(nos_list)
    has_nos = gt_nos != 0
    assert has_nos.any()
    storey_loss = F.smooth_l1_loss(pre_nos.squeeze()[has_nos], 
        gt_nos[has_nos],
        reduction="sum"
    )
    storey_loss = storey_loss / (has_nos.sum()+0.00001)
    return storey_loss

class mask_rcnn(detection_base): 
    def set_model(self):
        faster_rcnn_kargs = {
            'box_nms_thresh':0.3,
            'box_score_thresh':0.5
            #'box_fg_iou_thresh':0.7,
            #'box_bg_iou_thresh':0.7
        }
        self.main_model = maskrcnn_resnet50_fpn(pretrained=True, **faster_rcnn_kargs)
        in_features = self.main_model.roi_heads.box_predictor.cls_score.in_features
        # replace the pre-trained head with a new one
        self.main_model.roi_heads.box_predictor = FastRCNNPredictor(in_features, 2)

        # now get the number of input features for the mask classifier
        in_features_mask = self.main_model.roi_heads.mask_predictor.conv5_mask.in_channels
        hidden_layer = self.main_model.roi_heads.mask_predictor.conv5_mask.out_channels
        # and replace the mask predictor with a new one
        self.main_model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask,
                                                           hidden_layer,
                                                           2)
        #层数预测分支
        self.main_model.roi_heads.nos_roi_pool = MultiScaleRoIAlign(
                featmap_names=['0', '1', '2', '3'],
                output_size=7,
                sampling_ratio=2)
        representation_size = 1024
        resolution = self.main_model.roi_heads.nos_roi_pool.output_size[0]
        self.main_model.roi_heads.nos_head = nos_head(self.main_model.backbone.out_channels * resolution ** 2, representation_size)
        self.main_model.roi_heads.nos_predictor = nos_predictor(representation_size)
        self.main_model.roi_heads.nos_loss = MethodType(nos_loss, self.main_model.roi_heads)
        self.main_model.roi_heads.metadata_block = MethodType(metadata_block, self.main_model.roi_heads)
       
    def sample_step_end(self, variables):
        return 


# %% code_folding=[] run_control={"marked": false}
model_hparams = dict(
    batch_size = 16,
    shuffle = False,
    workers = 4,
    lr = 0.0001,
    nos_task = True,
    label_is_nos = True,
    data_path = '/media/dell/shihaoze/lsq/52City/V2/ImgSeason_SR_01'
)
trainer_hparams = dict(
    #fast_dev_run = True,
    #train_percent_check = 1.0,
    #val_percent_check = 0.01,
    #overfit_pct = 0.005,
    #amp_level='O1',
    #precision=16,
    #auto_lr_find=True,
    check_val_every_n_epoch = 1,
    gpus = GPU,
    max_epochs = 2000,
    num_sanity_val_steps = 2,
    row_log_interval = 100,
    progress_bar_refresh_rate = 1,
    weights_summary = None,
    gradient_clip_val= 5.0,
    gradient_clip_algorithm = "norm"
)
model_hparams.update(trainer_hparams)
model = mask_rcnn(model_hparams)
# if torch.cuda.device_count() > 1:
#     model = torch.nn.DataParallel(model, device_ids=range(torch.cuda.device_count()))
# model.to(torch.device('cuda'))
trainer = pl.Trainer(**trainer_hparams)
# %% [markdown]
# ### 训练

# %% editable=false deletable=false run_control={"frozen": true}
trainer.fit(model)

# %% [markdown]
# ### 预测

# %%
trainer.test(model, model.val_dataloader())
