import pandas as pd
import numpy as np

df_name = pd.read_excel(r'D:\下载\WeChat Files\wxid_rjybnd6x7egz22\FileStorage\File\2023-03\2020.xlsx', sheet_name='Sheet2', header=None)
name_arr = np.array(df_name)

df_2020 = pd.read_excel(r'D:\下载\WeChat Files\wxid_rjybnd6x7egz22\FileStorage\File\2023-03\2017-2021.xlsx', sheet_name='Sheet1', header=None)
# df_2021 = pd.read_excel(r'D:\下载\WeChat Files\wxid_rjybnd6x7egz22\FileStorage\File\2023-03\2021.xlsx', sheet_name='Sheet1', header=None)
# df_2022 = pd.read_excel(r'D:\下载\WeChat Files\wxid_rjybnd6x7egz22\FileStorage\File\2023-03\2022.xlsx', sheet_name='Sheet1', header=None)
arr_2020 = np.array(df_2020)
program_name_2020 = arr_2020[:, 1]
# print(program_name_2020)
# arr_2021 = np.array(df_2021)
# program_name_2021 = arr_2021[:, 1]
# arr_2022 = np.array(df_2022)
# print(arr_2020)
# print(arr_2022)

new_list = []
for item in arr_2020:
    money = item[4]
    money = money.replace(',', '')
    item[4] = float(money)
    if item[2] in name_arr:
        new_list.append(item)

# for item in arr_2021:
#     money = item[4]
#     money = money.replace(',', '')
#     item[4] = float(money)
#     if item[2] in name_arr and item[1] not in program_name_2020:
#         new_list.append(item)
#
# for item in arr_2022:
#     money = item[4]
#     money = money.replace(',', '')
#     item[4] = float(money)
#     if item[2] in name_arr and item[1] not in program_name_2020 and item[1] not in program_name_2021:
#         new_list.append(item)
# print(name_arr)
print(new_list)
data = pd.DataFrame(new_list)



new_list = []
for item in arr_2020:
    if item[2] in name_arr:
        new_list.append(item)

# for item in arr_2021:
#     if item[2] in name_arr:
#         new_list.append(item)
#
# for item in arr_2022:
#     if item[2] in name_arr:
#         new_list.append(item)
# print(name_arr)
# print(new_list)
data_all = pd.DataFrame(new_list)


writer = pd.ExcelWriter(r'D:\下载\WeChat Files\wxid_rjybnd6x7egz22\FileStorage\File\2023-03\ERSDC17-21.xlsx')		# 写入Excel文件
data.to_excel(writer, 'Sheet1', float_format='%.5f')		# ‘page_1’是写入excel的sheet名
data_all.to_excel(writer, 'Sheet2', float_format='%.5f')		# ‘page_1’是写入excel的sheet名
writer.save()

writer.close()