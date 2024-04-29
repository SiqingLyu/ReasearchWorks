import shapefile
import tifffile as tif
from skimage.measure import label, regionprops
import numpy as np
from numpy import ndarray
import os
import shutil
import traceback


def get_range(x):
    ma = np.nanmax(x)
    mi = np.nanmin(x)
    return mi, ma


# def Read_tif(tif_path):
#     dataset = gdal.Open(tif_path, gdal.GA_Update)
#     dataset.FlushCache()
#     return dataset


def read_tif(tif_path):
    dataset = tif.imread(tif_path)
    return dataset


def cal_rmse(y_true, ypred):
    diff=y_true.flatten()-ypred.flatten()
    return np.sqrt(np.mean(diff*diff))


def move_file(src_path, dst_path, file):
    print('from : ', src_path)
    print('to : ', dst_path)
    try:
        # cmd = 'chmod -R +x ' + src_path
        # os.popen(cmd)
        f_src = os.path.join(src_path, file)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        f_dst = os.path.join(dst_path, file)
        shutil.move(f_src, f_dst)
    except Exception as e:
        print('move_file ERROR: ', e)
        traceback.print_exc()


def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
        print(f"文件 {filename} 删除成功！")
    else:
        print(f"文件 {filename} 不存在。")



def make_dir(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)
    return path


def Normalize(array, outpath):
    '''
    Normalize the array
    '''
    array[array > 1e10] = 0
    array[array < -1e10] = 0
    mx = np.nanmax(array)
    mn = np.nanmin(array)
    # assert mx!=mn
    if mx == mn:
        print(outpath, 'value is :', mx)
        return np.zeros_like(array)
    t = (array-mn)/((mx-mn))
    return t


# def Normalize(array):
#     '''
#     Normalize the array
#     '''
#     mx = np.nanmax(array)
#     mn = np.nanmin(array)
#     t = (array-mn)/(mx-mn)
#     return t


def file_name_tif(file_dir):
    '''
    eg: Listfile, allFilename = file_name(r'/www/lsq/optical')
    only for tif files
    :param file_dir: str
    :return: two List: a list of file absolute path & a list of file with no suffix
    '''
    if (os.path.isdir(file_dir)):
        L = []
        allFilename = []
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if file.split('.')[-1] != 'tif':
                    continue
                formatName = os.path.splitext(file)[1]
                fileName = os.path.splitext(file)[0]
                allFilename.append(fileName)
                if (formatName == '.tif'):
                    tempPath = os.path.join(root, file)
                    L.append(tempPath)
        return L, allFilename
    else:
        print('must be folder path')


def file_name_shp(file_dir):
    '''
    eg: Listfile, allFilename = file_name(r'/www/lsq/optical')
    only for shp files
    :param file_dir: str
    :return: two List: a list of file absolute path & a list of file with no suffix
    '''
    if (os.path.isdir(file_dir)):
        L = []
        allFilename = []
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if file.split('.')[-1] != 'shp':
                    continue
                formatName = os.path.splitext(file)[1]
                fileName = os.path.splitext(file)[0]
                allFilename.append(fileName)
                if (formatName == '.shp'):
                    tempPath = os.path.join(root, file)
                    L.append(tempPath)
        return L, allFilename
    else:
        print('must be folder path')


def file_name(file_dir, suffix):
    '''
    eg: Listfile, allFilename = file_name(r'/www/lsq/optical')
    only for shp files
    :param file_dir: str
    :return: two List: a list of file absolute path & a list of file with no suffix
    '''
    if (os.path.isdir(file_dir)):
        L = []
        allFilename = []
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if file.split('.')[-1] != suffix:
                    continue
                formatName = os.path.splitext(file)[1]
                fileName = os.path.splitext(file)[0]
                allFilename.append(fileName)
                if (formatName == ('.' + suffix)):
                    tempPath = os.path.join(root, file)
                    L.append(tempPath)
        return L, allFilename
    else:
        print('must be folder path')


def get_filelist_keywords(data_path, keywords):
    FileList, allFileid = file_name(data_path, suffix = 'shp')
    #keywords = ['after','upper']
    for keyword in keywords:
        FileList_keyword = []
        for file_path in FileList:
            if keyword in file_path:
                FileList_keyword.append(file_path)
        FileList = FileList_keyword
    return FileList


# def get_polygons_shpfile(path):
#     '''
#     to read a shp file and convert the data to list type
#     :param path:  file path where the target shp file is
#     :return: a list which contains all the points and the polygons
#     '''
#     shp_f = geopandas.read_file(path)
#     polygon = shp_f.geometry.to_json()
#     polygon_dict = json.loads(polygon)
#     polygon_dict = polygon_dict["features"]
#     return polygon_dict


