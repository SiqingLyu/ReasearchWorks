# -*- coding: utf-8 -*-

import numpy
import os
import arcpy
from arcpy import env
from arcpy.sa import *

# 环的组成点集合
Lon_min, Lon_max = 73.53051, 73.76622
Lat_min, Lat_max = 34.81504, 34.98520
points=[[Lon_min,Lat_min],[Lon_min,Lat_max],[Lon_max,Lat_max],[Lon_max,Lat_min],[Lon_min,Lat_min]]
SR = arcpy.SpatialReference(4326)  # WGS84

# 组成环的Array对象
ring=arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in points]), SR)
ring=arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in points]), SR)
# 创建features列表，用于存放要素，在内存
features=[]
# 通过ring（Array）创建Polygon对象
# 将Polygon要素添加到features列表
features.append(ring)

# 调用复制要素工具，将内存中的features列表创建为shapefile
arcpy.CopyFeatures_management(features, r"F:\STKDATA\SHPs\Range\Glacier_collapse_general_range_small.shp")
