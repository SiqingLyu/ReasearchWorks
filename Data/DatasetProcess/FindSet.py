import numpy as np

from tools import *


def get_filename_by_lonlat(data_dir):
    data_paths, data_names = file_name_tif(data_dir)
    name_dict = {}
    for ii in range(len(data_paths)):
        data_name = data_names[ii]
        lon_min, lat_min = data_name.split('_')[-2].replace('p', '.'), data_name.split('_')[-1].replace('p', '.')
        lonlat = f"{lon_min}_{lat_min}"  # 保证类似102.5_24.3格式
        name_dict[lonlat] = data_paths[ii]
    return name_dict


def find_set_by_json(data_dir, dst_dir=None, json_file=r'ExperimentSet.json'):
    if dst_dir is not None:
        make_dir(dst_dir)
    json_data = read_json(json_file)
    name_dict = get_filename_by_lonlat(data_dir)
    for lonlatstr in json_data:
        # lon_min, lat_min = lonlatstr.split('_')[0], lonlatstr.split('_')[1]
        if lonlatstr in name_dict.keys():
            continue
            data_file = name_dict[lonlatstr]
            mycopyfile(data_file, dst_dir, fname_str=f"{lonlatstr}.tif")
        else:
            ds = gdal.Open(r'F:\ProductData\CBRA\CBRA_building_10m_0p5\2018\CBRA_2018_{}.tif'.format(lonlatstr))
            driver = gdal.GetDriverByName('GTiff')
            save_file = os.path.join(dst_dir, f"{lonlatstr}.tif")
            if os.path.isfile(save_file):
                delete_file(save_file)
            width, height = ds.RasterXSize, ds.RasterYSize
            # out_ds = driver.CreateCopy(r'Sentinel2_2017-2020_74.5_38.3_compress.tif', ds,
            #                            strict=1, callback=Show_Progress,
            #                            options=["TILED=YES", "COMPRESS=LZW", "BIGTIFF=YES"])  # LZW PACKBITS
            out_ds = driver.Create(save_file, xsize=width, ysize=height,
                                   bands=1, eType=gdal.GDT_Int8,
                                   options=["TILED=YES", "COMPRESS=LZW", "BIGTIFF=YES"])  # LZW PACKBITS
            geomat = ds.GetGeoTransform()
            out_ds.SetGeoTransform(geomat)
            out_ds.SetProjection(ds.GetProjection())

            data_ = ds.GetRasterBand(1).ReadAsArray()
            data_[data_ < 0] = 0
            data_[data_ > 0] = 0
            out_ds.GetRasterBand(1).WriteArray(data_)
            out_ds.GetRasterBand(1).SetNoDataValue(0)

            out_ds.FlushCache()


if __name__ == '__main__':
    find_set_by_json(r'F:\Data\Sentinel-2\GABLE_compress', dst_dir=r'F:\Data\ExperimentSet\label\height\GABLE')
    # for season in ["spring", "summer", "autumn", "winter", "all"]:
    #     find_set_by_json(rf'F:\Data\Sentinel-2\China_0p5\{season}',
    #                      dst_dir=rf'F:\Data\ExperimentSet\image\season\{season}')

    # find_AB_difference(r'F:\ProductData\CBRA\CBRA_building_10m_0p5\2018',
    #                    r'F:\ProductData\GABLE_0p5_10m_confirm', fix=['shp', 'tif'])
    # Aloss, BLoss = find_AB_difference_lon_lat(r'F:\ProductData\CBRA\CBRA_building_10m_0p5\2018',
    #                                           r'F:\ProductData\East_Asian_buildings\China_0p5_inLoc_10m_confirm',
    #                                           fix=['tif', 'tif'])
    # write_json("EALoss.json", BLoss)
