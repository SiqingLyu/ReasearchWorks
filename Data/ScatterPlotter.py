import numpy as np
import matplotlib as mpl

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Name   : scatter_render_main2.py
# Author : zengsk in NanJing
# Created: 2019/12/11 12:46

"""
Details:  散点图绘制
"""
import time
import numpy as np
import pandas as pd
import matplotlib.colors as colors
import matplotlib.pyplot as plt


def density_calc(x, y, radius):
    """
    散点密度计算（以便给散点图中的散点密度进行颜色渲染）
    :param x:
    :param y:
    :param radius:
    :return:  数据密度
    """
    res = np.empty(len(x), dtype=np.float32)
    for i in range(len(x)):
        print(i)
        res[i] = np.sum((x > (x[i] - radius)) & (x < (x[i] + radius))
                        & (y > (y[i] - radius)) & (y < (y[i] + radius)))
    return res


# Script Start...
start = time.process_time()

url_i = r"E:\Scripts\Test\scatter\data\estimate1.csv"
url_ii = r"E:\Scripts\Test\scatter\data\estimate2.csv"
url_iii = r"E:\Scripts\Test\scatter\data\estimate3.csv"
savefig_name = r"E:\Scripts\Test\scatter\data\scatter_render3.jpg"

# ------------ read data  -----------------
matrix_i = pd.read_csv(url_i).values
sevp_i = matrix_i[:, 1]   # 观测数据
estimate_i = matrix_i[:, 2]  # 预测数据

matrix_ii = pd.read_csv(url_ii).values
sevp_ii = matrix_ii[:, 1]
estimate_ii = matrix_ii[:, 2]

matrix_iii = pd.read_csv(url_iii).values
sevp_iii = matrix_iii[:, 1]
estimate_iii = matrix_iii[:, 2]

# ----------- Define Parameters ------------
radius = 3  # 半径
colormap = plt.get_cmap("jet")  # 色带
marker_size = 1  # 散点大小
xrange = [0, 350]
yrange = [0, 350]
xticks = np.linspace(0, 350, 8)
yticks = np.linspace(0, 350, 8)
xlabel = "Observation"
ylabel_i = "Estimate-1"
ylabel_ii = "Estimate-2"
ylabel_iii = "Estimate-3"
cbar_ticks = [10**0, 10**1, 10**2, 10**3, 10**4, 10**5]
font = {'family': 'Times New Roman',
        'weight': 'bold',
        'size': 7}

# -----------------  Plot Start  -----------------
fig = plt.figure(1, facecolor="grey")

# ---------------  sub plot no.1  ----------------
plt.subplot(1, 3, 1, aspect="equal")
Z1 = density_calc(sevp_i, estimate_i, radius)
plt.scatter(sevp_i, estimate_i, c=Z1, cmap=colormap, marker=".", s=marker_size,
            norm=colors.LogNorm(vmin=Z1.min(), vmax=0.5 * Z1.max()))
plt.xlim(xrange)
plt.ylim(yrange)
plt.xticks(xticks, fontproperties='Times New Roman', size=7)
plt.yticks(yticks, fontproperties='Times New Roman', size=7)
plt.xlabel(xlabel, fontdict=font)
plt.ylabel(ylabel_i, fontdict=font)
plt.grid(linestyle='--', color="grey")
plt.plot(xrange, yrange, color="k", linewidth=0.8, linestyle='--')
plt.rc('font', **font)
# color bar
cbar = plt.colorbar(orientation='horizontal', extend="both", pad=0.1)  # 显示色带
cbar.set_label("Scatter Density", fontdict=font)
cbar.set_ticks(cbar_ticks)
cbar.ax.tick_params(which="major", direction="in", length=2, labelsize=6)  # 主刻度
cbar.ax.tick_params(which="minor", direction="in", length=0)  # 副刻度

# ---------------  sub plot no.2  ----------------
plt.subplot(1, 3, 2, aspect="equal")
Z2 = density_calc(sevp_ii, estimate_ii, radius)
plt.scatter(sevp_ii, estimate_ii, c=Z2, cmap=colormap, marker=".", s=marker_size,
            norm=colors.LogNorm(vmin=Z2.min(), vmax=Z2.max()))
plt.xlim(xrange)
plt.ylim(yrange)
plt.xticks(xticks)
plt.yticks(yticks)
plt.xlabel(xlabel, fontsize=8)
plt.ylabel(ylabel_ii, fontsize=8)
plt.grid(linestyle='--', color="grey")
plt.plot(xrange, yrange, color="k", linewidth=0.8, linestyle='--')
plt.rc('font', **font)
# color bar
cbar = plt.colorbar(orientation='horizontal', extend="both", pad=0.1)  # 显示色带
cbar.set_label("Scatter Density", fontdict=font)
cbar.set_ticks(cbar_ticks)
cbar.ax.tick_params(which="major", direction="in", length=2, labelsize=6)  # 主刻度
cbar.ax.tick_params(which="minor", direction="in", length=0)  # 副刻度

# ---------------  sub plot no.3  ----------------
plt.subplot(1, 3, 3, aspect="equal")
Z3 = density_calc(sevp_iii, estimate_iii, radius)
plt.scatter(sevp_iii, estimate_iii, c=Z3, cmap=colormap, marker=".", s=marker_size,
            norm=colors.LogNorm(vmin=Z3.min(), vmax=Z3.max()))
plt.xlim(xrange)
plt.ylim(yrange)
plt.xticks(xticks)
plt.yticks(yticks)
plt.xlabel(xlabel, fontsize=8)
plt.ylabel(ylabel_iii, fontsize=8)
plt.grid(linestyle='--', color="grey")
plt.plot(xrange, yrange, color="k", linewidth=0.8, linestyle='--')
plt.rc('font', **font)

# color bar
cbar = plt.colorbar(orientation='horizontal', extend="both", pad=0.1)  # 显示色带
cbar.set_label("Scatter Density", fontdict=font)
cbar.set_ticks(cbar_ticks)
cbar.ax.tick_params(which="major", direction="in", length=2, labelsize=6)  # 主刻度
cbar.ax.tick_params(which="minor", direction="in", length=0)  # 副刻度

# save figure
fig.tight_layout()
plt.savefig(savefig_name, dpi=600)
plt.show()

elapsed = time.process_time() - start
print("This program totally costs {0} seconds!".format(elapsed))
print(" .... All is OK!!")
