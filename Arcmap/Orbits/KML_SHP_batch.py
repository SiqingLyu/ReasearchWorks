import os

import arcpy

import sys

path = arcpy.GetParameterAsText(0)  # 文件所在文件夹

path2 = arcpy.GetParameterAsText(1)  # 转换后文件保存文件夹

arcpy.env.workspace = path

try:

    for kmz in arcpy.ListFiles('*.KM*'):
        name1 = os.path.join(path, kmz)

        name2 = str(kmz[:-4]) + ".shp"

        arcpy.AddMessage(name2)

        arcpy.KMLToLayer_conversion(name1, path2, kmz[:-4])

        name3 = path2 + "\\" + str(kmz[:-4]) + ".gdb"

        arcpy.AddMessage(name3)

        arcpy.env.workspace = name3

        featureClasses = arcpy.ListFeatureClasses('*', '', 'Placemarks')  # 列出要素名

        name4 = name3 + "\\" + 'Placemarks' + "\\" + str(featureClasses[0])

        arcpy.AddMessage(name4)

        arcpy.FeatureClassToFeatureClass_conversion(name4, path2, name2)

        arcpy.AddMessage(name2)


except arcpy.ExecuteError:

    print(arcpy.GetMessages(2))