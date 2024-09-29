from tools import *


def compress_s2_dir(tar_dir, save_dir, delete_if=False):
    make_dir(save_dir)
    tar_paths, tar_names = file_name_tif(tar_dir)
    for ii in range(len(tar_paths)):
        img_name = tar_names[ii]
        img_path = tar_paths[ii]
        # print(from_img_name)
        print(f'processing: {img_name}')
        # asign(from_img=from_img_paths[ii], to_img=os.path.join(to_dir, from_img_name+'.tif'), out_path=os.path.join(save_dir, from_img_name+'.tif'))
        compress_s2_image(img_path, os.path.join(save_dir, img_name + '.tif'))
        if delete_if:
            delete_file(img_path)


def compress_GEDI_dir(tar_dir, save_dir, delete_if=False):
    make_dir(save_dir)
    tar_paths, tar_names = file_name_tif(tar_dir)
    for ii in range(len(tar_paths)):
        img_name = tar_names[ii]
        img_path = tar_paths[ii]
        # print(from_img_name)
        print(f'processing: {img_name}')
        # asign(from_img=from_img_paths[ii], to_img=os.path.join(to_dir, from_img_name+'.tif'), out_path=os.path.join(save_dir, from_img_name+'.tif'))
        compress_GEDI_image(img_path, os.path.join(save_dir, img_name + '.tif'))
        if delete_if:
            delete_file(img_path)


def compress_s2_image(data_file, save_file):
    ds = gdal.Open(data_file)
    driver = gdal.GetDriverByName('GTiff')
    if os.path.isfile(save_file):
        delete_file(save_file)
    width, height = ds.RasterXSize, ds.RasterYSize
    # out_ds = driver.CreateCopy(r'Sentinel2_2017-2020_74.5_38.3_compress.tif', ds,
    #                            strict=1, callback=Show_Progress,
    #                            options=["TILED=YES", "COMPRESS=LZW", "BIGTIFF=YES"])  # LZW PACKBITS
    out_ds = driver.Create(save_file, xsize=width, ysize=height,
                           bands=4, eType=gdal.GDT_UInt16,
                           options=["TILED=YES", "COMPRESS=LZW", "BIGTIFF=YES"])  # LZW PACKBITS
    geomat = ds.GetGeoTransform()
    out_ds.SetGeoTransform(geomat)
    out_ds.SetProjection(ds.GetProjection())

    for i in range(1, 5):
        data_ = ds.GetRasterBand(i).ReadAsArray()
        data_ = np.nan_to_num(data_ * 1e4)
        data_[data_ <= 0] = 0
        data_ = data_.astype(np.uint16)
        out_ds.GetRasterBand(i).WriteArray(data_)
        out_ds.GetRasterBand(i).SetNoDataValue(0)

    out_ds.FlushCache()


def compress_GEDI_image(data_file, save_file):
    ds = gdal.Open(data_file)
    driver = gdal.GetDriverByName('GTiff')
    if os.path.isfile(save_file):
        delete_file(save_file)
    width, height = ds.RasterXSize, ds.RasterYSize
    # out_ds = driver.CreateCopy(r'Sentinel2_2017-2020_74.5_38.3_compress.tif', ds,
    #                            strict=1, callback=Show_Progress,
    #                            options=["TILED=YES", "COMPRESS=LZW", "BIGTIFF=YES"])  # LZW PACKBITS
    out_ds = driver.Create(save_file, xsize=width, ysize=height,
                           bands=4, eType=gdal.GDT_UInt16,
                           options=["TILED=YES", "COMPRESS=LZW", "BIGTIFF=YES"])  # LZW PACKBITS
    geomat = ds.GetGeoTransform()
    out_ds.SetGeoTransform(geomat)
    out_ds.SetProjection(ds.GetProjection())

    data_ = ds.GetRasterBand(1).ReadAsArray()
    data_ = np.nan_to_num(data_ * 1e1)
    data_[data_ <= 0] = 0
    data_ = data_.astype(np.uint16)
    out_ds.GetRasterBand(1).WriteArray(data_)
    out_ds.GetRasterBand(1).SetNoDataValue(0)

    out_ds.FlushCache()



def compress_dir(tar_dir, save_dir):
    make_dir(save_dir)
    tar_paths, tar_names = file_name_tif(tar_dir)
    for ii in range(len(tar_paths)):
        img_name = tar_names[ii]
        img_path = tar_paths[ii]
        # print(from_img_name)
        print(f'processing: {img_name}')
        # asign(from_img=from_img_paths[ii], to_img=os.path.join(to_dir, from_img_name+'.tif'), out_path=os.path.join(save_dir, from_img_name+'.tif'))
        Image_Compress(img_path, os.path.join(save_dir, img_name + '.tif'))

        
def main():
    compress_dir(r'F:\ProductData\GABLE_0p5_10m_confirm', r'F:\Data\Sentinel-2\GABLE_compress')
    compress_dir(r'F:\ProductData\CBRA\CBRA_building_10m_0p5\2018', r'F:\Data\Sentinel-2\CBRA_compress')
    # Image_Compress()


if __name__ == '__main__':
    # compress_s2_image(r'Sentinel2_2017-2020_74.5_38.3.tif', r'Sentinel2_2017-2020_74.5_38.3_compress_LZW+DataCut.tif')
    # compress_GEDI_image(r'115.0_39.3.tif', r'115.0_39.3_compress_LZW+DataCut.tif')
    # Image_Compress(r'115.0_39.3.tif', r'115.0_39.3_compress_LZW.tif')

    for season in ["spring", "summer", "autumn", "winter", "all"]:
        compress_s2_dir(rf'F:\Data\Sentinel-2\China_0p5\{season}',
                        rf'F:\Data\Sentinel-2\China_0p5_compress\{season}',
                        delete_if=True)
    # main()
