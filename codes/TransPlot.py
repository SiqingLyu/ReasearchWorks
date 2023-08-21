from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import numpy as np
import csv
import pandas as pd
import matplotlib as mpl

mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'NSimSun,Times New Roman'
# color_tables = ['#324856', '#4a746a', '#d18237', '#d66c44', '#50293c']
# color_tables = ['#00997f', '#95d1ad', '#8ca581', '#b1d238', '#e8e613']
# color_tables = ['#61355f', '#9b4980', '#aad3e0', '#0d9aa2', '#045f6b']
# color_tables = ['#9f693e', '#d1a982', '#81555c', '#97472f', '#471d21']
# color_tables = ['#b8335b', '#d7a8b2', '#c4d4ca', '#809e73', '#31401c']
color_tables = ['#9ed048', '#c83c23', '#d9b611', '#2e4e7e', '#F11172']



xl = pd.ExcelFile(r'D:\Desktop\转换系数.xlsx')
levels = ['Low', 'Mid', 'Mid-high', 'High']
sheet_names = xl.sheet_names  # 所有的sheet名称
df = xl.parse('Combined_RMSE')  # 读取Excel中sheet_name的数据
# df = xl.parse('Combined')  # 读取Excel中sheet_name的数据
print(df)

MAE = []
trans =np.array(df['Trans'])
for i in range(1, 5):
    MAE.append(np.array(df[f'Level{i}']))
MAE = np.array(MAE)
print(MAE)
plt.figure(figsize=(6, 5), dpi=400)
# plt.plot(levels, MAE[:, 0], zorder=10, color=color_tables[0], label='Trans=2')
# plt.plot(levels, MAE[:, 1], zorder=10, color=color_tables[1], label='Trans=3')
# plt.plot(levels, MAE[:, 2], zorder=10, color=color_tables[2], label='Trans=4')
# plt.plot(levels, MAE[:, 3], zorder=10, color=color_tables[3], label='Trans=5')
# plt.xticks([2,3,4,5], rotation=0, fontsize=12)
# plt.yticks([0,1,2,3,4,5,6,7,8], fontsize=12)
# plt.grid(alpha=0.6, zorder=0, linestyle='-')
# plt.xlabel('The storey levels', fontsize=18)
# plt.ylabel('MAE', fontsize=18)

levels = [2, 3, 4, 5]
plt.plot(levels, MAE[0, :], zorder=10, color=color_tables[0], label='Storey: 1 - 3')
plt.plot(levels, MAE[1, :], zorder=10, color=color_tables[1], label='Storey: 4 - 6')
plt.plot(levels, MAE[2, :], zorder=10, color=color_tables[2], label='Storey: 7 - 9')
plt.plot(levels, MAE[3, :], zorder=10, color=color_tables[3], label='Storey: 10-12')
# plt.scatter(cities, Other, zorder=10, color='#CCCCCC', edgecolors='grey', label='Other Seasons')
plt.xticks([2,3,4,5], rotation=0, fontsize=18)
plt.yticks([0,1,2,3,4,5,6,7,8], fontsize=18)
plt.grid(alpha=0.6, zorder=0, linestyle='-')
plt.xlabel('Transformation Coefficient', fontsize=18)
plt.ylabel('RMSE', fontsize=18)

# plt.ylim(2016, 2022)
# plt.xlim(-1, 61)
# plt.xlim(-1, 61)
# plt.ylim(np.min(y), np.max(y))
# plt.xlim(np.min(x), np.max(x))

plt.legend(fontsize=12)
plt.savefig(r'LEVEL_MAE.jpg', dpi=700);

plt.show()
plt.close()