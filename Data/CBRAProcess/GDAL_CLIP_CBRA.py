import logging
from osgeo import ogr
from tools import *
from Locators import CBRALocator
import glob
import warnings
warnings.filterwarnings("ignore")
ogr.RegisterAll()

compression_options = [
    'COMPRESS=LZW' # 使用LZW压缩算法
]


def cut_shp(input_path, out_path, shp_path):
    """
    对单个tif图像进行Shp裁剪
    :param input_path:文件输入地址
    :param shp_path:shp图层输入地址
    :param out_path:文件输出地址
    :return:
    """
    # 打开栅格数据集
    input_raster = gdal.Open(input_path)

    # 获取输入栅格数据的地理信息
    x_origin, x_pixel_size, _, y_origin, _, y_pixel_size = input_raster.GetGeoTransform()
    # 打开矢量多边形数据集（研究区域）
    clip_polygon_path = shp_path
    clip_polygon_ds = ogr.Open(clip_polygon_path)
    clip_polygon_layer = clip_polygon_ds.GetLayer()
    # 获取裁剪多边形的边界框
    clip_extent = clip_polygon_layer.GetExtent()
    a = abs(input_raster.GetGeoTransform()[5])
    b = input_raster.GetGeoTransform()[1]
    xmin, xmax, ymin, ymax = clip_extent

    # 获取裁剪多边形的几何
    # 创建输出栅格数据集
    driver = gdal.GetDriverByName("GTiff")
    output_raster = driver.Create(out_path, int((xmax - xmin) / b) + 2,
                                   int((ymax - ymin) / a) + 2, input_raster.RasterCount, gdal.GDT_UInt16,
                                  options=["COMPRESS=LZW"])

    output_raster.SetProjection(input_raster.GetProjection())
    output_raster.SetGeoTransform(
        (xmin, x_pixel_size, 0, ymax, 0, y_pixel_size))

    logging.info("开始裁剪")
    # 执行裁剪操作
    gdal.Warp(output_raster, input_raster,
              format='GTiff', cutlineDSName=clip_polygon_path, cropToCutline=True)
    # result.FlushCache()
    logging.info("裁剪完成")
    # 关闭数据集
    input_raster = None
    output_raster = None
    clip_polygon_ds = None
    return out_path


def mosaic_files(input_folder, output_file):
    vrt_path = input_folder + "/tiles.vrt"
    input_pattern = input_folder + '/*.tif'
    gdal.BuildVRT(vrt_path, glob.glob(input_pattern))
    gdal.Translate(output_file, vrt_path, creationOptions=compression_options)


def get_bbox(shpfile):
    ds = ogr.Open(shpfile, 0)
    if ds is None:
        print('Could not open shapefile')
        exit(1)
    lyr = ds.GetLayer(0)
    if lyr is None:
        print('Could not find layer in shapefile')
        exit(1)
    extent = lyr.GetExtent()
    xmin, ymin, xmax, ymax = extent
    # print(extent)
    return extent


