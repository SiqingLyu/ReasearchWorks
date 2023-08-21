#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tools import *
citynames = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
             'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
             'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
             'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
             'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
            'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan']# 'Shenyang',


city_infos: dict = {
    'Aomen': 0,
    'Baoding': 0,
    'Beijing': 0,
    'Changchun': 0,
    'Changsha': 0,
    'Changzhou': 0,
    'Chengdu': 0,
    'Chongqing': 0,
    'Dalian': 0,
    'Dongguan': 0,
    'Eerduosi': 0,
    'Foshan': 0,
    'Fuzhou': 0,
    'Guangzhou': 0,
    'Guiyang': 0,
    'Haerbin': 0,
    'Haikou': 0,
    'Hangzhou': 0,
    'Hefei': 0,
    'Huhehaote': 0,
    'Huizhou': 0,
    'Jinan': 0,
    'Jiaxing': 0,
    'Jinhua': 0,
    'Kunming': 0,
    'Lasa': 0,
    'Lanzhou': 0,
    'Luoyang': 0,
    'Nanchang': 0,
    'Nanjing': 0,
    'Nanning': 0,
    'Nantong': 0,
    'Ningbo': 0,
    'Qingdao': 0,
    'Quanzhou': 0,
    'Sanya': 0,
    'Shantou': 0,
    'Shanghai': 0,
    'Shaoxing': 0,
    'Shenzhen': 0,
    'Shenyang': 0,
    'Shijiazhuang': 0,
    'Suzhou': 0,
    'Taizhou': 0,
    'Taiyuan': 0,
    'Tangshan': 0,
    'Tianjin': 0,
    'Wenzhou': 0,
    'Wuxi': 0,
    'Wuhu': 0,
    'Wuhan': 0,
    'Xiamen': 0,
    'Xian': 0,
    'Xining': 0,
    'Xianggang': 0,
    'Xuzhou': 0,
    'Yantai': 0,
    'Yangzhou': 0,
    'Yinchuan': 0,
    'Zhengzhou': 0,
    'Zhongshan': 0,
    'Zhuhai': 0
}


class DataCheck():
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.check_img_files()

    def process_nan(self, data, data_range):
        minvalue, maxvalue = data_range
        data = np.nan_to_num(data)
        return data


    def get_imgpixel_range(self, imgfile):
        imgfile = np.nan_to_num(imgfile)
        imgfile[imgfile<(-3.4028235e+37)] = 0
        imgfile = self.normalize(imgfile)
        return np.max(imgfile),np.min(imgfile)

    def normalize(self, array):
        '''
        Normalize the array
        '''
        mx = np.nanmax(array)
        mn = np.nanmin(array)
        t = (array - mn) / (mx - mn)
        return t

    # def check_img_nobackground(self, imgfile):

    def check_img_files(self):
        filepath_list, filename_list = self.file_name_tif(self.data_folder)
        max_all, min_all = 0, np.inf
        for ii in range(len(filename_list)):
            filename = filename_list[ii]
            filepath = filepath_list[ii]
            filedata = tif.imread(filepath)
            maxpix, minpix = self.get_imgpixel_range(filedata)
            # print(filename, "range:", minpix, maxpix)
            # time.sleep(0.1)
            max_all = max(maxpix, max_all)
            min_all = min(minpix, min_all)
        print('range of all:', min_all, max_all)

            # self.check_img_nobackground(filedata)
    def file_name_tif(self, path):
        '''
        eg: Listfile, allFilename = file_name(r'/www/lsq/optical')
        only for tif files
        :param file_dir: str
        :return: two List: a list of file absolute path & a list of file with no suffix
        '''
        file_dir = path
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

    def get_allzero_image_name(self):
        Listfile, allFilename = self.file_name_tif(self.data_folder)
        names = []
        for ii in range(len(allFilename)):
            tif_filepath = Listfile[ii]
            tif_fileid = allFilename[ii]
            # print('processing: ', tif_fileid)
            img_data = tif.imread(tif_filepath, dtype=np.float32)
            img_data = np.nan_to_num(img_data)
            mx = np.nanmax(img_data)
            mn = np.nanmin(img_data)
            if mx == mn:
                names.append(tif_fileid)
        return names


def city_patches(file_path:str = None):
    file_paths, file_names = file_name_tif(file_path)
    total = 0
    for i in range(len(file_names)):
        total+=1
        file_name = file_names[i]
        # print(file_name)
        for cityname in citynames:
            # print(cityname)
            if file_name.__contains__(cityname):
                city_infos[cityname] += 1
    print(city_infos, '\n', total)

if __name__ == '__main__':
    city_patches(r'D:\PythonProjects\DataProcess\Data\image\optical')
    citynames = ['Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
                  'Wuxi', 'Wuhu', 'Xuzhou', 'Yantai', 'Zhuhai']
    city_patches(r'D:\PythonProjects\DataProcess\Data\Test\image\optical')
    D = DataCheck(data_folder=r'D:\PythonProjects\DataProcess\Data\CNBH\CNBH_height')
    print()