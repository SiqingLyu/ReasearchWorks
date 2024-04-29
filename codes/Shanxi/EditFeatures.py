# -*- coding: utf-8 -*-
import os
import arcpy
import shutil
import json
import argparse


def judge_type(value):
    if value > 120:
        return "dry crop"
    elif value > 110:
        return "water crop"
    elif value > 60:
        return "unused"
    elif value > 50:
        return "buildings"
    elif value > 40:
        return "waters"
    elif value > 30:
        return "grass"
    elif value > 20:
        return "woods"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str, default=r"test.tif")
    parser.add_argument('--oripath', type=str, default="test.shp")
    args = parser.parse_args()

    # in_shp = r'G:\野外考察\2024\山西\Results\TempFiles\assignedshp_dissolve.shp'
    # ori_shp = r'G:\野外考察\2024\山西\应县图斑\应县.shp'
    # out_table = r'G:\野外考察\2024\山西\Results\TempFiles\assignedshp_dissolve_table.dbf'

    in_shp = args.filepath
    ori_shp = args.oripath
    out_table = in_shp[:-4]+'_table.dbf'
    #
    # #  ["ID", "FID", "ld2022", "AREA", "PERCENTAGE"]
    arcpy.TabulateIntersection_analysis(in_zone_features=in_shp, zone_fields="FID", in_class_features=ori_shp, out_table=out_table, class_fields="ld2022")
    fields = [field.name for field in arcpy.ListFields(out_table)]
    tab_dict = {}
    with arcpy.da.UpdateCursor(out_table, fields) as cursor:
        for row in cursor:
            # print row
            _, FID, ld, _, perc = row
            # print FID, tab_dict.keys()
            if FID not in tab_dict.keys():
                tab_dict[str(FID)] = [ld, 1, perc]
            elif perc > tab_dict[FID][2]:
                tab_dict[str(FID)][0] = ld
                tab_dict[str(FID)][1] += 1
                tab_dict[str(FID)][2] = perc
            else:
                tab_dict[str(FID)][1] += 1
    # with open(ref_txt, 'w') as f:
    #     # 将dic dumps json 格式进行写入
    #     f.write(json.dumps(tab_dict))

    arcpy.management.AddField(in_shp, "ld2022", "LONG")
    arcpy.management.AddField(in_shp, "Rc", "DOUBLE")
    arcpy.management.AddField(in_shp, "type", "DOUBLE")
    arcpy.management.AddField(in_shp, "correct", "DOUBLE")
    arcpy.management.AddField(in_shp, "verify", "DOUBLE")
    arcpy.management.AddField(in_shp, "remark", "TEXT")

    # use your own
    # in_shp = r'G:\野外考察\2024\山西\assignedshp_join.shp'
    # 获取图层
    fields = [field.name for field in arcpy.ListFields(in_shp)]
    Dynamic_Index = fields.index("GRIDCODE")
    FID_Index = fields.index("FID")
    Origin_Index = fields.index("ld2022")
    Rc_Index = fields.index("Rc")
    type_Index = fields.index("type")
    correct_Index = fields.index("correct")
    print fields

    with arcpy.da.UpdateCursor(in_shp, fields) as cursor:
        for row in cursor:
            row[Rc_Index] = 1
            FID_ID = row[FID_Index]
            Dynamic_ID = row[Dynamic_Index]
            type_ID = row[type_Index]
            correct_ID = row[correct_Index]

            Origin_ID = tab_dict[str(FID_ID)][0]
            count_ID = tab_dict[str(FID_ID)][1]

            if Dynamic_ID == Origin_ID:
                type_ID = 10
                correct_ID = Dynamic_ID
            elif judge_type(Dynamic_ID) == "water" and judge_type(Origin_ID) == "water":
                type_ID = 30
                correct_ID = Dynamic_ID
            elif count_ID == 1:
                type_ID = 20
                correct_ID = Dynamic_ID
            else:
                type_ID = 30
                correct_ID = Dynamic_ID

            row[Dynamic_Index] = Dynamic_ID
            row[type_Index] = type_ID
            row[correct_Index] = correct_ID
            row[Origin_Index] = Origin_ID
            cursor.updateRow(row)
    del cursor
    arcpy.management.DeleteField(in_shp, ["GRIDCODE"])

    fixes = ['dbf', 'shp', 'shx', 'sbn', 'sbx', 'prj']
    out_path = in_shp.replace('\\TempFiles', '').replace('assignedshp_dissolve', 'Result')
    for fix in fixes:
        shutil.move(in_shp[:-4]+'.{}'.format(fix), out_path[:-4]+'.{}'.format(fix))