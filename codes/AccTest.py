import codecs
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from matplotlib.colors import LogNorm, FuncNorm, BoundaryNorm, NoNorm
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import matplotlib as mpl
from plotScatterDensity import plot_SD
# plt.rcParams['axes.facecolor']='black'
from tools import make_dir
import os
floor_mode = 30
consider_floor = 10
steps = [5, 10, 15, 20]
City_names = ['all']
City_names_no = ['All cities']
# City_names = ['Beijing', 'Nanjing', 'Tianjin', 'Guangzhou', 'Chongqing', 'Haerbin', 'Hangzhou',
#              'Kunming', 'Nanchang', 'Shanghai', 'Shenzhen', 'Wuhan', 'Xiamen', 'Xian', 'Zhengzhou',
#              'Aomen', 'Baoding', 'Changchun', 'Changsha', 'Changzhou', 'Chengdu', 'Dalian', 'Dongguan',
#              'Eerduosi', 'Foshan', 'Fuzhou', 'Guiyang', 'Haikou', 'Hefei', 'Huhehaote', 'Huizhou',
#              'Jinan', 'Lanzhou', 'Lasa', 'Luoyang', 'Nanning', 'Ningbo', 'Quanzhou', 'Sanya', 'Shantou',
#              'Shenyang', 'Shijiazhuang', 'Suzhou', 'Taiyuan', 'Taizhou', 'Tangshan', 'Wenzhou', 'Xianggang',
#              'Xining', 'Yangzhou', 'Yinchuan', 'Zhongshan']
# City_names = ['Beijing','Nanjing','Shanghai','Tianjin','Tangshan','Suzhou','Hangzhou','Shijiazhuang']
# City_names = ['Shenzhen', 'Baoding', 'Chengdu', 'Dalian', 'Guangzhou', 'Haerbin', 'Nanjing', 'Qingdao', 'Xiamen', 'Haikou', 'Shenzhen','Hangzhou', 'Xian']
# City_names_no = ['11: Shenzhen', '3: Baoding', '7: Chengdu', '2: Dalian', '10: Guangzhou',
#               '1: Harbin', '6: Nanjing', '4: Qingdao', '9: Xiamen', '12: Haikou', '11: Shenzhen', '8: Hangzhou', '5: Xian']
def get_city_StepSample(text_name):
    f = codecs.open(text_name, mode='r', encoding='utf-8')  # 打开txt文件，以‘utf-8'编码读取
    line = f.readline()  # 以行的形式进行读取文件
    Floor_under5 = []
    Floor_under10 = []
    Floor_under15 = []
    Floor_under20 = []
    Floor_over20 = []
    step_sample_num = []
    Floor_all = []
    All_info = []
    line = f.readline()
    while line:
        data = line.split(',')
        sample_floor = data[2]
        Floor_all.append(int(sample_floor))
        if int(sample_floor) > 0 and int(sample_floor) <= 5:
            Floor_under5.append(int(sample_floor))
        if int(sample_floor) > 5 and int(sample_floor) <= 10:
            Floor_under10.append(int(sample_floor))
        if int(sample_floor) > 10 and int(sample_floor) <= 15:
            Floor_under15.append(int(sample_floor))
        if int(sample_floor) > 15 and int(sample_floor) <= 20:
            Floor_under20.append(int(sample_floor))
        if int(sample_floor) > 20 :
            Floor_over20.append(int(sample_floor))
        line = f.readline()
    f.close()
    step_sample_num.append( ( len(Floor_under5) / len(Floor_all) ) * (len(Floor_all) * 0.001))
    step_sample_num.append( ( len(Floor_under10) / len(Floor_all) ) * (len(Floor_all) * 0.001))
    step_sample_num.append( ( len(Floor_under15) / len(Floor_all) ) * (len(Floor_all) * 0.001))
    step_sample_num.append( ( len(Floor_under20) / len(Floor_all) ) * (len(Floor_all) * 0.001))
    step_sample_num.append( ( len(Floor_over20) / len(Floor_all) ) * (len(Floor_all) * 0.001))
    Floors_groupbystep = []
    Floors_groupbystep.append(len(Floor_under5))
    Floors_groupbystep.append(len(Floor_under10))
    Floors_groupbystep.append(len(Floor_under15))
    Floors_groupbystep.append(len(Floor_under20))
    Floors_groupbystep.append(len(Floor_over20))
    Floor_all_num = len(Floor_all)
    # print(ids)

    Sample_total = 0
    for i in range(0,4):
        step = steps[i]
        Floor_num = Floors_groupbystep[i]
        sample_num = step_sample_num[i]
        print(str(step) + '层以下数：' + str(Floor_num) + ', 占比:' + str(Floor_num / Floor_all_num)[0:5] + '应选取样本数量' + str(int(sample_num)))
        All_info.append(int(sample_num))
        Sample_total += int(sample_num)
    print(str(step) + '层以上数：' + str(Floors_groupbystep[4]) + ', 占比:' + str(Floors_groupbystep[4] / Floor_all_num)[0:5] + '应选取样本数量' + str(int(step_sample_num[4])))
    Sample_total += int(step_sample_num[4])
    print('总选取的样本数量：', Sample_total)
    All_info.append(int(step_sample_num[4]))
    All_info.append(Sample_total)
    return All_info

