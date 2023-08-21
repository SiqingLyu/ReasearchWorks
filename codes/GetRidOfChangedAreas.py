import os
import tifffile as tif
import numpy as np
from tools import *

BACKGROUND = 0

def get_var(target, datalist):
    var_data = np.zeros_like(target['masks'][0])
    all_data = np.zeros_like(target['masks'][0])
    for data in datalist:
        all_data += data
    avg_data = all_data/len(datalist)
    for data in datalist:
        var = (data - avg_data) ** 2
        var_data += var
    var_data /= len(datalist)
    return var_data

def get_rid_of_changed_area(var_data, target, label, VAR_THD):
    '''
    inputing a group of data which locate at the same place from different seasons,
    delete the building box if it contains obvious building distruct(from optical var top5%)
    :param datalist: datalist of different seasons
    :param target: containing masks, areas, noses
    :return: new target with changed buildings getting rid of.
    '''


    new_data = np.copy(label)
    for ii in range(len(target['masks'])):
        mask = target['masks'][ii]
        var_this_building = np.mean(var_data[mask])
        if var_this_building > VAR_THD:
            print()
            new_data[mask] = BACKGROUND
    return new_data

def get_all_var(file_path):


if __name__ == '__main__':
    save_path = r''
    root_path = r'E:\实验数据\SEASONet\Data\image'
    file_paths, filenames = []
    seasons = ['spring', 'summer', 'fall', 'winter']

    VAR_THD, all_vars = get_all_var()

    for ii in range(len(filenames)):
        lab_path = r''
        file_paths = []
        file_paths.append(os.path.join(root_path, 'optical'))
        for season in seasons:
            file_paths.append(os.path.join(root_path, 'season', season))

        var_data = all_vars[ii]
        label = tif.imread(lab_path)
        target = get_target(lab_path)
        lab_ridof = get_rid_of_changed_area(var_data)
