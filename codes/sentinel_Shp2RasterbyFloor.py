from osgeo import gdal, ogr, osr
import geopandas
import json
from shapely.geometry import Polygon, MultiPoint
from tqdm import tqdm
import time
import numpy as np
sr = osr.SpatialReference('LOCAL_CS["arbitrary"]')
#在内存中创建一个shape文件的图层，含有两个多边形
source_ds = ogr.GetDriverByName('Memory').CreateDataSource( 'shapefile' )
source_lyr = source_ds.CreateLayer('poly', srs=sr, geom_type=ogr.wkbPolygon )
source_lyr.CreateField(ogr.FieldDefn('TCODE',ogr.OFTReal))
wkt_geom = ['POLYGON((1020 1030 40,1020 1045 30,1050 1045 20,1050 1030 35,1020 1030 40))',
 'POLYGON((1010 1046 85,1015 1055 35,1055 1060 26,1054 1048 35,1010 1046 85))']
# print(wkt_geom[0])
# print(type(wkt_geom[0]))
#栅格值
def Get_polygon(dict):
    '''
    to calculate the area of a shp file
    :param dict: input shp file dictionary
    :return: total area
    '''
    polygons = []
    left = 10000000.0
    top = 0
    len_dict = len(dict["features"])
    with tqdm(total=len_dict) as pbar:
        for i in range(0,len_dict):
            if dict["features"][i]["geometry"]["coordinates"][0].__len__() >= 3:
                data = dict["features"][i]["geometry"]["coordinates"][0]
                data = str(Polygon(data))
                polygons.append(data)
                pbar.update()
                x =min(np.array(dict["features"][i]["geometry"]["coordinates"][0])[:,0])
                print(x)
                if left > x:
                    left = x
    time.sleep(0.5)
    return polygons, left, top


def main(path):
    shp_f = geopandas.read_file(path)
    polygon = shp_f.geometry.to_json()
    polygon_dict = json.loads(polygon)
    polygon_data,x,y = Get_polygon(polygon_dict)
    print(x)
    # celsius_field_values = list(shp_f["Floor"])
    # for i in range(len(polygon_data)):
    #     feat = ogr.Feature(source_lyr.GetLayerDefn())
    #     feat.SetGeometryDirectly(ogr.Geometry(wkt=str(polygon_data[i])))
    #     feat.SetField('TCODE', celsius_field_values[i])
    #     source_lyr.CreateFeature(feat)
    # #在内存中，创建一个 100*100 大小的1波段的空白图像
    # #‘’代表不往磁盘上写的话，文件名可以是空
    # target_ds = gdal.GetDriverByName('MEM').Create('', 1000, 1000, 1, gdal.GDT_Byte )
    # target_ds.SetGeoTransform( (1000,1,0,1100,0,-1) )
    # target_ds.SetProjection( sr.ExportToWkt())
    # #调用栅格化函数。RasterizeLayer函数有四个参数，分别有栅格对象，波段，矢量对象，TCODE的属性值将为栅格值
    # err = gdal.RasterizeLayer( target_ds, [1], source_lyr,options= ["ATTRIBUTE=TCODE"])
    # #将内存中的图像，存储到硬盘文件上
    # gdal.GetDriverByName('GTiff').CreateCopy('rasterized_poly.tif', target_ds)
    # del target_ds


if __name__ == '__main__':
    path = './Data/Beijing.shp'
    main(path)

del source_ds