def get_city_Rateunder10(text_name):
    f = codecs.open(text_name, mode='r', encoding='utf-8')  # 打开txt文件，以‘utf-8'编码读取
    line = f.readline()  # 以行的形式进行读取文件
    Floor_under10 = []
    ids = []
    GT_Floor = []
    line = f.readline()
    while line:
        a = line.split(',')
        c = a[0]
        d = a[2]
        ids.append(int(c))
        if int(d) > 0:
            GT_Floor.append(int(d))
        if int(d) > 0 and int(d) <= 10:
            Floor_under10.append(int(d))
        line = f.readline()
    f.close()
    # print(ids)
    print('验证房屋总数：' + str(len(ids)))
    print('10层以下数：' + str(len(Floor_under10)) + ', 占比:' + str(len(Floor_under10) / len(ids)))

def redistribute_city_sample(text_name, Sample_info):
    f = codecs.open(text_name, mode='r', encoding='utf-8')  # 打开txt文件，以‘utf-8'编码读取
    f.readline() #跳过第一行
    line = f.readline()  # 以行的形式进行读取文件
    ids = []
    GT_Floor = []
    Floor_62 = []
    Floor_info = []
    while line:
        a = line.split(',')
        b = a[3]  # 这是选取需要读取的位数
        c = a[0]
        d = a[2]
        b = b.replace("\r\n", "")
        if int(b) > 0 and int(d) < 30:
            Floor_62.append(int(b))  # 将其添加在列表之中
                                     # Floor_62是实际地面的建筑物层数，GT代表数据记录的层数
            ids.append(int(c))
            GT_Floor.append(int(d))
            Floor_info.append([int(c), int(d), int(b)])
        line = f.readline()
    f.close()
    Floor_samples = []
    Floor_arr = np.array(GT_Floor)
    Sample_total_num = len(GT_Floor)
    Floor_rest = Floor_arr
    for i in steps:
        Floor_sample = Floor_rest[Floor_rest <= i]
        Floor_rest = Floor_rest[Floor_rest > i]
        Floor_samples.append(Floor_sample)
        print('第', i, '层内总样本数量: ', len(Floor_sample))
    Floor_samples.append(Floor_rest)
    print('第 20 层以上样本数量: ', len(Floor_rest))
    print(Sample_info[0],Sample_info[5])
    if Sample_info[0] < len(Floor_samples[0]):
        total_num = Sample_info[5]
    else:
        total_num = len(Floor_samples[0]) / (Sample_info[0] / Sample_info[5])
    print('以5层以下为准，总数为: ', int(total_num), '样本总数为: ', Sample_total_num)
    New_Floor_samples = []
    New_GT_Floors = []
    New_sample_num = []
    print('以5层以下为准，应该选取各层样本数为： ')
    for i in range(0,5):
        x = int((Sample_info[i] / Sample_info[5]) * (total_num))
        if i < 4 :
            print('第 ', steps[i], '内应选取样本数量：', x)
        else:
            print('第 20 层以上样本数量: ', x)
        New_sample_num.append(x)
    i = 0
    New_sample_num = np.array(New_sample_num)
    while(i < len(Floor_info)):
        Floor = Floor_info[i][1]
        GT = Floor_info[i][2]
        if Floor <= 5 and Floor > 0 and New_sample_num[0] > 0:
            New_Floor_samples.append(Floor)
            New_GT_Floors.append(GT)
            New_sample_num[0] -= 1
        elif Floor <= 10 and Floor > 5 and GT < floor_mode and New_sample_num[1] > 0:
            New_Floor_samples.append(Floor)
            New_GT_Floors.append(GT)
            New_sample_num[1] -= 1
        elif Floor <= 15 and Floor > 10 and GT < floor_mode and New_sample_num[2] > 0:
            New_Floor_samples.append(Floor)
            New_GT_Floors.append(GT)
            New_sample_num[2] -= 1
        elif Floor <= 20 and Floor > 15 and GT < floor_mode and New_sample_num[3] > 0:
            New_Floor_samples.append(Floor)
            New_GT_Floors.append(GT)
            New_sample_num[3] -= 1
        elif Floor > 20  and GT < floor_mode and New_sample_num[4] > 0:
            New_Floor_samples.append(Floor)
            New_GT_Floors.append(GT)
            New_sample_num[4] -= 1
        i += 1

    return New_Floor_samples, New_GT_Floors

