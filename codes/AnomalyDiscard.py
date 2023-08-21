#!/usr/bin/python
# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from matplotlib.colors import LogNorm, BoundaryNorm, NoNorm
import math
import matplotlib as mpl
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'NSimSun,Times New Roman'


def get_distance_point2line(point, line_ab):
    """
    Args:
        point: [x0, y0]
        line_ab: [k, b]
    """
    k, b = line_ab
    distance = abs(k * point[0] - point[1] + b) / math.sqrt(k**2 + 1)
    return distance

def f_1(x, A, B):
    return A * x + B


def main(excel_path = r'C:\Users\lenovo\Desktop\test.xlsx'):
    # 读取excel文件
    df = pd.read_excel(excel_path)
    x = np.array(df)[:,0]
    y = np.array(df)[:,1]
    assert len(x) == len(y), 'x, y长度不匹配'

    #拟合直线
    A1, B1 = optimize.curve_fit(f_1, x, y)[0]
    x_a = np.arange(np.min(x)-2, np.max(x), 0.01)  # 0.01为步长
    y_a = A1 * x_a + B1
    equ = 'y = ' + str(A1)[0:6] + ' * x + ' + str(B1)[0:6]
    print(equ)

    # 获取每个点到直线距离
    distances = []
    for ii in range(len(x)):
        x0 = x[ii]
        y0 = y[ii]
        point = [x0, y0]
        line = A1, B1
        dis = get_distance_point2line(point, line)
        dis_xy = [dis, x0, y0]
        distances.append(dis_xy)

    # 保存距离最大九个点
    distances = np.array(distances)
    distances = distances[distances[:, 0].argsort()]

    # distances.sort(np.lexsort(distances[:,::-1].T))
    df_anomaly = pd.DataFrame(distances[-9:, 1:])
    df_anomaly.to_csv(r'anomaly.csv', index=False)
    x_anomaly = distances[-9:, 1]
    y_anomaly = distances[-9:, 2]
    # 去除九个距离最大点
    distances = distances[: -9]
    # 按照原先的顺序排列

    new_xy = distances[:, 1:]
    new_xy = new_xy[new_xy[:, 0].argsort()]
    new_x = new_xy[:,0]
    new_y = new_xy[:,1]
    new_df = pd.DataFrame(new_xy)
    new_df.to_csv(r'moon.csv', index=False)

    #  画图
    plt.figure(figsize=(5,5), dpi=500)
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示汉字

    plt.title('After Outliers are  Eliminated')
    plt.scatter(new_x, new_y, zorder=10, marker='o', label='Reality Data')

    #新的拟合直线
    A1, B1 = optimize.curve_fit(f_1, new_x, new_y)[0]
    x1 = np.arange(np.min(new_x-2), np.max(new_x+2), 0.01)  # 0.01为步长
    y1 = A1 * x1 + B1
    equ = 'y = ' + str(A1)[0:6] + ' * x + ' + str(B1)[0:6]
    print(equ)
    plt.plot(x1, y1, "blue", zorder = 3, alpha=0.5, label='Fitting Straight Line after processing')
    # plt.plot(x1, x1, "black")

    # plt.grid(alpha = 0.3, zorder=1)
    plt.yticks([1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000])
    plt.xlabel('The numbers of workers', fontsize=15)
    plt.ylabel('The output of fish fillets', fontsize=15)
    plt.legend()  # 显示图例

    plt.figure(figsize=(5,5), dpi=500)
    plt.title('Before Outliers are  Eliminated')
    plt.scatter(x, y, zorder=10, marker='o', label='Anomaly Data', color='red', alpha=0.6)
    plt.plot(x_a, y_a, "gray", linestyle='-', zorder = 3, alpha=0.5, label='Fitting Straight Line before processing')
    plt.xlabel('The numbers of workers', fontsize=15)
    plt.ylabel('The output of fish fillets', fontsize=15)
    plt.legend()  # 显示图例
    plt.show()

if __name__ == '__main__':
    excel_path = r'Fish.xlsx'
    main(excel_path)