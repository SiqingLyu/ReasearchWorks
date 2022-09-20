# -*- coding: UTF-8 -*-
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
import sys
sys.path.append('/media/dell/shihaoze/lsq/LSQNetModel')
sys.path.append('/media/dell/shihaoze/lsq/LSQNetModel/Mask-main')
# sys.setrecursionlimit(1000)
from torch.utils import data
from models import get_model
from utils import get_logger
from torch.autograd import Variable
import math
from tensorboardX import SummaryWriter #change tensorboardX
from dataloaders.dataloaders import *
from Data.tools import *
# from pytorch_tools import *
import torch.nn.functional as F
# from segmentation_models_pytorch_revised import DeepLabV3Plus
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['CUDA_LAUNCH_BLOCKING'] = '0'

def add(num1, num2):
    return num1 + num2

def detach_all(contain):
    if isinstance(contain, dict):
        ret = {}
        for k, v in contain.items():
            if hasattr(v, 'grad_fn') and v.grad_fn:
                ret[k] = v.detach()
            else:
                ret[k] = v
    return ret
def dict_to_arr(dict_):
    result = dict_.items()  # 此处可根据情况选择.values or .keys
    data = list(result)
    numpyArray = np.array(data)
    return numpyArray
def main(cfg, writer, logger):

    # Setup seeds
    torch.manual_seed(cfg.get("seed", 33))
    torch.cuda.manual_seed(cfg.get("seed", 33))
    np.random.seed(cfg.get("seed", 33))
    random.seed(cfg.get("seed", 33))
    # Setup device
    device = torch.device(cfg["training"]["device"])
    # Setup Dataloader
    data_path = cfg["data"]["path"]
    batch_size = cfg["training"]["batch_size"]
    epochs = cfg["training"]["epochs"]
    shuffle = cfg['training']['shuffle']

    # Load dataset
    trainimg, trainlab, traintar, valimg, vallab, valtar, _, _, _ = make_dataset(data_path, split=[0.8, 0.1, 0.1])
    train_dataset = MaskRcnnDataloader(trainimg, trainlab, traintar, augmentations=True, area_thd=4,
                                       label_is_nos=cfg['data']['label_is_nos'], footprint_mode=True)
    val_dataset = MaskRcnnDataloader(valimg, vallab, valtar, augmentations=False, area_thd=4,
                                     label_is_nos=cfg['data']['label_is_nos'],footprint_mode=True)
    traindataloader = torch.utils.data.DataLoader(
        train_dataset,batch_size=batch_size, shuffle=shuffle, num_workers=4, pin_memory=True, collate_fn=train_dataset.collate_fn)
    evaldataloader = torch.utils.data.DataLoader(
        val_dataset,batch_size=batch_size, shuffle=shuffle, num_workers=8, pin_memory=True, collate_fn=val_dataset.collate_fn)

    # Setup Model
    model = get_model(cfg, Maskrcnn=True).to(device)
    # if torch.cuda.device_count() > 1:
    #     model = torch.nn.DataParallel(model, device_ids=range(torch.cuda.device_count()))

    # print the model
    start_epoch = 0
    resume = cfg["training"]["resume"]
    if os.path.isfile(resume):
        print("=> loading checkpoint '{}'".format(resume))
        checkpoint = torch.load(resume)
        model.load_state_dict(checkpoint['state_dict'])
        # optimizer.load_state_dict(checkpoint['optimizer'])
        print("=> loaded checkpoint '{}' (epoch {})"
                 .format(resume, checkpoint['epoch']))
        start_epoch = checkpoint['epoch'] + 1
    else:
        print("=> no checkpoint found at resume")
        print("=> Will start from scratch.")

    # get all parameters (model parameters + task dependent log variances)
    params = [p for p in model.parameters()]
    print('Number of model parameters: {}'.format(sum([p.data.nelement() for p in model.parameters()])))
    # optimizer = torch.optim.Adam(params, lr=cfg["training"]["lr"], betas=(0.9, 0.999))
    optimizer = torch.optim.SGD(params, lr=cfg["training"]["lr"], momentum=0.9)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
    train_log = []
    Nan_files = []
    torch.autograd.set_detect_anomaly(True)
    for epoch in range(epochs-start_epoch):
        model.on_epoch_start()
        epoch = start_epoch + epoch

        print('===========================TRAINING================================')
        # train
        model.train()
        train_loss = list()
        loss_classifier ,loss_box_reg, loss_nos, loss_mask, loss_objectness, loss_rpn_box_reg = [],[],[],[],[],[]
        step = 0
        for img, target in tqdm.tqdm(traindataloader):
            step += 1
            if step >= 5:  #  warm-up
                with torch.autograd.profiler.profile(enabled=True, use_cuda=True, record_shapes=False) as prof:
                    img = torch.tensor([item.cpu().detach().numpy() for item in img]).cuda()
                    batch = img, target
                    loss_dict = model.forward(batch)
                    loss_nos.append(loss_dict['loss_nos'].cpu().detach().numpy())
                    loss_values = loss_dict.values()
                    loss_values = list(loss_values)
                    for i in range(len(loss_values)):
                        if loss_values[i] != loss_values[i]:
                            print('Here is a NaN loss item:', loss_values[i])
                            loss_values[i] = torch.tensor(0.).cuda()
                    loss = reduce(add, loss_values)
                    train_loss.append(loss.cpu().detach().numpy())
                    train_log.append(loss_dict)
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    print('train loss: ', loss.item())
                print(prof.table())
                prof.export_chrome_trace('./MaskRCNN_profile.json')
            else:
                img = torch.tensor([item.cpu().detach().numpy() for item in img]).cuda()
                # i = 0
                # for item in target:
                #     for key in item:
                #         if type(item[key]) == str:
                #             continue
                #         else:
                #             # print(key)
                #             item[key].cuda()
                #     target[i] = item
                #     i += 1

                batch = img, target
                loss_dict = model.forward(batch)
                # print('=================================-------------------------->',loss_dict)
                # loss_classifier.append(loss_dict['loss_classifier'].cpu().detach().numpy())
                # loss_box_reg.append(loss_dict['loss_box_reg'].cpu().detach().numpy())
                loss_nos.append(loss_dict['loss_nos'].cpu().detach().numpy())
                # loss_objectness.append(loss_dict['loss_objectness'].cpu().detach().numpy())
                # loss_mask.append(loss_dict['loss_mask'].cpu().detach().numpy())
                # loss_rpn_box_reg.append(loss_dict['loss_rpn_box_reg'].cpu().detach().numpy())

                loss_values = loss_dict.values()
                loss_values = list(loss_values)
                for i in range(len(loss_values)):
                    if loss_values[i] != loss_values[i]:
                        print('Here is a NaN loss item:', loss_values[i])
                        loss_values[i] = torch.tensor(0.).cuda()
                loss = reduce(add, loss_values)
                if math.isnan(loss.item()):
                    print(loss_dict)
                    assert loss_dict == loss_dict
                train_loss.append(loss.cpu().detach().numpy())
                train_log.append(loss_dict)
                optimizer.zero_grad()
                loss.backward()


                optimizer.step()
                print('train loss: ', loss.item())

        # eval
        print('==========================VALIDATING===============================')
        model.eval()
        val_outs = []
        with torch.no_grad():
            for img, target in tqdm.tqdm(evaldataloader):
                img = torch.tensor([item.cpu().detach().numpy() for item in img]).cuda()
                batch = img, target
                out = model.validation_step(batch)
                val_outs.append(out)
            result = model.validation_epoch_end(val_outs)
        val_loss = result['val_loss'].cpu().detach().numpy()
        val_log = result['log']
        print('val loss:', val_loss, '\nlog info :\n', val_log)

        # scheduler step
        scheduler.step()

        # save models
        if epoch % 2 == 0: # every five internval
            savefilename = os.path.join(logdir, 'finetune_'+str(epoch)+'.tar')
            torch.save({
                'epoch': epoch,
                'state_dict': model.state_dict(),
                'train_loss': np.nanmean(train_loss),
                'eval_loss': np.nanmean(val_loss), #*100
                # 'classifier_loss': np.nanmean(loss_classifier),
                # 'loss_box_reg':np.nanmean(loss_box_reg),
                'loss_nos': np.nanmean(loss_nos),
                # 'loss_objectness': np.nanmean(loss_objectness),
                # 'loss_mask': np.nanmean(loss_mask),
                # 'loss_rpn_box_reg': np.nanmean(loss_rpn_box_reg),
                # 'MAE_all': val_log['MAE_all'].cpu().detach().numpy(),
                # 'F1_all': val_log['F1_all'].cpu().detach().numpy(),
                # 'R_all': val_log['R_all'].cpu().detach().numpy(),
                'RMSE_all': val_log['RMSE_all'].cpu().detach().numpy(),
                'IoU_NoS_all': val_log['IoU_NoS_all'].cpu().detach().numpy(),
                # 'seg_acc_all': val_log['seg_acc_all'].cpu().detach().numpy(),
                # 'seg_IoU_all': val_log['seg_IoU_all'].cpu().detach().numpy(),

            }, savefilename)
        #

        writer.add_scalar('train loss',
                          (np.nanmean(train_loss)),  # average
                          epoch)
        # writer.add_scalar('classifier_loss', np.nanmean(loss_classifier),  # average
        #                   epoch)
        writer.add_scalar('loss_nos', np.nanmean(loss_nos),  # average
                          epoch)
        writer.add_scalar('MAE_all', val_log['MAE_all'].cpu().detach().numpy(),  # average
                          epoch)
        # writer.add_scalar('F1_all', val_log['F1_all'].cpu().detach().numpy(),  # average
        #                   epoch)
        # writer.add_scalar('res_rel', val_log['res_rel_all'].cpu().detach().numpy(),  # average
        #                   epoch)
        # writer.add_scalar('R_all', val_log['R_all'].cpu().detach().numpy(),  # average
        #                   epoch)
        writer.add_scalar('RMSE_all', val_log['RMSE_all'].cpu().detach().numpy(),  # average
                          epoch)
        writer.add_scalar('IoU_NoS_all', val_log['IoU_NoS_all'].cpu().detach().numpy(),  # average
                          epoch)
        writer.add_scalar('val loss',
                          val_loss, #average
                          epoch)
        writer.close()




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

    logdir = os.path.join("/media/dell/shihaoze/lsq/LSQNetModel/runs", os.path.basename(args.config)[:-4], "V12_connectasvalue")
    # make_dir(logdir)
    writer = SummaryWriter(log_dir=logdir)

    print("RUNDIR: {}".format(logdir))
    shutil.copy(args.config, logdir)

    logger = get_logger(logdir)
    logger.info("here begin the log")

    main(cfg, writer, logger)
