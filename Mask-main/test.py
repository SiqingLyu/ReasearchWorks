'''
用于训练img + season + vvh三分支Unet模型


'''

import os

import yaml
import shutil
import torch
import random
import argparse
import numpy as np
from tqdm import tqdm
from functools import reduce
import copy
import sys
sys.path.append('/media/dell/shihaoze/lsq/LSQNetModel')
sys.path.append('/media/dell/shihaoze/lsq/LSQNetModel/Mask-main')
from torch.utils import data
from models import get_model
from utils import get_logger
from tensorboardX import SummaryWriter #change tensorboardX
from dataloaders.dataloaders import *
import torch.nn.functional as F
# from segmentation_models_pytorch_revised import DeepLabV3Plus
os.environ['CUDA_VISIBLE_DEVICES']= '1'
from Data.tools import *

def add(num1, num2):
    return num1 + num2


def save_predict(predict, filename, imgsize, save_path):
    mask = np.squeeze(predict['masks'].cpu().detach().numpy())
    labels = predict['labels'].cpu().detach().numpy()
    if len(labels) == 0:
        print("no item found")
        return
    print(mask.shape, labels)
    mask_all = np.zeros(imgsize, imgsize)
    assert len(mask) == len(labels)
    for i in range(len(labels)):
        mask_save = mask[i]
        label_tmp = labels[i]
        mask_all = np.where(mask_save > 0, label_tmp, mask_all)
    tif.imsave(mask_all, os.path.join(save_path, filename+'.tif'))

def main(cfg, writer, logger):

    # Setup seeds
    torch.manual_seed(cfg.get("seed", 1337))
    torch.cuda.manual_seed(cfg.get("seed", 1337))
    np.random.seed(cfg.get("seed", 1337))
    random.seed(cfg.get("seed", 1337))
    # Setup device
    device = torch.device(cfg["training"]["device"])
    # Setup Dataloader
    data_path = cfg["data"]["path"]
    batch_size = cfg["training"]["batch_size"]
    epochs = cfg["training"]["epochs"]
    make_dir(cfg["savepath"])
    # Load dataset
    _, _, _, _, testimg, testlab = make_dataset(data_path, split=[0.8, 0.1, 0.1])
    test_dataset =  MaskRcnnDataloader(testimg, testlab, augmentations=False, area_thd=1, label_is_nos=cfg['data']['label_is_nos'], footprint_mode=True)
    testdataloader = torch.utils.data.DataLoader(test_dataset,
        batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True,collate_fn=test_dataset.collate_fn)

    # Setup Model
    model = get_model(cfg).to(device)
    # if torch.cuda.device_count() > 1:
    #     model = torch.nn.DataParallel(model, device_ids=range(torch.cuda.device_count()))

    # print the model
    resume = cfg["test"]["resume"]
    if os.path.isfile(resume):
        print("=> loading checkpoint '{}'".format(resume))
        checkpoint = torch.load(resume)
        model.load_state_dict(checkpoint['state_dict'])
        # optimizer.load_state_dict(checkpoint['optimizer'])
        print("=> loaded checkpoint '{}' (epoch {})"
                 .format(resume, checkpoint['epoch']))
        start_epoch = checkpoint['epoch']
    else:
        print("=> no checkpoint found at resume")
        print("=> Will start from scratch.")

    model.eval()
    test_outs = []
    with torch.no_grad():
        for img, target in tqdm.tqdm(testdataloader):
            img = torch.tensor([item.cpu().detach().numpy() for item in img]).cuda()
            i = 0
            for item in target:
                for key in item:
                    if type(item[key]) == str:
                        continue
                    else:
                        # print(key)
                        item[key].cuda()
                target[i] = item
                i += 1
            batch = img, target
            out = model.test_step(batch)
            # save_predict(out, target, cfg["data"]["img_rows"], cfg["savepath"])
            test_outs.append(out)
        result = model.test_epoch_end(test_outs)
    val_loss = result['val_loss'].cpu().detach().numpy()
    val_log = result['log']
    print('val loss:', val_loss, '\nlog info :\n', val_log)





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="config")
    parser.add_argument(
        "--config",
        nargs="?",
        type=str,
        default="../configs/MaskRcnn_res50.yml",
        help="Configuration file to use",
    )

    args = parser.parse_args()

    with open(args.config) as fp:
        cfg = yaml.load(fp, Loader=yaml.FullLoader)

    logdir = os.path.join("/media/dell/shihaoze/lsq/LSQNetModel/runs", os.path.basename(args.config)[:-4], "V9_rpnasknown")
    writer = SummaryWriter(log_dir=logdir)

    print("RUNDIR: {}".format(logdir))
    shutil.copy(args.config, logdir)

    logger = get_logger(logdir)
    logger.info("here begin the log")

    main(cfg, writer, logger)
