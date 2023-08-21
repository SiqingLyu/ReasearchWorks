from LabelTargetProcessor import LabelTarget
from tools import *

citynames = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
             'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
             'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
             'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
             'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
            'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan'] #]  # 'Shenyang',
# citynames = ['Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
#              'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai', 'Changsha', 'Huizhou', 'Lanzhou', 'Luoyang']
citynames = ['Sanya', 'Haikou', 'Aomen', 'Xianggang', 'Zhongshan', 'Shenzhen', 'Dongguan', 'Foshan', 'Nanning', 'Shantou', 'Guangzhou', 'Xiamen', 'Quanzhou', 'Kunming', 'Fuzhou', 'Guiyang', 'Wenzhou', 'Nanchang', 'Taizhou', 'Ningbo', 'Hangzhou', 'Lasa', 'Chongqing', 'Wuhan', 'Chengdu', 'Shanghai', 'Suzhou', 'Changzhou', 'Hefei', 'Nanjing', 'Yangzhou', 'Xian', 'Zhengzhou', 'Jinan', 'Xining', 'Taiyuan', 'Shijiazhuang', 'Yinchuan', 'Baoding', 'Tianjin', 'Eerduosi', 'Dalian', 'Tangshan', 'Beijing', 'Huhehaote', 'Changchun', 'Haerbin']
citynames = ['Zhuhai', 'Huizhou', 'Changsha', 'Jinhua', 'Shaoxing', 'Jiaxing', 'Wuhu', 'Wuxi', 'Nantong', 'Luoyang', 'Xuzhou', 'Lanzhou', 'Qingdao', 'Shenyang']

def num_floors_statistic(filepath, level=[], cities = []):
    levels_all = np.zeros(len(level))
    areas_all = np.zeros(len(level))
    for city in cities:
        file_paths, file_names = file_name_tif(filepath)
        labels = np.array([])
        areas = np.array([])
        for ii in range(len(file_paths)):
            file_path = file_paths[ii]
            file_city = file_names[ii].split('_')[0]
            if file_city != city:
                continue
            data = LabelTarget(label_data=tif.imread(file_path))
            label = np.array(data.to_target_cpu()['nos'])
            area = np.array(data.to_target_cpu()['area'])
            labels = np.concatenate((labels, label), axis=0)
            areas = np.concatenate((areas, area), axis=0)
        if len(labels) < 1 :
            continue
        leveled_sumfloors = []
        leveled_sumareas = []
        leveled_sumvars = []
        for i in range(len(level) - 1):
            sum_thislevel = 0
            sum_thislevel_area = 0
            sum_thislevel_floor = []

            from_ = level[i]
            to_ = level[i + 1]
            for n in range(len(labels)):
                floor = labels[n]
                if from_ <= floor < to_:
                    sum_thislevel += 1
                    sum_thislevel_floor.append(floor)
                    sum_thislevel_area += areas[n]
            leveled_sumvars.append(np.var(np.array(sum_thislevel_floor)))
            leveled_sumfloors.append(sum_thislevel)
            leveled_sumareas.append(sum_thislevel_area)
            levels_all[i] += sum_thislevel
            areas_all[i] += sum_thislevel_area
        floor_sum_rate = []
        area_sum_rate = []
        for level_floor in leveled_sumfloors:
            rate = level_floor/np.array(leveled_sumfloors).sum()
            floor_sum_rate.append(rate)
        for level_area in leveled_sumareas:
            rate = level_area/np.array(leveled_sumareas).sum()
            area_sum_rate.append(rate)
        print(f'city:{city}, Floor: level sums: {leveled_sumfloors}, level rate: {floor_sum_rate}, '
              f'\nArea: level sums: {leveled_sumareas}, level rate: {area_sum_rate}, '
              f'\nVAR: level vars: {leveled_sumvars}')
    print('============ALL CITIES:===========')

    for i in range(len(level) - 1):
        print(f'------Floor-----\nLevel{i}: sums:{levels_all[i]}, rate:{levels_all[i] / levels_all.sum()}')
        print(f'------Area-----\nLevel{i}: sums:{areas_all[i]}, rate:{areas_all[i] / areas_all.sum()}')


def num_floors_mean(filepath, cities = []):
    for city in cities:
        file_paths, file_names = file_name_tif(filepath)
        labels = np.array([])
        for ii in range(len(file_paths)):
            file_path = file_paths[ii]
            file_city = file_names[ii].split('_')[0]
            if file_city != city:
                continue
            data = LabelTarget(label_data=tif.imread(file_path))
            label = np.array(data.to_target_cpu()['nos'])
            labels = np.concatenate((labels, label), axis=0)
        if len(labels) < 1 :
            continue
        mean_floors = np.mean(labels)
        building_sum = len(labels)
        print(f'city:{city}, building sums: {building_sum}, mean floors: {mean_floors}')


if __name__ == '__main__':
    filepath = r'D:\PythonProjects\DataProcess\Data\Label_all'
    level = np.arange(1,31)
    # level = [1,6,11,16,21,1000]
    level = [0, 7, 14, 10000]
    # level = [0, 3, 16, 10000]
    # cities = ['Qingdao', 'Shenyang', 'Wuxi', 'Huizhou', 'Changsha', 'Zhuhai',
    #           'Jinhua', 'Shaoxing', 'Jiaxing', 'Wuhu', 'Nantong', 'Luoyang',
    #           'Xuzhou', 'Lanzhou']
    cities = [ 'Shenyang', 'Qingdao', 'Wuxi',  'Changsha', 'Huizhou']
    num_floors_statistic(filepath, level, cities)
    # num_floors_mean(filepath, citynames)
    # print(leveled_sumfloors, '\n', floor_sum_rate)