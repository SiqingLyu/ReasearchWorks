from tools import *


def to_wgs84_shp_dir(filedir, save_root):
    make_dir(save_root)
    out_CS = arcpy.SpatialReference('WGS 1984')

    filepaths, filenames = file_name_shp(filedir)
    for ii in range(len(filepaths)):
        filepath = filepaths[ii]
        filename = filenames[ii]
        print filepath.decode('gbk')
        spatial_ref = arcpy.Describe(filepath).spatialReference
        if 'GCS_WGS_1984' not in spatial_ref.exportToString().split('[')[1].split(',')[0]:
            # pass
            save_path = os.path.join(save_root, filename + '.shp')
            print u"Projecting  " + filename.decode('gbk')
            if os.path.isfile(save_path):
                continue
            arcpy.Project_management(filepath, save_path, out_CS)
        else:
            for suffix in ['.dbf', '.prj', '.shp', '.shp.xml', '.shx', '.sbn', '.sbx']:
                from_file = filepath.replace('.shp', suffix)
                print from_file, save_root
                if os.path.isfile(from_file):
                    mycopyfile(from_file, save_root)


def to_wgs84_tif_dir(filedir, save_root):
    make_dir(save_root)
    out_CS = arcpy.SpatialReference('WGS 1984')

    filepaths, filenames = file_name_tif(filedir)
    for ii in range(len(filepaths)):
        filepath = filepaths[ii]
        filename = filenames[ii]
        print filepath.decode('gbk')
        spatial_ref = arcpy.Describe(filepath).spatialReference
        if 'GCS_WGS_1984' not in spatial_ref.exportToString().split('[')[1].split(',')[0]:
            # pass
            save_path = os.path.join(save_root, filename + '.tif')
            print u"Projecting  " + filename.decode('gbk')
            if os.path.isfile(save_path):
                continue
            print filepath, save_path, out_CS
            arcpy.ProjectRaster_management(filepath, save_path, out_CS, cell_size=8.9831528e-005)
        else:
            for suffix in ['.tif', '.tfw', '.tif.aux.xml', '.tif.vat.dbf', '.tif.xml', '.tif.ovr']:
                from_file = filepath.replace('.tif', suffix)
                print from_file, save_root
                if os.path.isfile(from_file):
                    mycopyfile(from_file, save_root)


def strict_clip(dir_clip, dir_ref, save_root):
    make_dir(save_root)
    tif_ps, tif_ns = file_name_tif(dir_clip)
    for ii in range(len(tif_ps)):
        print "{}/{}".format(ii+1, len(tif_ps))
        tif_path = tif_ps[ii]
        tif_name = tif_ns[ii]
        ref_path = os.path.join(dir_ref, tif_name+'.tif')
        save_path = os.path.join(save_root, tif_name+'.tif')
        assert os.path.isfile(ref_path)
        arcpy.Clip_management(in_raster=tif_path, out_raster=save_path,
                              in_template_dataset=ref_path, maintain_clipping_extent="MAINTAIN_EXTENT")


if __name__ == '__main__':
    # to_wgs84_tif_dir(r'D:\Dataset\@62allcities\Label_bk0_nodata0', r'D:\Dataset\@62allcities\Label_bk0_nodata0_wgs84')
    strict_clip(r'D:\Dataset\@62allcities\Label_bk0_nodata0_wgs84', dir_ref=r'G:\ProductData\GABLE_TIF_10m',
                save_root=r'G:\ProductData\AMAP_10m_wgs84_for_GABLE_in_61city')