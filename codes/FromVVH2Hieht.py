import tifffile as tif
from tools import file_name_tif, make_dir
import numpy as np
import os
from scipy import optimize
from matplotlib.colors import LogNorm, FuncNorm, BoundaryNorm, NoNorm
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import matplotlib as mpl


# 拟合指数曲线
def target_func(x, a, b, c):
    return a * (np.power(x, b)) + c

def plot_scatter(x, y, savename= ''):
    # y = y[(x >= 0) & (x <= 50)]
    # x = x[(x >= 0) & (x <= 50)]
    xmax = np.max(x)
    xmin = np.min(x)
    xbin = int(xmax - xmin)
    ymax = np.max(y)
    ymin = np.min(y)
    ybin = int(ymax - ymin)
    # print(xbin, ybin)
    plt.figure(figsize=(6, 5), dpi=300)

    # 绘制散点
    # plt.scatter(x0[:], y0[:], 3, "red")
    # 直线拟合与绘制
    a,b,c = optimize.curve_fit(target_func, x, y, maxfev=500000)[0]
    x1 = np.arange(0, 90, 0.0001)  # 0.01为步
    y1 = a * (x1**b) + c
    plt.plot(x1, y1, "blue", zorder=2, alpha=0.5)

    # plt.plot(x1, x1, "grey", linestyle='--', zorder=1, alpha=0.7)

    equ = 'y = ' + str(a)[0:6] + ' * (x ** ' + str(b)[0:6] + ') + ' + str(c)[0:6]
    print(equ)
    MSE = np.sum(np.power((x - y), 2)) / len(x)
    R2 = 1 - MSE / np.var(x)
    RMSE = np.math.sqrt(MSE)
    MAE = np.mean(np.abs(x-y))
    print(f"RMSE: {RMSE}, R2: {R2}, MAE:{MAE}")
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = 'NSimSun,Times New Roman'

    # h = plt.hist2d(x, y, bins=(10000, 10000),  # cmap = CMAP,
    #                norm=BoundaryNorm(
    #                    boundaries=[0, 20, 40, 60, 80, 100, 200],
    #                    ncolors=300, extend='max')
    #                )
    # h = plt.hist2d(x, y, bins=(xbin, ybin), cmin=1, # cmap = CMAP,
    #                norm=BoundaryNorm(
    #                    boundaries=np.arange(1, 51),
    #                    ncolors=300, extend='max')
    #                )
    # plt.scatter(x, y)
    # plt.axis([0, 90, 0, 90])
    # plt.xticks([0, 15, 30, 45, 60, 75, 90], fontsize=15)
    # plt.yticks([0, 15, 30, 45, 60, 75, 90], fontsize=15)

    # cb1 = plt.colorbar(h[3], label="Samples", orientation='horizontal') #, ticks=[0, 5, 10, 2000])
    # tick_locator = ticker.MaxNLocator(nbins=5)  # colorbar上的刻度值个数
    # cb1.locator = tick_locator
    # cb1.set_ticks([1, 5, 10, 15, 20])
    # cb1.update_ticks()

    plt.scatter(x, y, zorder=10)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.grid(alpha=0.3, zorder=0, linestyle='--')

    plt.ylim(-5, 5)
    plt.xlim(0, 8)
    plt.xlabel('VVH', fontsize=20)
    plt.ylabel('ln(height)', fontsize=20)
    # plt.legend(fontsize=16)
    plt.savefig(savename, dpi=300, bbox_inches='tight');

    plt.show()
    plt.close()


