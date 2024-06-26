# -*- coding: utf-8 -*-
"""
这个代码用于将shp文件转换为栅格文件

"""
from tools import *
ResOUT = 8.9831528e-005


def to_raster_signle(filepath, savepath, data_="GABLE"):
    field_name = "height" if data_ == "GABLE" else "STATUS"
    print filepath, savepath
    arcpy.FeatureToRaster_conversion(filepath, field_name, savepath, ResOUT)


def if_empty(file_path):
    file_size = os.path.getsize(file_path) / 1024
    if file_size < 2:
        return True
    return False


def to_raster_dir(dpath, save_root, data_="GABLE"):
    make_dir(save_root)
    paths, names = file_name_shp(dpath)
    for ii in range(len(paths)):
        print "processing {}/{}".format(ii+1, len(paths))
        file_path = paths[ii]
        file_name = names[ii]
        save_path = os.path.join(save_root, file_name+'.tif')

        if (if_empty(file_path)) or os.path.isfile(save_path):
            continue

        to_raster_signle(file_path, save_path, data_=data_)


def confirm_single(file_path, ref_file, save_file):
    arcpy.Clip_management(in_raster=file_path, in_template_dataset=ref_file,
                          out_raster=save_file, nodata_value=255, maintain_clipping_extent="MAINTAIN_EXTENT")


def confirm_dir(file_root, ref_root, save_root):
    make_dir(save_root)

    # filepaths, filenames = file_name_tif(file_root)
    ref_paths, ref_names = file_name_tif(ref_root)
    for ii in range(len(ref_paths)):
        ref_path = ref_paths[ii]
        ref_name = ref_names[ii].replace('.', 'p')
        lon_, lat_ = ref_name.split('_')[-2],  ref_name.split('_')[-1]
        loc_name = "{}_{}".format(lon_, lat_)
        print loc_name

        file_path = os.path.join(file_root, loc_name+'.tif')
        if not os.path.isfile(file_path):
            continue

        save_file = os.path.join(save_root, loc_name+'.tif')
        if os.path.isfile(save_file):
            continue

        confirm_single(file_path, ref_path, save_file)


if __name__ == '__main__':
    # year = 2016
    # to_raster_dir(r'G:\ProductData\East_Asian_buildings\China_0p5_inLoc', save_root=r'G:\ProductData\East_Asian_buildings\China_0p5_inLoc_10m', data_="EA")
    # to_raster_dir(r'G:\ProductData\GABLE_0p5', save_root=r'G:\ProductData\GABLE_0p5_10m')

    # arcpy.FeatureToRaster_conversion(r'G:\ProductData\GABLE_0p5\127p5_48p3.shp', 'height', r'G:\test.tif', ResOUT)

    # confirm_dir(file_root=r'G:\ProductData\East_Asian_buildings\China_0p5_inLoc_10m',
    #             ref_root=r'G:\ProductData\CBRA\CBRA_building_10m_0p5\2018',
    #             save_root=r'G:\ProductData\East_Asian_buildings\China_0p5_inLoc_10m_confirm')

    confirm_dir(file_root=r'G:\ProductData\GABLE_0p5_10m',
                ref_root=r'G:\ProductData\CBRA\CBRA_building_10m_0p5\2018',
                save_root=r'G:\ProductData\GABLE_0p5_10m_confirm')