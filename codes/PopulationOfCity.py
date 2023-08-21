citynames = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou',
             'Chongqing', 'Haerbin', 'Hangzhou', 'Kunming',
             'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan',
             'Xiamen', 'Xian', 'Zhengzhou',
             'Aomen', 'Baoding', 'Changchun', 'Changsha',
             'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
             'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang',
             'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
             'Jinan', 'Lanzhou', 'Lasa', 'Luoyang',
             'Nanning', 'Ningbo', 'Quanzhou', 'Sanya',
             'Shantou', 'Shijiazhuang', 'Suzhou', 'Taiyuan',
             'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
             'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan',
             'Jiaxing', 'Jinhua', 'Nantong', 'Qingdao',
             'Shaoxing', 'Shenyang', 'Wuxi', 'Wuhu',
             'Xuzhou', 'Yantai', 'Zhuhai'
             ]
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
             '徐州市', '烟台市', '珠海市'
             ]
def main(city):
    if city in citynames:
        return 1
    else:
        return 0

print(main('重庆市'))
print(len(citynames))
population: dict = {
    'Aomen': 68.84,
    'Baoding': 919.5,
    'Beijing': 2188.6,
    'Changchun': 853.4,
    'Changsha': 1023.9,
    'Changzhou': 535,
    'Chengdu': 2119.2,
    'Chongqing': 3212.4,
    'Dalian': 745.4,
    'Dongguan': 1053.7,
    'Eerduosi': 216.8,
    'Foshan': 961.3,
    'Fuzhou': 842,
    'Guangzhou': 1881.1,
    'Guiyang': 610.2,
    'Haerbin': 988.5,
    'Haikou': 288.7,
    'Hangzhou': 1220.4,
    'Hefei': 946.5,
    'Huhehaote': 349.6,
    'Huizhou': 606.6,
    'Jinan': 933.6,
    'Jiaxing': 551.6,
    'Jinhua': 712,
    'Kunming': 850.2,
    'Lasa': 86.8,
    'Lanzhou': 438.4,
    'Luoyang': 706.9,
    'Nanchang': 643.8,
    'Nanjing': 942.3,
    'Nanning': 883.3,
    'Nantong': 773.3,
    'Ningbo': 954.4,
    'Qingdao': 1025.7,
    'Quanzhou': 885,
    'Sanya': 103.7,
    'Shantou': 553,
    'Shanghai': 2489.4,
    'Shaoxing': 533.7,
    'Shenzhen': 1768.2,
    'Shenyang': 911.8,
    'Shijiazhuang': 1120.5,
    'Suzhou': 1284.8,
    'Taizhou': 666.1,
    'Taiyuan': 539.1,
    'Tangshan': 769.7,
    'Tianjin': 1373,
    'Wenzhou': 964.5,
    'Wuxi': 748,
    'Wuhu': 367.2,
    'Wuhan': 1364.9,
    'Xiamen': 528,
    'Xian': 1316.3,
    'Xining': 247.6,
    'Xianggang': 741.31,
    'Xuzhou': 902.8,
    'Yantai': 710.4,
    'Yangzhou': 457.7,
    'Yinchuan': 288.2,
    'Zhengzhou': 1274.2,
    'Zhongshan': 446.7,
    'Zhuhai': 246.7
}
print(population.keys())
n = len(population.keys())
temp_population = 0
for cityname in population.keys():
    pop = float(population[cityname])
    temp_population += pop

print(temp_population)