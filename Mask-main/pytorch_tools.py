import torch
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import pytorch_lightning as pl
import os
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
from torchvision.utils import make_grid

from collections import OrderedDict
#解决 RuntimeError: received 0 items of ancdata
torch.multiprocessing.set_sharing_strategy('file_system')


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

def to_numpy(contain):
    if isinstance(contain, (list,tuple,map)):
        return [i.cpu().numpy() if isinstance(i, torch.Tensor) else i for i in contain ]
    if isinstance(contain, torch.Tensor):
        return contain.cpu().numpy()
    return np.array(contain)

def to_cpu(contain):
    if isinstance(contain, (list,tuple,map)):
        return [i.cpu() for i in contain if isinstance(i, torch.Tensor)]


def make_log(pre,loc,*args):
    '''pre为前缀字符串，如't_',loc应始终传入locals()'''
    d = OrderedDict()
    for i in args:
        for k,v in loc.items():
            if i is v:
                d[pre+k] = v
                break
    return d


class pl_model_base(pl.LightningModule):
    def __init__(self, hparams):
        super(pl_model_base, self).__init__()
        self.hparams = hparams
        self.batch_size = hparams['batch_size']
        self.shuffle = hparams['shuffle']
        self.workers = hparams['workers']
        self.train_dataset, self.valid_dataset = self.get_dataset()
        self.set_model()
        self.init_end()

    def init_end(self):
        return





    def train_dataloader(self):
        return DataLoader(
        self.train_dataset,
        batch_size=self.batch_size,
        num_workers=self.workers,
        collate_fn = self.train_dataset.collate_fn,
        pin_memory=False,
        shuffle=self.shuffle)
    def val_dataloader(self):
        return DataLoader(
        self.valid_dataset,
        batch_size=self.batch_size,
        num_workers=self.workers,
        collate_fn = self.train_dataset.collate_fn,
        pin_memory=False,
        shuffle=False)
    def set_model(self):
        pass
    def set_dataset(self):
        pass
