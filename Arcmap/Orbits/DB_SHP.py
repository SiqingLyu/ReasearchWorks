# -*- coding: utf-8 -*-
"""
此代码用于将图层数据转为shp
"""
import arcpy, os
from tools import *
def main(out_path, db):
    arcpy.env.workspace = db

    # Loop through all the FileGeodatabases within the workspace
    wks = arcpy.ListWorkspaces('*', 'FileGDB')
    # Skip the Master GDB
    for fgdb in wks:
        fcz = []

        satellite_name = fgdb.split('\\')[-1].split('.')[0].replace('-', '_')
        save_name = os.path.join(out_path, '{}.shp'.format(satellite_name))
        if os.path.exists(save_name):
            continue
        print fgdb.split('\\')[-1].split('.')[0]
        # Change the workspace to the current FileGeodatabase
        arcpy.env.workspace = fgdb

        # For every Featureclass inside, copy it to the Master and use the name from the original fGDB
        featureClasses = arcpy.ListFeatureClasses('*', '', 'Placemarks')
        for fc in featureClasses:
            if fc == 'Polylines':  # 只要线段，点不要，这个看自己的需求
                print "COPYING: " + fc + " FROM: " + fgdb
                fcCopy = fgdb + os.sep + 'Placemarks' + os.sep + fc
                print(fcCopy)
                fcz.append(fcCopy)

        arcpy.Merge_management(fcz, save_name)

    # M123是导出shp的文件名，可以自行修改，不能重复

    print("done")


if __name__ == '__main__':
    # 下面是输出shp的文件夹
    out_path = "F:\STKDATA\SHPs"
    # 下面是gdb存放的的文件夹
    db = "F:\STKDATA\DBs"

    for end_date in [24, 26, 28, 30]:
        out_path = make_dir(r"F:\STKDATA\SHPs\23_{}".format(end_date))
        db = r"F:\STKDATA\DBs\23_{}".format(end_date)
        main(out_path, db)