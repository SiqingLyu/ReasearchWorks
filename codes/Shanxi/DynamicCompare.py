# -*- coding: utf-8 -*-
"""
代码用于结合DynamicWorld数据得到伪真值结果，
在本代码的结果中，不对ld2022进行修正，而是直接将correct赋值
以方便对照
最终要提交前，要把correct复制到ld2022上再提交
"""

from AssignGeo2Matches import asign
from tools import *


def fix_holes(bin_image, kernel):
    """
    erode bin image
    Args:
        bin_image: image with 0,1 pixel value
    Returns:
        erode image
    """
    kernel_size = kernel.shape[0]
    if (kernel_size % 2 == 0) or kernel_size < 1:
        raise ValueError("kernel size must be odd and bigger than 1")
    # if (bin_image.max() != 1) or (bin_image.min() != 0):
    #     raise ValueError("input image's pixel value must be 0 or 1")
    d_image = np.copy(bin_image)
    center_move = int((kernel_size - 1) / 2)
    for i in range(center_move, bin_image.shape[0] - kernel_size + 1):
        for j in range(center_move, bin_image.shape[1] - kernel_size + 1):
            data = bin_image[i - center_move:i + center_move,
                   j - center_move:j + center_move]
            data_list = data.flatten()
            # print(np.bincount(data_list).argmax())
            data[data == 0] = np.bincount(data_list).argmax()
            bin_image[i - center_move:i + center_move,
            j - center_move:j + center_move] = data
    return d_image


