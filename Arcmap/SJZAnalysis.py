#!/usr/bin/python
# -*- coding:utf-8 -*-
import arcpy
from arcpy import env
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from arcpy.sa import *
from AnalysisTools import histogram_data
import numpy as np
City_names = ['Beijing', 'Nanjing', 'Nanchang', 'Chongqing', 'Hangzhou', 'Jinan',
              'Kunming', 'Guangzhou', 'Ningbo', 'Shanghai', 'Xiamen', 'Xian', 'Zhengzhou',
              'Haerbin', 'Wuhan']
env.workspace = "D:\\ArcMapAbout\\Data\\Shapes.gdb"
names = []
Floor_A = []
for name in City_names:
    names = []
    # name_bd = name + 'BD'
    # name_gd = name + 'GD'
    names.append(name)
    # names.append(name_bd)
    # names.append(name_gd)
    for file in names:
        try:
            cursor = arcpy.SearchCursor(file)
            fieldList = arcpy.ListFields(file)
        except(IOError):
            print ("file doesn't exist")
            continue
        # floor = []
        # height = []
        # area = []
        Floor = []
        fields = []
        for field in fieldList:
            fields.append(field.name)

        print ("----------------"+file+"------------------")
        print (fields)
        if "Floor" in fields and file == name:
            for row in cursor:
                try:
                    Floor.append(int(row.Floor))
                    Floor_A.append(int(row.Floor))
                except(RuntimeError):
                    print ("Floor doesn't exist")
                    break
            print ("Floor  exist")
            Floor = np.array(Floor)
            histogram_data(Floor, 'GTAnalysis/{0}floor.png'.format(file))
Floor_A = np.array(Floor_A)
histogram_data(Floor_A,'GTAnalysis/Floor_all.png'.format(file))

        # if "floor" in fields and file == name_gd:
        #     for row in cursor:
        #         try:
        #             floor.append(int(row.floor))
        #         except(RuntimeError):
        #             print ("floor  doesn't exist")
        #             break
        #     print ("floor  exist")
        #     floor = np.array(floor)
        #     histogram_data(floor, 'GDAnalysis/{0}floor.png'.format(file))
        # if "floor_1" in fields and file == name_gd:
        #     for row in cursor:
        #         try:
        #             floor.append(int(row.floor_1))
        #         except(RuntimeError):
        #             print ("floor  doesn't exist")
        #             break
        #     print ("floor  exist")
        #     floor = np.array(floor)
        #     histogram_data(floor, 'GDAnalysis/{0}floor.png'.format(file))
        #
        #
        # if "height" in fields and file == name_bd:
        #     for row in cursor:
        #         try:
        #             height.append(int(row.height))
        #         except(RuntimeError):
        #             print ("Floor doesn't exist")
        #             break
        #     print ("height  exist")
        #     height = np.array(height)
        #     histogram_data(height, 'BDAnalysis/{0}Height.png'.format(file))
        #