# def cal_shp_area(polygons):
#     '''
#     to calculate the area of a shp file
#     :param dict: input shp file dictionary
#     :return: total area
#     '''
#     area_total = 0
#     len_dict = len(polygons)
#     with tqdm(total=len_dict) as pbar:
#         for i in range(0,len_dict):
#             if polygons[i]["geometry"]["coordinates"][0].__len__() >= 3:
#
#                 data = polygons[i]["geometry"]["coordinates"][0]
#                 try:
#                     area_total += Polygon(data).convex_hull.area
#                 except(AssertionError):
#                     # print("Assertion Error occurs ~\n")
#                     area_total+=0
#                 pbar.set_postfix(total_area = area_total)
#                 pbar.update()
#     return area_total


def get_shp_infos(shp_path):
    file = shapefile.Reader(shp_path)
    shapes = file.shapes()  # read all the features
    records = file.records()
    fields = file.fields
    return records, fields


def transpose_list(list):
    return zip(*list)


def get_allzero_image_name(image_path):
    Listfile, allFilename = file_name_tif(image_path)
    names = []
    for ii in range(len(allFilename)):
        tif_filepath = Listfile[ii]
        tif_fileid = allFilename[ii]
        # print('processing: ', tif_fileid)
        img_data = read_tif(tif_filepath)
        img_data = np.nan_to_num(img_data)
        mx = np.nanmax(img_data)
        mn = np.nanmin(img_data)
        if mx == mn:
            names.append(tif_fileid)
    return names


class LabelTarget:
    def __init__(self,
                 label_data: ndarray = None, height_data = None,
                 target_data: dict = None):
        assert label_data is not None or target_data is not None, 'Must input some Data!'
        self.label = label_data
        self.target = target_data
        self.height = height_data

    def from_target(self, background: int = 0):
        """
        get label data from a target
        :param background: default as 0
        :return: mask_all: label as numpy.ndarray
        """
        assert self.target is not None, 'Must input target data to get label'
        target_data = self.target
        data = target_data.copy()
        labels = data['nos']
        masks = data['masks']
        mask_all = np.zeros_like(masks[0])
        mask_all[mask_all == 0] = background
        for i in range(len(masks)):
            mask_data = masks[i]
            label_data = labels[i]
            mask_all = np.where(mask_data != background, int(label_data), mask_all)
        return mask_all

    def to_target_cpu(self, **kwargs):
        assert self.label is not None, 'Must input label data to get target'
        boxes, masks, labels, areas, noses, heights = self.get_box_mask_value_area(**kwargs)
        if boxes is None:
            return None
        assert len(boxes) > 0
        target = {
            'boxes': np.array(boxes),
            'labels': np.array(labels, dtype=np.int64),
            'masks': np.array(masks, dtype=np.uint8),
            'area': np.array(areas, dtype=np.float),
            'nos': np.array(noses,  dtype=np.float)
        }
        self.target = target
        return target

    def get_box_mask_value_area(self,
                                area_thd: int = 1,
                                mask_mode: str = 'value',  # bool value
                                background: int = 0,
                                label_is_value: bool = False,
                                value_mode: str = 'argmax',
                                connect_mode: int = 2):
        """
        use skimage.measure to get boxes, masks and the values, the areas of them
        :param label_is_value:
        :param background: background value of the image
        :param area_thd: objects whose area is below area_thd will be discard
        :param mask_mode: whether to connect pixels by 'is not background' or values
        :return: Boxes, Masks, Labels, Areas, all in array type
        """
        assert mask_mode in ['value', '01'], 'mask_mode must in [value, 01]'
        data = np.copy(self.label)
        height_data = np.copy(self.height) if self.height is not None else None
        value_region = label(data, connectivity=connect_mode, background=background)
        boxes, masks, labels, areas, nos_list, heights = [], [], [], [], [], []
        for region in regionprops(value_region):
            if region.area < area_thd: continue
            # region.bbox垂直方向为x， 而目标检测中水平方向为x
            y_min, x_min, y_max, x_max = region.bbox
            boxes.append([x_min, y_min, x_max, y_max])
            m = value_region == region.label
            if value_mode == 'argmax':
                # 取众数
                value = np.bincount(data[m]).argmax()
            if value_mode == 'mean':
                value = np.mean(data[m])

            if value_mode == 'meanheight':
                #from floor to height
                value = 3 * np.mean(data[m])

            if height_data is not None:
                height = np.mean(height_data[m])
                heights.append(height)

            nos_list.append(value)
            masks.append(m)
            labels.append(value if label_is_value else 1)
            areas.append(region.area)
        if len(boxes) == 0:
            print("No BOXes")
            return None, None, None, None, None, None
        assert background not in labels
        masks = np.array(masks)
        if mask_mode is '01':
            masks = np.where(masks, 1, background)
        return np.array(boxes), masks, np.array(labels), np.array(areas), np.array(nos_list), np.array(heights)