class ShanxiSolution:
    def __init__(self, dynamic_path, origin_path, dem_path, save_root, arcpy_file, ori_shp):
        self.origin_path = origin_path
        self.dynamic_path = dynamic_path
        self.dem_path = dem_path
        self.save_root = save_root
        self.temp_root = make_dir(os.path.join(save_root, 'TempFiles'))
        self.dynamic_data = read_tif(dynamic_path).astype(np.uint8)
        self.origin_data = read_tif(origin_path).astype(np.uint8)
        self.dem_data = read_tif(dem_path)
        self.dem_data = self.dem_data - np.min(self.dem_data)
        self.origin_data[self.origin_data == 255] = 0
        self.out_data = np.zeros_like(self.origin_data)
        self.arcpy_file = arcpy_file
        self.ori_shp = ori_shp

    def assign_img(self):  # 给生成的数据赋值地理坐标信息
        temp_save_path = self.temp_root + '\\Dynamic_Origin.tif'
        tif.imsave(temp_save_path, self.out_data)
        filename = self.origin_path.split('\\')[-1].split('.')[0]
        self.tifpath = self.temp_root + f'\\Assigned_{filename}1.tif'
        asign(from_img=temp_save_path, to_img=self.origin_path,
              out_path=self.tifpath)

    def pre_process(self):

        self.out_data[self.dynamic_data == 7] = 65  # 默认裸地
        self.out_data[self.origin_data == 45] = 45  # 滩涂
        self.out_data[self.origin_data == 46] = 46  # 滩地

        # self.out_data = np.where(self.dynamic_data == 4, self.origin_data,
        #                          self.out_data)  # 将Dynamic的耕地部分全部更换为origindatas
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 111)] = 111  # 水田旱地全部按照原始结果赋值，之后按照dem调整
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 112)] = 112  # 若对应地区海拔减去整个县海拔大于500m为山区
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 113)] = 113  # 大于500m为山区水田或旱地，200m丘陵，其余平原
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 114)] = 114
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 121)] = 121
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 122)] = 122
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 123)] = 123
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 124)] = 124
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 31)] = 123  # 默认为平原旱地， 注意，之后要根据DEM进行区分
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 32)] = 123  # 纠正错判为草地的类型
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 33)] = 123  #
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 41)] = 123  #
        self.out_data[(self.dynamic_data == 4) & (self.origin_data == 42)] = 123  #

        self.out_data[(self.dynamic_data == 5) & (
                (self.origin_data == 21) | (self.origin_data == 22) | (self.origin_data == 23))] = 22  # 灌木林
        self.out_data[(self.dynamic_data == 5) & (
                (self.origin_data == 31) | (self.origin_data == 32) | (self.origin_data == 33))] = 22  # 灌木林
        self.out_data[(self.dynamic_data == 1) | (self.origin_data == 21)] = 21  # 有林地
        self.out_data[(self.out_data == 21) & (self.origin_data == 23)] = 23  # 疏林地

        self.out_data[(self.dynamic_data == 2) & (self.origin_data == 31)] = 31  # 低草
        self.out_data[(self.dynamic_data == 2) & (self.origin_data == 32)] = 32  # 中草
        self.out_data[(self.dynamic_data == 2) & (self.origin_data == 33)] = 33  # 高草

        self.out_data[(self.dynamic_data == 7) & (self.origin_data == 61)] = 61  # 沙地
        self.out_data[(self.dynamic_data == 7) & (self.origin_data == 62)] = 62  # 戈壁
        self.out_data[(self.dynamic_data == 7) & (self.origin_data == 63)] = 63  # 盐碱地

        self.out_data[(self.dynamic_data == 6) | (self.origin_data == 53)] = 53  # 其他建设用地
        self.out_data[self.origin_data == 52] = 52  # 农村居民点
        self.out_data[self.origin_data == 51] = 51  # 城市用地

        self.out_data = np.where(self.dynamic_data == 8, self.origin_data, self.out_data) # 雪冰以原始为主

        # self.out_data = np.where(
        #     (self.origin_data != 51) & (self.origin_data != 52) & (self.origin_data != 53) & (self.dynamic_data == 6),
        #     52,
        #     self.out_data)  # 默认出现Origin中未辨认的建筑物时为农村居民点，后续要根据叠置分析判断用地类型

        self.out_data[self.dynamic_data == 0] = 42  # 默认湖泊， 后续要根据面积调整水库坑塘
        self.out_data[self.origin_data == 41] = 41  # 默认湖泊， 后续要根据面积调整水库坑塘
        self.out_data = np.where(
            ((self.origin_data == 45) | (self.origin_data == 46)) & (self.dynamic_data == 0),
            41,
            self.out_data)  # 滩涂滩地内为河渠

        self.out_data = np.where(self.out_data == 0, self.origin_data, self.out_data)  # 剩余地区与origin保持一致
        self.out_data = np.where(self.origin_data == 0, 0, self.out_data)  # 剩余地区与origin保持一致

        self.out_data[((self.out_data / 10) > 12) & (self.dem_data >= 500)] = 121
        self.out_data[((self.out_data / 10) > 12) & (self.dem_data >= 200) & (self.dem_data < 500)] = 122
        self.out_data[((self.out_data / 10) > 12) & (self.dem_data < 200)] = 123

        self.out_data[((self.out_data/10) < 12) & ((self.out_data/10) > 11) & (self.dem_data >= 500)] = 111
        self.out_data[((self.out_data/10) < 12) & ((self.out_data/10) > 11) & (self.dem_data >= 200) & (self.dem_data < 500)] = 112
        self.out_data[((self.out_data/10) < 12) & ((self.out_data/10) > 11) & (self.dem_data < 200)] = 113

        self.out_data = self.out_data.astype(np.uint8)

    def filter_img(self, img, bin=500, thd=20):
        img_width, img_length = img.shape
        img_test = np.zeros((img_width + bin, img_length + bin)).astype(np.uint8)
        img_test[0: img_width, 0:img_length] = np.copy(img)
        x_bin = int(np.floor((img_width + bin) / bin))
        y_bin = int(np.floor((img_length + bin) / bin))
        for i in range(x_bin):
            for j in range(y_bin):
                data_tmp = np.copy(img_test[i * bin: (i + 1) * bin, j * bin: (j + 1) * bin])
                LT = LabelTarget(label_data=data_tmp)
                LT.to_target_cpu(area_thd=thd,
                                     mask_mode='value',  # bool value
                                     background=0,
                                     label_is_value=False,
                                     value_mode='argmax',
                                     connect_mode=1)
                if LT.target is None:
                    img_test[i * bin: (i + 1) * bin, j * bin: (j + 1) * bin] = np.zeros((bin, bin))
                    continue
                print("processing")
                data_tmp = LT.from_target(background=0)
                assert np.max(data_tmp) != np.min(data_tmp)
                img_test[i * bin: (i + 1) * bin, j * bin: (j + 1) * bin] = data_tmp
        img[0: img_width, 0:img_length] = img_test[0: img_width, 0:img_length]
        return img

    def to_shp(self, arcpy_file=r'', ori_shp=r''):
        savepath = self.temp_root + '\\assignedshp.shp'
        cmd = r"{} ShanxiSolution_arcpytoshp.py " \
              r"--filepath {} --savepath {} --oripath {}".format(arcpy_file, self.tifpath, savepath, ori_shp)
        os.system(cmd)
        return savepath[:-4] + '_dissolve.shp'

    def statistic(self, arcpy_file=r'', in_shp=r'', ori_path=r'', savefile=r''):
        cmd = r"{} EditFeatures.py " \
              r"--filepath {} --oripath {}".format(arcpy_file, in_shp, ori_path)
        os.system(cmd)

    def get_dynamic_origin(self):
        self.dynamic_data = self.filter_img(self.dynamic_data, bin=1000, thd=100)
        self.pre_process()
        # self.out_data = erode_bin_arr(self.out_data, kernel=np.ones(shape=(5, 5)))

        self.out_data = self.filter_img(self.out_data, bin=1000, thd=100)
        # self.out_data = fix_holes(self.out_data, kernel=np.ones(shape=(5, 5)))
        self.assign_img()
        _path = self.to_shp(arcpy_file=self.arcpy_file, ori_shp=self.ori_shp)
        self.statistic(arcpy_file=self.arcpy_file, in_shp=_path, ori_path=self.ori_shp, savefile=self.save_root+'\\Result.shp')
        shutil.rmtree(self.temp_root)
        print("Finished!")


if __name__ == '__main__':
    # 结果保存于assignshp_join_result.shp中 使用时，必须保持所有输入的tif文件大小严格一致，即长宽相同
    SS = ShanxiSolution(dynamic_path=r'G:\野外考察\2024\山西\应县图斑\Dynamic_yingxian.tif',  # 对应地区的dynamicworld数据，分辨率10m，严格裁剪
                        origin_path=r'G:\野外考察\2024\山西\应县图斑\YingxianID_10m.tif',
                        dem_path=r'G:\野外考察\2024\山西\应县图斑\YingxianDEM_10m.tif',  # 对应地区的shp转栅格文件，分辨率10m
                        save_root=make_dir(r'G:\野外考察\2024\山西\Results'), arcpy_file=r'D:\ArcGIS\arcgis10.2\ArcGIS10.2\python.exe',
                        ori_shp=r'G:\野外考察\2024\山西\应县图斑\应县.shp')
    SS.get_dynamic_origin()