def plot_scatter2(x, y, savename= ''):
    # y = y[(x >= 0) & (x <= 50)]
    # x = x[(x >= 0) & (x <= 50)]
    xmax = np.max(x)
    xmin = np.min(x)
    xbin = int(xmax - xmin)
    ymax = np.max(y)
    ymin = np.min(y)
    ybin = int(ymax - ymin)
    # print(xbin, ybin)
    plt.figure(figsize=(6, 5), dpi=300)

    def f_1(x, A, B):
        return A * x + B
    # 绘制散点
    # plt.scatter(x0[:], y0[:], 3, "red")
    # 直线拟合与绘制
    A,B = optimize.curve_fit(f_1, x, y, maxfev=1000)[0]
    x1 = np.arange(0, 90, 0.0001)  # 0.01为步
    plt.plot(x1, x1, "blue", zorder=2, alpha=0.5)

    # plt.plot(x1, x1, "grey", linestyle='--', zorder=1, alpha=0.7)

    equ = 'y = ' + str(A)[0:6] + ' * x  + ' + str(B)[0:6]
    print(equ)
    MSE = np.sum(np.power((x - y), 2)) / len(x)
    R2 = 1 - MSE / np.var(x)
    RMSE = np.math.sqrt(MSE)
    MAE = np.mean(np.abs(x-y))
    print(f"RMSE: {RMSE}, R2: {R2}, MAE:{MAE}")
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = 'NSimSun,Times New Roman'

    # h = plt.hist2d(x, y, bins=(10000, 10000),  # cmap = CMAP,
    #                norm=BoundaryNorm(
    #                    boundaries=[0, 20, 40, 60, 80, 100, 200],
    #                    ncolors=300, extend='max')
    #                )
    # h = plt.hist2d(x, y, bins=(xbin, ybin), cmin=1, # cmap = CMAP,
    #                norm=BoundaryNorm(
    #                    boundaries=np.arange(1, 51),
    #                    ncolors=300, extend='max')
    #                )
    # plt.scatter(x, y)
    # plt.axis([0, 90, 0, 90])
    # plt.xticks([0, 15, 30, 45, 60, 75, 90], fontsize=15)
    # plt.yticks([0, 15, 30, 45, 60, 75, 90], fontsize=15)

    # cb1 = plt.colorbar(h[3], label="Samples", orientation='horizontal') #, ticks=[0, 5, 10, 2000])
    # tick_locator = ticker.MaxNLocator(nbins=5)  # colorbar上的刻度值个数
    # cb1.locator = tick_locator
    # cb1.set_ticks([1, 5, 10, 15, 20])
    # cb1.update_ticks()

    plt.scatter(x, y, zorder=10)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.grid(alpha=0.3, zorder=0, linestyle='--')

    plt.ylim(0, 15)
    plt.xlim(0, 15)
    plt.xlabel('reference height', fontsize=20)
    plt.ylabel('estimate height', fontsize=20)
    # plt.legend(fontsize=16)
    plt.savefig(savename, dpi=300, bbox_inches='tight');

    plt.show()
    plt.close()




def cal_abc(lab_path, VVH_path):
    labpaths, filenames = file_name_tif(lab_path)
    # cityname = 'Xuzhou'
    jj = 0
    for ii in range(len(filenames)):
        labpath = labpaths[ii]
        filename = filenames[ii]
        # if cityname not in filename:
        #     continue
        # print('calculating VVH height of :', filename)
        VVHpath = os.path.join(VVH_path, filename+'.tif')
        lab = tif.imread(labpath).astype('float64')
        lab *= 3
        VVH = tif.imread(VVHpath)
        lab_500 = np.array([np.mean(lab[20:70, 20: 70]), np.mean(lab[70:120, 70:120]), np.mean(lab[70:120, 20: 70]), np.mean(lab[20: 70, 70:120])])
        VVH_500 = np.array([np.mean(VVH[20:70, 20: 70]), np.mean(VVH[70:120, 70:120]),  np.mean(VVH[70:120, 20: 70]), np.mean(VVH[20: 70, 70:120])])
        VVH_500 = VVH_500[lab_500>0]
        lab_500 = lab_500[lab_500>0]
        if np.isnan(VVH_500).any() or np.isnan(lab_500).any():
            continue
        if len(VVH_500) < 1:
            continue
        assert np.max(VVH_500) < 9
        if jj == 0:
            lab_all = lab_500.flatten()
            VVH_all = VVH_500.flatten()
        else:
            if len(lab_500) > 0:
                lab_all = np.hstack((lab_all, lab_500.flatten()))
                VVH_all = np.hstack((VVH_all, VVH_500.flatten()))
        jj += 1

    print(lab_all.shape, VVH_all.shape)
    # VVH_all += 0.2
    # print(lab_all.shape, VVH_all.shape)
    print(np.isinf(lab_all).any())
    lab_all_ = np.log(lab_all)
    # VVH_all = VVH_all[VVH_all<10]
    a, b, c = optimize.curve_fit(target_func, VVH_all, lab_all_, maxfev=500000)[0]
    plot_scatter(VVH_all, lab_all_, savename='TEST.png')
    mx = np.max(VVH_all)
    print(np.max(VVH_all))
    VVH_height = np.exp(187 * np.power(VVH_all, 0.00089) -186)
    plot_scatter2(lab_all, VVH_height, savename='TEST.png')

    return a,b,c


def main(path, save_path, lab_path):
    a, b, c = cal_abc(lab_path, path)
    print(a,b,c)
    # filepaths, filenames = file_name_tif(path)
    # for ii in range(len(filenames)):
    #     filename = filenames[ii]
    #     filepath = filepaths[ii]
    #     data = tif.imread(filepath)
    #
    #     data = a*(data**b) + c
    #     save_name = os.path.join(save_path, filename+'.tif')
    #     tif.imsave(save_name, data)


if __name__ == '__main__':
    path = r'D:\PythonProjects\DataProcess\Data\TEST_VVH\image\VVVH'
    save_path = r'D:\PythonProjects\DataProcess\Data\TEST_VVH\image\VVVH_height'
    lab_path = r'D:\PythonProjects\DataProcess\Data\TEST_VVH\label'
    make_dir(save_path)
    main(path, save_path, lab_path)