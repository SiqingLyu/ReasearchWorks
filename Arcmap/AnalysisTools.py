#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['font.sans-serif']=['SimHei']   # 用黑体显示中文
matplotlib.rcParams['axes.unicode_minus']=False     # 正常显示负号
def histogram_data(data, savepath):
    try:
        data = np.sort(data)
        new_data = []
        for i in range(len(data)):
            if data[i] > 40:
                break
            if data[i] != 0:
                new_data.append(data[i])
        new_data = np.array(new_data)
        plt.hist(new_data, bins=40, normed=0, facecolor="blue", edgecolor="black", alpha=0.7)
        # 显示横轴标签
        plt.xlabel("Floors")
        # 显示纵轴标签
        plt.ylabel("Frequence")
        # 显示图标题
        plt.title("Histogram")
        plt.savefig(savepath, bbox_inches='tight')
        plt.close('all')
    except(ValueError):
        print ("data is in zero-size")
    except(TypeError):
        print ("Type Error ")
        print (type(data[0]))
if __name__ == '__main__':
    data = np.random.randn(10000)
    histogram_data(data,'test.png')