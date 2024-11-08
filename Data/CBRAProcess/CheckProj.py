from tools import *


def check_proj_folder(folder, suffix='shp', tar_proj='GCS_WGS_1984'):
    file_paths, _ = file_name(folder, suffix)
    not_this_proj_files = []
    i = 0
    for filepath in file_paths:
        i += 1
        print "{} / {}".format(i, len(file_paths))
        spatial_ref = arcpy.Describe(filepath).spatialReference
        if tar_proj not in spatial_ref.exportToString().split('[')[1].split(',')[0]:
            not_this_proj_files.append(filepath)
    if len(not_this_proj_files) > 0:
        print not_this_proj_files
        print "This(these) files not in " + tar_proj
    return

if __name__ == '__main__':
    check_proj_folder(r'G:\ProductData\GABLE\GABLE_0p5', suffix='shp')