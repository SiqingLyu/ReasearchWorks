from tools import make_dir,file_name_tif
from osgeo import gdal
import numpy as np
import math
import time
from tqdm import tqdm
import os
import tifffile as tif

def main(path):
    tif_data = tif.imread(path)
    print(f'ImgSize: {tif_data.shape[0]} * {tif_data.shape[1]}')
    width = tif_data.shape[1]
    height = tif_data.shape[0]

    width_new = width /



if __name__ == '__main__':
    main(r'D:\experiment\results\BSG_Maskres50_result_V2.3MUX_newscheduler_15city_60\IMG_10\Beijing.tif')