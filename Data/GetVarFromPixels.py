'''
此代码用于获取影像上的方差
为了方便计算，将影像分块，分块大小可以通过times进行设置
'''
from tools import make_dir,file_name_tif
import numpy as np
import math
import time
from tqdm import tqdm
import os
import tifffile as tif
from LabelTargetProcessor import LabelTarget

def main(path, save):
    tif_data = tif.imread(path)
    times = 100
    print(f'ImgSize: {tif_data.shape[1]} * {tif_data.shape[0]}')
    width = tif_data.shape[1]
    height = tif_data.shape[0]

    width_new = np.floor(width / times).astype(np.uint8)
    height_new = np.floor(height / times).astype(np.uint8)
    print(f'New ImgSize: {width_new} * {height_new}')
    var_data = np.zeros((height_new, width_new))
    # print(var_data)
    for i in range(height_new):
        for j in range(width_new):
            temp_data = tif_data[i*times: (i+1)*times, j*times: (j+1)*times]
            # print(temp_data)
            if np.any(temp_data>0):
                pixels = LabelTarget(label_data=temp_data)
                pixels.to_target_cpu()
                buildings = pixels.target['nos']
                var_data[i][j] = np.var(buildings)
    print(var_data)
    tif.imsave(save, var_data)
if __name__ == '__main__':
    cities = ["Qingdao", "Xuzhou", "Shenyang", "Zhuhai", "Wuxi", "Changsha"]
    for city in cities:

        path = rf'D:\Dataset\@62allcities\Label_bk0_nodata0\{city}.tif'
        save = path[: -4] + '_var1000m.tif'
        main(path, save)