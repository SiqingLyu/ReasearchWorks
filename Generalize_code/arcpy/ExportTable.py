from tools import *


def export_table_from_single_shp(shpfile):
    table_list = []
    fields = [field.name for field in arcpy.ListFields(shpfile)]
    with arcpy.da.UpdateCursor(shpfile, fields) as cursor:
        for row in cursor:
            # print row
            table_list.append(row)
    return table_list


def export_changed_from_single_shp(shpfile):
    total_changed = 0
    total = 0
    fields = [field.name for field in arcpy.ListFields(shpfile)]
    JC_Index = fields.index("Join_Count")
    with arcpy.da.UpdateCursor(shpfile, fields) as cursor:
        for row in cursor:
            # print row
            total += 1
            if row[JC_Index] == 0:
                total_changed += 1
    # print total_changed, total
    return total_changed, total


def export_table_from_dir(dir_path):
    shp_paths, shp_names = file_name_shp(dir_path)
    table_all = {}
    fields = [field.name for field in arcpy.ListFields(shp_paths[0])]
    table_all["names"] = fields
    table_all["content"] = []
    for ii in range(len(shp_names)):
        print "processing {}/{}".format(ii+1, len(shp_names))
        path_ = shp_paths[ii]
        # name_ = shp_names[ii]
        table_tmp = export_table_from_single_shp(path_)
        table_all["content"] += table_tmp
    return table_all


def export_changed_from_dir(dir_path):
    shp_paths, shp_names = file_name_shp(dir_path)
    total_all = 0.
    change_all = 0.
    for ii in range(len(shp_names)):
    # for ii in range(0, 2):
        print "processing {}/{}".format(ii+1, len(shp_names))
        path_ = shp_paths[ii]
        # name_ = shp_names[ii]
        changed_num, total_num = export_changed_from_single_shp(path_)
        change_all += changed_num
        total_all += total_num
    change_rate = change_all / total_all
    return change_rate


if __name__ == '__main__':
    data_dict = {}
    # for year in [2017, 2018, 2019, 2020, 2021]:
    year = 2021
    # data_dict = export_table_from_dir(r'G:\ProductData\CBRA\CBRA_{}_10m_shp_New'.format(year))
    change_rate = export_changed_from_dir(r'G:\ProductData\CBRA\CBRA_{}_10m_shp_Removed'.format(year))
    data_dict[year] = change_rate
    write_json(os.path.join(make_dir(r'G:\ProductData\CBRA\CBRA_data_dict'), 'Change_removed_{}.json'.format(year)), data_dict)
