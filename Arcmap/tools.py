import numpy as np
import os

def get_range(x):
    ma = np.max(x)
    mi = np.min(x)
    return mi, ma


def cal_rmse(y_true, ypred):
    diff=y_true.flatten()-ypred.flatten()
    return np.sqrt(np.mean(diff*diff))


def make_dir(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)
    return path


def Normalize(array):
    '''
    Normalize the array
    '''
    mx = np.nanmax(array)
    mn = np.nanmin(array)
    t = (array-mn)/((mx-mn))
    return t


def file_name_tif(file_dir):
    '''
    eg: Listfile, allFilename = file_name(r'/www/lsq/optical')
    only record tif files
    :param file_dir: str
    :return: two List: a list of file absolute path & a list of file with no suffix
    '''
    if (os.path.isdir(file_dir)):
        L = []
        allFilename = []
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if file.split('.')[-1] != 'tif':
                    continue
                formatName = os.path.splitext(file)[1]
                fileName = os.path.splitext(file)[0]
                allFilename.append(fileName)
                if (formatName == '.tif'):
                    tempPath = os.path.join(root, file)
                    L.append(tempPath)
        return L, allFilename
    else:
        print('must be folder path')