# -*- coding: utf-8 -*-
"""
此代码用于将KML转为图层
"""
import arcpy, os
from tools import *

def main(kml, db):
    # Set workspace (where all the KMLs are) 放kml文件的文件夹，如果kml文件过多，建议50个kml一个文件夹，多执行几个py就行，否则500个kml可能要一个小时
    arcpy.env.workspace = kml

    # Set local variables and location for the consolidated file geodatabase 导出的geodata文件夹
    outLocation = db

    # Create the master FileGeodatabase

    # Convert all KMZ and KML files found in the current workspace 找出kml文件，速度不快的
    for kmz in arcpy.ListFiles('*.kml'):

        print "CONVERTING: " + os.path.join(arcpy.env.workspace, kmz)
        arcpy.KMLToLayer_conversion(kmz, outLocation)


if __name__ == '__main__':
    kml = "F:\STKDATA\KMLs"
    db =  "F:\STKDATA\DBs"

    for end_date in [24, 26, 28, 30]:
        kml = r"F:\STKDATA\KMLs\23_{}".format(end_date)
        db = make_dir(r"F:\STKDATA\DBs\23_{}".format(end_date))
        main(kml, db)