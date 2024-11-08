# -*- coding: utf-8 -*-
from tools import *


def remain_changed_only(in_shp):
    fields = [field.name for field in arcpy.ListFields(in_shp)]
    assert ("Join_Count" in fields), "Unknown prop name of gridcode in assignshp_dissolve.shp"
    Dynamic_Index = fields.index("Join_Count")
    with arcpy.da.UpdateCursor(in_shp, fields) as cursor:
        cntr = 0

        for row in cursor:
            cntr += 1

            if row[Dynamic_Index] == 0:
                cursor.deleteRow()
                print "Record {} Deleted".format(cntr)


def delete_unchanged_shp_dir(dir_path):
    shp_paths, shp_names = file_name_shp(dir_path)
    for ii in range(len(shp_names)):
    # for ii in range(0, 2):
        print "processing {}/{}".format(ii+1, len(shp_names))
        path_ = shp_paths[ii]
        remain_changed_only(path_)


if __name__ == '__main__':
    data_dict = {}
    # for year in [2017, 2018, 2019, 2020, 2021]:
    year = 2021
    delete_unchanged_shp_dir(r'G:\ProductData\CBRA\CBRA_{}_10m_shp_Removed'.format(year))
