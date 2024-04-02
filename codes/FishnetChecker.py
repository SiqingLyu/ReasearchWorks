import tifffile as tif
from tools import *
import os
import numpy as np
import shapefile as shpf


class CBRA_Fishnet:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = shpf.Reader(file_path, encoding='utf-8')

    def get_bboxes(self):
        net_num = len(self.data.records())
        bboxes = []
        for ii in range(net_num):
            shapes = self.data.shape(ii)
            bbox = shapes.bbox
            bboxes.append(bbox)
        return bboxes


if __name__ == '__main__':
    C = CBRA_Fishnet(file_path=r'D:\画图\四大地理区域\Beifang_fishnet_2p5.shp')
    bboxes = C.get_bboxes()
    print(bboxes)
    print(bboxes[0][1] +2.5 == bboxes[0][3])