def get_city_RMSE(Floor_sample, GT_Floor, city):
    print('最终验证房屋总数：' + str(len(Floor_sample)))
    print('最终验证样本分布：')
    Floor_rest = np.array(Floor_sample)
    for i in steps:
        Floor_temp = Floor_rest[Floor_rest <= i]
        Floor_rest = Floor_rest[Floor_rest > i]
        print('最终第', i, '层内总样本数量: ', len(Floor_temp))
    print('最终第 20 层以上样本数量: ', len(Floor_rest))
    x = GT_Floor
    y = Floor_sample
    xbin = np.max(x) - np.min(x)
    ybin = np.max(y) - np.min(y)
    plt.figure(figsize=(5, 5.2), dpi=200)
    # 拟合点
    x0 = x
    y0 = y
    def f_1(x, A, B):
        return A * x + B
    # 绘制散点
    # plt.scatter(x0[:], y0[:], 3, "red")
    # 直线拟合与绘制
    A1, B1 = optimize.curve_fit(f_1, x0, y0)[0]
    x1 = np.arange(0, 30, 0.01)  # 30和75要对应x0的两个端点，0.01为步长
    y1 = A1 * x1 + B1
    # plt.plot(x1, y1, "blue")
    plt.plot(x1, x1, "gray", linestyle='--', zorder=2, alpha=0.9)
    equ = 'y = ' + str(A1)[0:6] +' * x + ' + str(B1)[0:6]
    print(equ)
    plt.title(" ")
    # plt.xlabel('Actual number of floors')
    # plt.ylabel('Number of floors from our data')
    x = np.array(x).flatten()
    y = np.array(y).flatten()
    MSE = np.sum(np.power((x - y), 2)) / len(x)
    R2 = 1 - MSE / np.var(x)
    RMSE = np.math.sqrt(MSE)
    MAE = np.mean(np.abs(x-y))
    # print("RMSE:", RMSE)
    print('R2: ', R2, 'RMSE: ', RMSE)
    # plt.text(2, np.max(y) - 3, f'RMSE = {np.round(RMSE, 3)}', fontsize=10, color='white')
    # plt.text(2, np.max(y) - 4, f'R2 = {np.round(R2, 3)}', fontsize=10, color='white')
    # plt.text(2, np.max(y) - 2, 'city: Nanjing', fontsize=10, color='white')
    # plt.title(text_name[0:-4])
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = 'NSimSun,Times New Roman'
    print(x, x.shape)
    x = np.hstack((x, 1))
    x = np.hstack((x, 35))
    y = np.hstack((y, 1))
    y = np.hstack((y, 35))
    h = plt.hist2d(x, y, bins=(34, 34), cmin=1, norm=BoundaryNorm(boundaries=np.arange(1,21,1), ncolors=300, extend='max'))
    # h = plt.hist2d(x, y, bins=(10,10), cmin=1, norm=BoundaryNorm(boundaries=[1,2,3,4,5,6,7,8,9,10,40,70,100, 201], ncolors=300, extend='max'))
    # cb1 = plt.colorbar(h[3], ticks=[0, 5, 10, 40])
    # tick_locator = ticker.MaxNLocator(nbins=5)  # colorbar上的刻度值个数
    # cb1.locator = tick_locator
    # cb1.set_ticks([1, 5, 10, 15, 20])
    # cb1.update_ticks()
    plt.axis([1,min(np.max(x), np.max(y)), 1, min(np.max(x), np.max(y))])
    plt.axis([1,30,1,30])
    # plt.xticks([1,5,10,15, 20, 25, min(np.max(x), np.max(y))], fontsize= 15)
    # plt.yticks([1,5,10,15, 20, 25,  min(np.max(x), np.max(y))], fontsize= 15)
    plt.xticks([1,5,10,15, 20, 25, 30], fontsize= 15)
    plt.yticks([1,5,10,15, 20, 25, 30], fontsize= 15)
    plt.grid(alpha=0.3, zorder=10, linestyle='--')

    plt.xlabel('Actual NoS', fontsize=16)
    plt.ylabel('NoS from our data', fontsize=16)
    # plt.title(city if city!='Haerbin' else 'Harbin', fontsize=24)
    # plt.text(3,23,f'RMSE = {np.round(RMSE,3)} \nMAE   = {np.round(MAE,3)}', fontsize=26, weight='bold')
    plt.title(city if city!='Haerbin' else 'Harbin', fontsize=22)
    plt.text(3,25,f'RMSE = {np.round(RMSE,3)} \nMAE   = {np.round(MAE,3)} \nR$^{2}$    = {np.round(R2,3)}', fontsize=20, weight='bold')

    plt.savefig(os.path.join(make_dir(r'./CityVals'), city[3:]+'.jpg'), dpi=400, bbox_inches='tight')
    plt.show()
    plt.close()
    return RMSE

if __name__ == '__main__':
    print('=======================start==========================\n')

    for ii in range(len(City_names)):
        city_name = City_names[ii]
        print('验证房屋所在城市：' + city_name)
        text_name = './CityInfo/ori/' + city_name + 'ori.txt'
        get_city_Rateunder10(text_name)
        print('//////////////////////分层处理/////////////////////////')
        Sample_info = get_city_StepSample(text_name)
        text_name = 'CityInfo/' + city_name + '.txt'
        print(text_name)
        try:
            print('///////////////根据分层结果调整样本分布/////////////////')
            Floor_sample, GT_Floor = redistribute_city_sample(text_name, Sample_info)
            print('////////////////////最终的结果///////////////////////')
            RMSE = get_city_RMSE(Floor_sample, GT_Floor, City_names_no[ii])
            print("RMSE:", RMSE)
        except(FileNotFoundError):
            print(city_name + '采样文件不存在！')
        print('--------------------------------------------------\n')

    print('==============================end================================')
