import os
import shutil
from tools import file_name_tif
from tools import make_dir

citynames = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
             'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
             'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
             'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
             'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
            'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan',  #]  # 'Shenyang',
             'Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
             'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Changsha', 'Huizhou', 'Lanzhou', 'Luoyang'
             ]
print(len(citynames))
def main(work_dir):
    file_paths, file_names = file_name_tif(work_dir)
    for ii in range(len(file_names)):
        filename = file_names[ii]
        filepath = file_paths[ii]
        print(filepath, filename)
        filecity = filename.split('_')[0]
        if filecity in citynames:
            city_dir = os.path.join(work_dir, filecity)
            make_dir(city_dir)
            new_filepath = os.path.join(city_dir, filename+'.tif')
            shutil.move(filepath, new_filepath)

if __name__ == '__main__':
    dir = r'D:\experiment\results\Version1.0-Mask\Maskres50_result_V3.8Buffer21_leftright0_15city_64\Assigned'
    main(dir)
