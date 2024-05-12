# -*- coding: utf-8 -*-
import arcpy
from arcpy import da
from tools import *


class ShpCreator:
    def __init__(self, locations=None, save_path='', spatial_id=4326):
        self.locations = locations
        self.save_path = save_path
        self.spatial = arcpy.SpatialReference(spatial_id)

    def create_polygon(self, name='', index=0):
        """
        location:[
                    [
                        [x, y], [x, y], [x, y], ..., [x, y]
                    ],
                    [
                        [x, y], [x, y], [x, y], ..., [x, y]
                    ],
                    ...
                ]
        """
        out_path = os.path.join(self.save_path, name)
        ring = arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in self.locations[index]]), self.spatial)
        features = [ring]
        arcpy.CopyFeatures_management(features, out_path)

    def create_polygons(self, name='', index=0):
        """
        location:[
                    [
                        [x, y], [x, y], [x, y], ..., [x, y]
                    ],
                    [
                        [x, y], [x, y], [x, y], ..., [x, y]
                    ],
                    ...
                ]
        """
        features = []
        out_path = os.path.join(self.save_path, name)
        for index in range(len(self.locations)):
            ring = arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in self.locations[index]]), self.spatial)
            features.append(ring)
        arcpy.CopyFeatures_management(features, out_path)

    def create_polyline(self, name='', index=0):
        """
        location:[
                    [
                        [x, y], [x, y], [x, y], ..., [x, y]
                    ],
                    [
                        [x, y], [x, y], [x, y], ..., [x, y]
                    ],
                    ...
                ]
        """
        out_path = os.path.join(self.save_path, name)
        ring = arcpy.Polyline(arcpy.Array([arcpy.Point(*p) for p in self.locations[index]]), self.spatial)
        features = [ring]
        arcpy.CopyFeatures_management(features, out_path)

    def create_polylines(self, name=''):
        """
        location:[
                    [
                        [x, y], [x, y], [x, y], ..., [x, y]
                    ],
                    [
                        [x, y], [x, y], [x, y], ..., [x, y]
                    ],
                    ...
                ]
        """
        features = []
        out_path = os.path.join(self.save_path, name)
        for index in range(len(self.locations)):
            ring = arcpy.Polyline(arcpy.Array([arcpy.Point(*p) for p in self.locations[index]]), self.spatial)
            features.append(ring)
        arcpy.CopyFeatures_management(features, out_path)

    def create_rectangle(self, name='', index=0):
        """
        location:[
                    [x_min, y_min, x_max, y_max] ,
                    [x_min, y_min, x_max, y_max] ,
                    ...
                ]
        """
        out_path = os.path.join(self.save_path, name)
        if os.path.isfile(out_path):
            return
        lon_min, lat_min, lon_max, lat_max = self.locations[index]
        points = [[lon_min, lat_min], [lon_min, lat_max], [lon_max, lat_max], [lon_max, lat_min], [lon_min, lat_min]]
        ring = arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in points]), self.spatial)
        features = [ring]
        arcpy.CopyFeatures_management(features, out_path)

    def create_rectangles(self, name=''):
        """
        location:[
                    [x_min, y_min, x_max, y_max] ,
                    [x_min, y_min, x_max, y_max] ,
                    ...
                ]
        """
        out_path = os.path.join(self.save_path, name)
        features = []
        for index in range(len(self.locations)):
            lon_min, lat_min, lon_max, lat_max = self.locations[index]
            points = [[lon_min, lat_min], [lon_min, lat_max], [lon_max, lat_max], [lon_max, lat_min], [lon_min, lat_min]]
            ring = arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in points]), self.spatial)
            features.append(ring)
        arcpy.CopyFeatures_management(features, out_path)

    def create_point(self, name='', index=0):
        """
        location:[
                    [x, y] ,
                    [x, y] ,
                    ...
                ]
        """
        out_path = os.path.join(self.save_path, name)
        x, y = self.locations[index]
        point = arcpy.Point(x, y)  # 假设点是按10的倍数增加的
        point_geo = arcpy.PointGeometry(point, self.spatial)
        features = [point_geo]
        arcpy.CopyFeatures_management(features, out_path)

    def create_points(self, name=''):
        """
        location:[
                    [x, y] ,
                    [x, y] ,
                    ...
                ]
        """
        out_path = os.path.join(self.save_path, name)
        pointList = []
        for index in range(len(self.locations)):
            x, y = self.locations[index]
            point = arcpy.Point(x, y)  # 假设点是按10的倍数增加的
            point_geo = arcpy.PointGeometry(point, self.spatial)
            pointList.append(point_geo)
        arcpy.CopyFeatures_management(pointList, out_path)


if __name__ == '__main__':
#     locations = [[72.605228, 35.404896]]
    locations = [[61.224444444444, 23.209166666666, 86.06, 47.5805555555]]
    SC = ShpCreator(locations=locations, save_path=make_dir(r'G:\STKDATA\SHPs\Range'))
    SC.create_rectangle(name='Landslide20240415_big.shp')