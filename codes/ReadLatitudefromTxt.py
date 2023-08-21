import shutil

from tools import *
import pandas as pd
import numpy as np

citynames = ['北京市', '南京市', '天津市', '广州市',
             '重庆市', '哈尔滨市', '杭州市', '昆明市',
             '南昌市', '上海市', '深圳市', '武汉市',
             '厦门市', '西安市', '郑州市',
             '澳门', '保定市', '长春市', '长沙市',
             '常州市', '成都市', '大连市', '东莞市',
             '鄂尔多斯市', '佛山市', '福州市', '贵阳市',
             '海口市', '合肥市', '呼和浩特市', '惠州市',
             '济南市', '兰州市', '拉萨市', '洛阳市',
             '南宁市', '宁波市', '泉州市', '三亚市',
             '汕头市', '石家庄市', '苏州市', '太原市',
             '台州市', '唐山市', '温州市', '香港',
             '西宁市', '扬州市', '银川市', '中山市',
             '嘉兴市', '金华市', '南通市', '青岛市',
             '绍兴市', '沈阳市', '无锡市', '芜湖市',
             '徐州市', '珠海市'
             ]
citynames_en = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
             'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
             'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
             'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
             'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
             'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan',
             'Jiaxing', 'Jinhua', 'Nantong', 'Qingdao', 'Shaoxing', 'Shenyang',
             'Wuxi', 'Wuhu', 'Xuzhou', 'Zhuhai'
             ]
citynames_test = ['西宁市', '扬州市', '银川市', '惠州市',
             '嘉兴市', '金华市', '南通市', '青岛市',
             '绍兴市', '沈阳市', '无锡市', '芜湖市',
             '徐州市', '珠海市']
print(len(citynames), len(citynames_test))

Lat_sections = np.arange(11.3, 52, 2.5)
Lon_sections = np.arange(73.5, 134, 2.5)
path = r'D:\Data\SEASONet\Citipoints.txt'
df = pd.read_table(path, sep = ',')
# print(np.array(df['roi_if']))
print(df.keys())
names = np.array(df['city_name'])
# print(names)
roi_ifs = np.array(df['roi_if'])
test_if = np.array(df['test_if'])
longitudes = np.array(df['x'])
latitudes = np.array(df['y'])
assert len(longitudes) == len(latitudes)
cities_sections = []
for i in range(len(Lat_sections)):
    for j in range(len(Lon_sections)):
        cities_sections.append([])
for ii in range(len(names)):
    name = names[ii]
    latitude = latitudes[ii]
    longitude = longitudes[ii]
    roi_if = roi_ifs[ii]
    if roi_if == 2 or roi_if == 1:
        if name in citynames:
            for jj in range(len(Lat_sections) - 1):
                if latitude >= Lat_sections[jj] and latitude < Lat_sections[jj + 1]:
                    for ll in range(len(Lon_sections) - 1):
                        if longitude >= Lon_sections[ll] and longitude < Lon_sections[ll + 1]:
                            kk = citynames.index(name)
                            name_en = citynames_en[kk]
                            cities_sections[jj*(len(Lon_sections) - 1)+ll].append([name_en, longitude, latitude, Lat_sections[jj+1], Lon_sections[ll]])

cities_sections_new = []
years = [2017, 2018, 2019, 2020, 2021]
for year in years:
    for item in cities_sections:
        if len(item) > 0:
            cities_sections_new.append(item[0])
            city_file_name = ''
            for i in range(len(item)):
                city_file_name = city_file_name + item[i][0]
            save_path = rf'F:\实验数据\Zeping5YearsBuildings\{year}\{city_file_name}'
            make_dir(save_path)
            target_file = rf'E:\result_all\result{year}\CBRA_{year}_E{item[0][-1]}_N{item[0][-2]}.tif'
            shutil.copy(target_file, os.path.join(save_path, f'CBRA_{year}_E{item[0][-1]}_N{item[0][-2]}.tif'))
            print(item, save_path, target_file)

print(cities_sections_new)
a=np.array(cities_sections_new)
np.save('D:\Data\SEASONet\City_latitudes.npy', cities_sections_new) # 保存为.npy格式