def clip_patches(root_path, save_path, save_name, year, shp_file):
    Lon_min, Lon_max, Lat_min, Lat_max = get_bbox(shp_file)
    out_path = make_dir(os.path.join(save_path, str(year)))
    save_name = save_name + '_{:.1f}_{:.1f}'.format(Lon_min, Lat_min)
    out_raster = os.path.join(out_path, save_name + '.tif')
    print(out_raster)

    # if os.path.isfile(out_raster):
    #     return

    CBRA_locator = CBRALocator(root_path,
                               rectangle_pos=[[Lon_min, Lat_max],
                                              [Lon_max, Lat_min]],
                               year=year)
    CBRA_names = CBRALocator.locate_image(CBRA_locator)

    if (len(CBRA_names[1]) > 1) | (len(CBRA_names[2]) > 1) | (len(CBRA_names[3]) > 1):  # 有多个图像要裁剪
        out_path_ = make_dir(os.path.join(out_path, save_name))

        print(CBRA_names)  # 对应区域裁剪时所需要的所有的CBRA影像
        print("================NOW CLIPPING================")
        for ii in range(len(CBRA_names)):
            CBRA_path = CBRA_names[ii]
            if len(CBRA_path) == 0:  # 如果对应的影像不存在
                continue
            if not os.path.isfile(CBRA_path):
                continue
            out_raster_ii = os.path.join(out_path_, save_name + '_{}.tif'.format(ii))
            if os.path.isfile(out_raster_ii) is not True:  # 若已经有对应的影像，则跳过
                print("=======----processing: {}----=======".format(CBRA_path))

                cut_shp(CBRA_path, out_raster_ii, shp_file)

        #  获取所有的图像名称
        # clipped_file_paths, clipped_file_names = file_name_tif(os.path.join(save_path, str(year)))
        clipped_file_paths, clipped_file_names = file_name_tif(out_path_)
        if len(clipped_file_paths) == 0:
            return
        # if len(clipped_file_paths) == 1:
        #     tmp_file = clipped_file_paths[0]
        else:
            inputs = ''
            for path in clipped_file_paths:
                inputs += path + ';'
            # print inputs[: -1], os.path.join(out_path, save_name+'0.tif')
            print("================NOW IN MOSAIC================")
            # save_path_mosaic = os.path.join(out_path_, save_name + '_0.tif')
            out_raster_tmp = out_raster_ii.replace(".tif", "_merge.tif")
            merge_files(clipped_file_paths, out_raster_tmp)
            Image_Compress(out_raster_tmp, out_raster)
            # mosaic_files(out_path_, out_raster)

            # tmp_file = os.path.join(out_path_, save_name + '.tif')
            # tmp_file_resample = os.path.join(out_path_, save_name + '_resample.tif')
            # os.rename(save_path_mosaic,  tmp_file)
            # move_file(out_path_, out_path, save_name + '.tif')
            # arcpy.Resample_management(tmp_file, tmp_file_resample, ResOUT, "NEAREST")
        # TODO: CLIP (OPTIONAL)
        shutil.rmtree(out_path_)

    else:  # 只有一个图像需要裁剪
        return
        print(CBRA_names) # 对应区域裁剪时所需要的所有的CBRA影像
        print("================NOW CLIPPING================")
        CBRA_path = CBRA_names[0]
        if len(CBRA_path) == 0:  # 如果对应的影像不存在
            return
        if not os.path.isfile(CBRA_path):
            return
        print("=======----processing: {}----=======".format(CBRA_path))
        cut_shp(CBRA_path, out_raster, shp_file)


def main(year):
    # Configs
    CBRA_bin = 2.5
    # patch_bin = 0.5

    root_path = r'G:\ProductData\CBRA\0_source_data'  # CBRA 数据存储位置，内包含2016-2021所有文件夹和影像
    save_path = r'G:\ProductData\CBRA\1_0p5degree'  # 裁剪得到的影像的保存位置
    # save_path = r'G:\ProductData\CBRA\CBRA_building_10m_0p5'  # 裁剪得到的影像的保存位置
    save_name = "CBRA_{}".format(str(year))  # 裁剪得到的影像系列的名称, 最终结果默认存在save_name0.tif中
    clip_root = r'G:\ProductData\CHINA_fishnet_0p5'
    # bin_num = int(CBRA_bin / patch_bin)
    # 获取目标的经纬度范围

    clip_files, clip_names = file_name_shp(clip_root)
    for ii in range(len(clip_files)):
        clip_file = clip_files[ii]
        clip_name = clip_names[ii]

        clip_patches(root_path, save_path, save_name, year, shp_file=clip_file)


if __name__ == '__main__':
    # Lon_min, Lon_max, Lat_min, Lat_max = get_bbox(r'D:\Data\BeijingSouthEastRegion.shp')
    # print(Lon_min, Lon_max, Lat_min, Lat_max)
    main(2021)
