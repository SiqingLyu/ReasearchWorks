import os, shutil


SingleYears = ['Beijing', 'Changchun', 'Changzhou', 'Dalian', 'Haikou', 'Hangzhou',
               'Haerbin', 'Hefei', 'Hohhot', 'Hongkong', 'Huizhou', 'Jiaxing', 'Jinan',
               'Jinhua', 'Kunming', 'Luoyang', 'Nanchang', 'Nanjing', 'Nantong', 'Ningbo',
               'Qingdao', 'Shanghai', 'Shantou', 'Shaoxing', 'Shenyang', 'Shenzhen',
               'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Tianjin', 'Wenzhou', 'Wuhan',
               'Wuhu', 'Wuxi', 'Xuzhou', 'Yangzhou', 'Yinchuan']

SingleYearTest = ['Hefei', 'Wuxi', 'Tianjin', 'Huizhou', 'Haerbin']

def main(path):
    for (root, dir, files) in os.walk(path):
        for file in files:
            path_tmp = os.path.join(root, file)
            city_name = path_tmp.split('\\')[-1].split('_')[0]
            if city_name not in SingleYears:
                os.remove(path_tmp)
                print('Delete: ', path_tmp)
            if city_name in SingleYearTest:
                path_tar = root.replace('SingleYear', 'SingleYear_Test')
                if not os.path.isdir(path_tar):
                    os.makedirs(path_tar)
                shutil.move(path_tmp, os.path.join(path_tar, file))
                # print(path_tar)

if __name__ == '__main__':
    main(r'E:\实验数据\SEASONet\SingleYear')