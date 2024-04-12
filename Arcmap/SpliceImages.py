# -*- coding: utf-8 -*-

"""
@File    : arcpy批量镶嵌1.py
@Author  : fungis@163.com
@Time    : 2020/04/16 09:14
@notice  : 运行前最好对栅格数据集进行备份，以免误删数据
"""
import os
import arcpy
from arcpy import env


# 删除拼接后的其他栅格文件
def removeGivenFile(input_file):
    if (os.path.exists(input_file)):
        os.remove(input_file)


def main(path = r"D:\PythonProjects\DataProcess\Data\TEST_BSG\Beijing" ):
    env.workspace = path # 输入栅格所在目录
    rasters = arcpy.ListRasters('*', raster_type='TIF')  # 如果是TIF影像，改下这个参数：raster_type='TIF'
    print ('栅格目录:' + str(rasters))
    # 存储所有的栅格文件名
    data = []
    for raster in rasters:
        data.append(raster)
    # 去掉第一个
    data2 = data[1:]
    # 第一个参数为除去第一个以外的所有栅格，第二个参数为第一个栅格即要合并到的栅格（拼接到第一个栅格中）
    if len(data) > 1:
        arcpy.Mosaic_management(data2, data[0])
        print('拼接完成:' + str(env.workspace) + os.sep + str(data[0]))
        # 删除其他拼接前的栅格，只保留拼接后的栅格数据集
        # for otherRaster in data2:
        #     removeGivenFile(str(env.workspace) + os.sep + str(otherRaster))

if __name__ == '__main__':
    # paths = [
    #     r"D:\experiment\results\Version2.0-Unet\UNet_M3Net_SSN_296_TESTBSG\Beijing",
    #     r"D:\experiment\results\Version2.0-Unet\UNet_M3Net_SSN_296_TESTBSG\Shanghai",
    #     r"D:\experiment\results\Version2.0-Unet\UNet_M3Net_SSN_296_TESTBSG\Guangzhou"]
    paths = []
    work_dir = r'D:\Dataset\GEDI\Nanfang'
    main(work_dir)
    # subdirs = os.listdir(work_dir)
    # for subdir in subdirs:
    #     paths.append(os.path.join(work_dir, subdir))
    #
    # # paths = [r'D:\Desktop\TEBEIJING']
    # for path in paths:
    #     main(path)