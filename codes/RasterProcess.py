# -*- coding: utf-8 -*-
"""
@ Time    : 2020/6/22 9:27
@ Author  : Xu Penglei
@ Email   : xupenglei87@163.com
@ File    : RasterProcess.py
@ Desc    : 本文件中包含对栅格数据进行处理的程序
"""

from osgeo import gdal,osr,ogr
import numpy as np
import cv2
import warnings
import skimage.io as io
warnings.filterwarnings('ignore')

class RasterProcessor(object):
    def __init__(self):
        pass

    def saveRaster(self,output_path,arr,geomat=None,geoproj=None):
        _ = io.imsave(output_path,arr)
        ds = gdal.Open(output_path,gdal.GA_Update)
        ds.SetProjection(geoproj)
        ds.SetGeoTransform(geomat)
        ds=None

    def getGeoExtent(self,path):
        data = gdal.Open(path)
        w = data.RasterXSize
        h = data.RasterYSize
        geomat = data.GetGeoTransform()
        ulLon, ulLat, LonInterval, LatInterval = geomat[0], geomat[3], geomat[1], geomat[5]
        brLon = ulLon+w*LonInterval
        brLat = ulLat+h*LatInterval
        return [ulLon,ulLat,brLon,brLat]

    def GeoToPix(self,geomat,geoPoint):
        """
        将栅格空间坐标点转化为栅格点
        :param geomat: 栅格的地理信息，共有6个元素，geomat[0],geomat[3]对应raster左上角坐标,
                        geomat[1],geomat[5]分别对应lon分辨率和lat分辨率
        :param geoPoint: 空间坐标点
        :return: 栅格坐标
        """
        ulLon, ulLat, LonInterval, LatInterval = geomat[0],geomat[3],geomat[1],geomat[5]
        x,y = round((geoPoint[0]-ulLon)/LonInterval),round((geoPoint[1]-ulLat)/LatInterval)

        return x if x>=0 else 0, y if y>=0 else 0

    def clip(self, raster, UpperLeft, BottomRight, wh=None):
        """
        通过左上右下栅格坐标对栅格进行裁剪
        :param raster: 输入栅格
        :param UpperLeft: 左上角坐标,[row,col]
        :param BottomRight: 右下角坐标,[row,col]
        :return: cliped Raster
        """
        # TODO 添加异常情况处理
        if wh:
            return raster[UpperLeft[1]:UpperLeft[1]+wh[1],
               UpperLeft[0]:UpperLeft[0]+wh[0]]
        else:
            return raster[UpperLeft[1]:BottomRight[1],
                   UpperLeft[0]:BottomRight[0]]

    def clipWithGeo(self, raster,UpperLeft, BottomRight, geomat, wh=None):
        """
        通过左上右下地理坐标对栅格进行裁剪
        :param raster: 输入栅格
        :param UpperLeft: 左上角地理坐标[lon,lat]
        :param BottomRight: 右下角地理坐标[lon,lat]
        :param geomat: 栅格的地理信息，共有6个元素，geomat[0],geomat[3]对应raster左上角坐标,
                        geomat[1],geomat[5]分别对应lon分辨率和lat分辨率
        :return: clipedRaster
        """

        UpperLeftPix = self.GeoToPix(geomat,UpperLeft)
        BottomRightPix = self.GeoToPix(geomat,BottomRight)
        if wh:
            return self.clip(raster, UpperLeftPix, BottomRightPix,wh)
        else:
            return self.clip(raster,UpperLeftPix,BottomRightPix)

    def resample(self,raster,w=0,h=0,wFactor=None,hFactor=None,inter=None):
        """
        对栅格数据进行重采样
        :param raster: 输入栅格数据
        :param w: 重采样后的width
        :param h: 重采样后的height
        :param wFactor: w重采样比例
        :param hFactor: h重采样比例
        :return: 重采样后的栅格
        """
        if inter is not None:
            inter_method = inter
        else:
            inter_method = cv2.INTER_CUBIC
        if wFactor is None or hFactor is None:
            return cv2.resize(raster,(w,h),interpolation=inter_method)
        else:
            return cv2.resize(raster,(0,0),fx=wFactor,fy=hFactor,interpolation=inter_method)

    def resampleWithGeo(self,raster, geomat, w=0,h=0,wFactor=None,hFactor=None,inter=None):
        """
        对栅格进行重采样，同时修改Geomat
        :param raster: 输入栅格数据, Array
        :param geomat: Geomat
        :param w: 重采样之后的width
        :param h: 重采样之后的height
        :param wFactor: w重采样比例
        :param hFactor: h重采样比例
        :return: 重采样之后的栅格和Geomat
        """
        resample_raster = self.resample(raster,w,h,wFactor,hFactor,inter)
        old_h,old_w = raster.shape[:2]
        new_h,new_w = resample_raster.shape[:2]
        h_ratio,w_ratio = old_h/new_h, old_w/new_w
        geomat_new = list(geomat).copy()
        geomat_new[1] = geomat[1]*w_ratio
        geomat_new[5] = geomat[5]*h_ratio
        return resample_raster,geomat_new

    def maxminScale(self,raster,max=255,min=0):
        """
        将栅格数据归一化
        :param raster: 栅格数据
        :param max:
        :param min:
        :return: 归一化后的数据
        """
        return (max-raster)/(max-min)

    def geoReferencing(self,infile,outfile,cp_fn):
        """
        栅格几何校正, 结果不大对
        :param infile: 输入栅格的路径
        :param outfile: 输出栅格的路径
        :param cp_fn: 控制点的文件名
        :return:
        """
        def geo2pix(geomat,lng,lat):
            """
            :param geomat: 栅格的地理信息，共有6个元素，geomat[0],geomat[3]对应raster左上角坐标,
                        geomat[1],geomat[5]分别对应lon分辨率和lat分辨率
            :return:
            """
            pixel = (lng-geomat[0])/geomat[1]
            line = (lat-geomat[3])/geomat[5]
            return [pixel,line]

        with open(cp_fn,'r') as f:
            cp_str = f.readlines()
        cp = [list(map(float,n.replace('\n',' ').split('\t'))) for n in cp_str]

        dataset = gdal.Open(infile, gdal.GA_Update)
        dataset.FlushCache()
        proj = dataset.GetProjection()
        geomat = dataset.GetGeoTransform()
        gcps_list = [gdal.GCP(p[0],p[1],0,*geo2pix(geomat,p[2],p[3])) for p in cp]
        dataset.SetGCPs(gcps_list,proj)
        dataset.FlushCache()
        dst_ds = gdal.Warp(outfile, dataset, format='GTiff')
        del dataset, gcps_list

# inp_file = r'C:\Users\XuPenglei\Desktop\temp\GF2\GF2_PMS2_E113.5_N22.2_20150123_L1A0000607681\touying.tif'
# oup_file = r'C:\Users\XuPenglei\Desktop\temp\GF2\GF2_PMS2_E113.5_N22.2_20150123_L1A0000607681\reference.tif'
# cp_fn = r'C:\Users\XuPenglei\Desktop\temp\GF2\澳门_GF2_PMS2_E113.5_N22.2_20150123_L1A0000607681.txt'
# p = RasterProcessor()
# p.geoReferencing(inp_file,oup_file,cp_fn)


