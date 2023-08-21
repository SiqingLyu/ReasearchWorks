import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib as mpl
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'NSimSun,Times New Roman'
# color_tables = ['#324856', '#4a746a', '#d18237', '#d66c44', '#50293c']
# color_tables = ['#00997f', '#95d1ad', '#8ca581', '#b1d238', '#e8e613']
# color_tables = ['#61355f', '#9b4980', '#aad3e0', '#0d9aa2', '#045f6b']
# color_tables = ['#9f693e', '#d1a982', '#81555c', '#97472f', '#471d21']
# color_tables = ['#b8335b', '#d7a8b2', '#c4d4ca', '#809e73', '#31401c']
color_tables = ['#9ed048', '#c83c23', '#d9b611', '#2e4e7e', '#F11172']

df = pd.read_excel(r'D:\Desktop\实验表格\城市可获取季节表格1.xlsx')
print(df)

cities = np.array(df['City'])
spring_years = np.array(df['Spring'])
summer_years = np.array(df['Summer'])
autumn_years = np.array(df['Autumn'])
winter_years = np.array(df['Winter'])
# Other = np.array(df['Other Seasons'])

plt.figure(figsize=(13, 5), dpi=400)
plt.scatter(cities, spring_years, zorder=10, color=color_tables[0], label='Spring(April)')
plt.scatter(cities, summer_years, zorder=10, color=color_tables[1], label='Summer(July)')
plt.scatter(cities, autumn_years, zorder=10, color=color_tables[2], label='Autumn(October)')
plt.scatter(cities, winter_years, zorder=10, color=color_tables[3], label='Winter(January)')
# plt.scatter(cities, Other, zorder=10, color='#CCCCCC', edgecolors='grey', label='Other Seasons')
plt.xticks(rotation=270, fontsize=12)
plt.yticks(fontsize=12)
plt.grid(alpha=0.6, zorder=0, linestyle='-')

plt.ylim(2016, 2022)
plt.xlim(-1, 61)
# plt.ylim(np.min(y), np.max(y))
# plt.xlim(np.min(x), np.max(x))
plt.xlabel('The name of the City', fontsize=18)
plt.ylabel('Year', fontsize=18)

plt.legend(fontsize=14)
plt.savefig(r'DataAvailableCheck.jpg', dpi=700, bbox_inches='tight');

plt.show()
plt.close()