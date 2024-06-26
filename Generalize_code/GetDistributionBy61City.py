from tools import *
import matplotlib.pyplot as plt
import matplotlib as mpl

import pandas as pd
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'NSimSun,Times New Roman'

PLOT_SHOW_ = False

EULUC_DICT = {
    101: "Residential",
    201: "Business Office",
    202: "Commercial Service",
    301: "Industrial",
    # 401: "Road",
    402: "Transportation Stations",
    # 403: "Airport Facilities",
    501: "Administrative",
    502: "Educational",
    503: "Medical",
    504: "Sport and cultural",
    505: "Park and greenspace"
}


class Distributor:
    """
    in this class, the namelist of floor and function should be the same
    """

    def __init__(self, floor_root: str = '', function_root: str = '', nodata: dict = None, save_root: str = 'Test', mode: str = 'Floor'):
        if nodata is None:
            nodata = {"floor": 255, "func": 255, "GEDI": -9999}
        self.save_root = make_dir(save_root)
        self.func_root = function_root
        self.floor_root = floor_root
        self.floor_paths, self.floor_names = file_name_tif(floor_root)
        self.function_paths, self.function_names = file_name_tif(function_root)
        self.nodata = nodata
        self.dist_cities, self.dist_overall = self.get_distribution()
        self.mode = mode

    def get_num_all(self):
        self.num_all = self.get_num(self.dist_overall)
        return self.num_all

    def get_num_all_by_class(self):
        temp_dict = {}
        self.num_all_by_class = self.get_num_by_class(self.dist_overall, temp_dict)
        return self.num_all_by_class

    def get_num(self, dict_):
        num = {}
        for v in EULUC_DICT.keys():
            class_name = EULUC_DICT[v]
            if class_name not in dict_.keys():
                continue
            if self.mode == "StoryHeight":
                to_count_list = np.round(dict_[class_name]).astype(np.uint8)  # for story height
                to_count_list = list(to_count_list[(to_count_list <= 6) & (to_count_list > 0)])

            elif self.mode == "Floor":
                to_count_list = np.array(dict_[class_name])  # for story height
                to_count_list = list(to_count_list[to_count_list <= 30])

            count_num = count_list(to_count_list)
            num = add_dict1_to_dict2(dict1=count_num, dict2=num)
        return num

    def get_num_by_class(self, dict_, num_by_class):
        for v in EULUC_DICT.keys():
            class_name = EULUC_DICT[v]
            if class_name not in dict_.keys():
                continue
            if self.mode == "StoryHeight":
                to_count_list = np.round(dict_[class_name]).astype(np.uint8)  # for story height
                to_count_list = list(to_count_list[(to_count_list <= 6) & (to_count_list > 0)])

            elif self.mode == "Floor":
                to_count_list = np.array(dict_[class_name])  # for story height
                to_count_list = list(to_count_list[to_count_list<=30])

            count_num = count_list(to_count_list)
            if class_name not in num_by_class.keys():
                num_by_class[class_name] = count_num
            else:
                num_by_class[class_name] = add_dict1_to_dict2(dict1=count_num, dict2=num_by_class[class_name])
        return num_by_class

    def get_num_city(self):
        num_city = {}
        for city in self.dist_cities.keys():
            num_city[city] = self.get_num(self.dist_cities[city])
        self.num_city = num_city
        return num_city

    def get_num_city_by_class(self):
        num_city_by_class = {}
        for city in self.dist_cities.keys():
            temp_dict = {}
            num_city_by_class[city] = self.get_num_by_class(self.dist_cities[city], temp_dict)
        self.num_city_by_class = num_city_by_class
        return num_city_by_class

    def get_distribution(self):
        print("Getting Distribution")
        dists = {}
        all_class_num_dict = {}
        for ii in range(len(self.floor_names)):
            floor_path, floor_name = self.floor_paths[ii], self.floor_names[ii]
            if floor_name not in self.function_names:
                continue

            floor_data = read_tif(floor_path)
            func_path = os.path.join(self.func_root, floor_name + '.tif')
            func_data = read_tif(func_path)
            data_invalid = func_data[(func_data != self.nodata["func"]) & (func_data != 0)]
            if len(data_invalid) == 0:
                dists[floor_name] = {}
                continue

            print(f"working on {floor_name}")
            class_dict = self.get_class_num(func_data, floor_data)
            for v in EULUC_DICT.keys():
                if EULUC_DICT[v] not in all_class_num_dict.keys():
                    all_class_num_dict[EULUC_DICT[v]] = class_dict[EULUC_DICT[v]]
                else:
                    all_class_num_dict[EULUC_DICT[v]] += class_dict[EULUC_DICT[v]]
            dists[floor_name] = class_dict

        return dists, all_class_num_dict

    def get_class_num(self, func_data, floor_data):
        class_dict = {}
        for v in EULUC_DICT.keys():
            class_area = np.where(func_data == int(v), True, False)
            cor_floor = floor_data[(class_area == True) & (floor_data != self.nodata["floor"])]
            class_dict[EULUC_DICT[v]] = list(cor_floor)
        return class_dict

    def plot_dist_single(self, dist: dict = None, title: str = 'Test', format_: str = 'bar'):
        assert format_ in ['pie', 'bar'], "不支持扇形图和柱状图以外的图像 "
        if format_ == "bar":
            plt.figure(figsize=(10, 5))
            plt.title(title)
            plt.bar(dist.keys(), dist.values())
        if format_ == "pie":
            plt.figure(figsize=(10, 10))
            plt.title(title)
            plt.pie(dist.values(), labels=dist.keys(), autopct='%1.1f%%', startangle=90)

        save_path = make_dir(os.path.join(self.save_root, format_))
        plt.savefig(os.path.join(save_path, f"{title}_{format_}.jpg"))
        if PLOT_SHOW_:
            plt.show()

    def plot_dist_city(self, format_: str = 'bar'):
        for city in self.num_city:
            dist = self.num_city[city]
            self.plot_dist_single(dist, title=f"{city}", format_=format_)

    def plot_dist_all(self, format_: str = 'bar'):
        self.plot_dist_single(self.num_all, title='0_Overall', format_=format_)

    def plot_dist_city_by_class(self, format_: str = 'bar'):
        for city in self.num_city_by_class:
            for k in self.num_city_by_class[city]:
                dist = self.num_city_by_class[city][k]
                self.plot_dist_single(dist, title=f"{city}_{k}", format_=format_)

    def plot_dist_all_by_class(self, format_: str = 'bar'):
        for k in self.num_all_by_class:
            self.plot_dist_single(self.num_all_by_class[k], title=f"0_Overall_{k}", format_=format_)

    def plot_dist_city_by_sth(self):
        for city in self.num_city_by_sth_perc:
            dist = self.num_city_by_sth_perc[city]
            plot_multi_bar(func_list=list(EULUC_DICT.values()), data_dict=dist,
                           title=f"{city}_Storyheight",save_root=self.save_root)

    def plot_dist_all_by_sth(self):
        # print()
        plot_multi_bar(func_list=list(EULUC_DICT.values()), data_dict=self.num_all_by_sth_perc,
                       title=f"0_Overall_Storyheight", save_root=self.save_root)

    def get_all_dict_by_sth(self):
        self.num_all_by_sth = get_dict_by_sth(self.num_all_by_class)
        # print(self.num_all_by_sth.keys())
        return self.num_all_by_sth

    def get_sum_in_class(self, dict_):
        class_sum = np.zeros(len(EULUC_DICT.keys()))
        index_ = 0
        for class_name in dict_.keys():
            for v in dict_[class_name].values():
                # print(v)
                class_sum[index_] += v
            index_ += 1
        return class_sum

    def get_all_dict_in_perc(self):
        self.num_all_by_sth = get_dict_by_sth(self.num_all_by_class)  # {0: ..., 1: ...,}
        self.num_all_by_sth_perc = []
        class_sum = self.get_sum_in_class(self.num_all_by_class)
        for sth in self.num_all_by_sth:
            num_ = sth[1] #[?, ?, ?, ... , ?]: len=len(EULUC_DICT.keys())
            # print(np.array(self.num_all.values()))
            perc = np.array(num_) / class_sum
            perc = np.round(perc, 4) * 100
            self.num_all_by_sth_perc.append([sth[0], perc])
        return self.num_all_by_sth_perc

    def get_all_dict_by_sth_in_perc(self):
        self.num_all_by_sth = get_dict_by_sth(self.num_all_by_class)  # {0: ..., 1: ...,}
        self.num_all_by_sth_perc = []
        class_sum = self.get_sum_in_class(self.num_all_by_class)
        for sth in self.num_all_by_sth:
            num_ = sth[1] #[?, ?, ?, ... , ?]: len=len(EULUC_DICT.keys())
            # print(np.array(self.num_all.values()))
            perc = np.array(num_) / class_sum
            perc = np.round(perc, 4) * 100
            self.num_all_by_sth_perc.append([sth[0], perc])
        return self.num_all_by_sth_perc

    def get_city_dict_by_sth(self):
        num_city_by_sth = {}
        city_dict = self.num_city_by_class
        for city in city_dict.keys():
            city_dict_tmp = city_dict[city]
            num_city_by_sth[city] = get_dict_by_sth(city_dict_tmp)
        self.num_city_by_sth = num_city_by_sth
        return num_city_by_sth

    def get_city_dict_by_sth_in_perc(self):
        num_city_by_sth_perc = {}

        city_dict = self.num_city_by_class
        for city in city_dict.keys():
            city_dict_tmp = city_dict[city]
            class_sum = self.get_sum_in_class(city_dict_tmp)
            num_city_by_sth = get_dict_by_sth(city_dict_tmp)
            num_perc = []
            for sth in num_city_by_sth:
                num_ = sth[1]  # [?, ?, ?, ... , ?]: len=len(EULUC_DICT.keys())
                perc = np.array(num_) / class_sum
                perc = np.round(perc, 4) * 100
                num_perc.append([sth[0], perc])
            num_city_by_sth_perc[city] = num_perc
        self.num_city_by_sth_perc = num_city_by_sth_perc
        return num_city_by_sth_perc


def get_dict_by_sth(dict_):
    all_dict_by_sth = {}
    for class_name in dict_.keys():
        sth_dict = dict_[class_name]
        for sth in sth_dict.keys():
            # print(sth)
            index_ = list(EULUC_DICT.values()).index(class_name)
            if sth not in all_dict_by_sth.keys():
                all_dict_by_sth[sth] = np.zeros(len(EULUC_DICT.keys()))
                # print(all_dict_by_sth[sth])
                all_dict_by_sth[sth][index_] = sth_dict[sth]
            else:
                all_dict_by_sth[sth][index_] += sth_dict[sth]
    all_dict_by_sth = sorted(all_dict_by_sth.items(), key=lambda x: x[0])
    return all_dict_by_sth


def get_story_height_data(floor_data, height_data):
    # out_data = np.zeros_like(floor_data)
    out_data = np.where((floor_data != 255) & (height_data >= 2), height_data/floor_data, 255)
    out_data = np.where((out_data < 20) & (out_data > 0), out_data, 255)
    return out_data


def get_story_height_all(floor_root, height_root, save_root):
    make_dir(save_root)
    filepaths, filenames = file_name_tif(floor_root)
    for ii in range(len(filenames)):
        floor_path, floor_name = filepaths[ii], filenames[ii]
        if floor_name == "Lasa":  # 目前GEDI和其他数据还没有下载西北和青藏的数据
            continue
        # if os.path.isfile(os.path.join(save_root, floor_name+'.tif')):
        #     continue
        height_path = os.path.join(height_root, floor_name+'.tif')
        floor_data = read_tif(floor_path)
        height_data = read_tif(height_path)
        story_height_data = get_story_height_data(floor_data, height_data)
        tif.imsave(os.path.join(save_root, floor_name+'.tif'), story_height_data)


def plot_multi_bar(func_list, data_dict, title, save_root):
    """
    这个函数用于打印堆叠柱状图
    """
    # plt.rcParams['font.family'] = ['SimHei']  # 指定中文字体为黑体
    # 读取Excel文件
    # df = pd.read_excel(r'C:\Users\liuchunlin2\Desktop\新建文件夹\新建 XLSX 工作表.xlsx', sheet_name='Sheet3')
    # 设置柱状图的宽度
    bar_width = 0.35
    # 设置x轴的位置
    x = range(len(func_list))
    colors = [
        '#00bfff',
        '#8dd9cc',
        '#cccaa8',
        '#bcd4e6',
        '#ee82ee',
        '#ffc0cb',
        '#a899e6',
        '#fe4eda',
        '#f8de7e',
        '#ffffbf',
        '#d2b48c',
        '#bfafb2',
        '#e5d7bd',
        '#3399ff']
    # 绘制堆叠柱状图
    fig, ax = plt.subplots(figsize=(3.1, 10), dpi=400)

    rects = {}
    if len(data_dict) == 0:
        return
    bottoms = np.zeros_like(data_dict[0][1])
    for ii in range(len(data_dict)):
        story_height = data_dict[ii][0]
        if ii == 0:
            rects[story_height] = ax.bar(x, data_dict[ii][1], bar_width,
                                         color=colors[ii],
                                         label=f"{story_height} m/story")
        else:
            # print(data_dict[ii-1][1])
            bottoms += data_dict[ii - 1][1]
            # print(bottoms)
            rects[story_height] = ax.bar(x, data_dict[ii][1], bar_width,
                                         color=colors[ii],
                                         bottom=bottoms,
                                         label=f"{story_height} m/story")

    # rects1 = ax.bar(x, df['销售数量'], bar_width, label='销售数量')
    # rects2 = ax.bar(x, df['销售数量2'], bar_width, bottom=df['销售数量'], label='销售数量2')

    # 添加标签和标题
    # ax.set_xlabel('Land Use Type')
    # ax.set_ylabel('Story Height Total')
    # ax.set_title(title)
    ax.set_xticks(x)
    ax.set_ylim(0, 100)
    ax.set_xticklabels(func_list, rotation=90)
    ax.set_yticklabels(["0%", "20%", "40%", "60%", "80%", "100%"], rotation=90)
    # ax.legend(ncol=3, loc="upper right")

    # # 在每个柱子上方显示数据标签
    # for k in rects.keys():
    #     rect_ = rects[k]
    #     for rect in rect_:
    #         height = rect.get_height()
    #         ax.annotate(f'{height}', xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, 3),
    #                     textcoords='offset points', ha='center', va='bottom')
    # total_height = 0.0
    # for k in rects.keys():
    #     rect_ = rects[k]
    #     height_ = rect_.get_height()
    #     total_height += height_
    #
    # for rect1, rect2 in zip(rects1, rects2):
    #     height1 = rect1.get_height()
    #     height2 = rect2.get_height()
    #     total_height = height1 + height2
    #     ax.annotate(f'{height2}', xy=(rect2.get_x() + rect2.get_width() / 2, total_height), xytext=(0, 3),
    #                 textcoords='offset points', ha='center', va='bottom')

    # 显示图形
    save_path = make_dir(os.path.join(save_root, "STH_Dist_perc"))
    fig.tight_layout()
    plt.savefig(os.path.join(save_path, f"{title}.jpg"), dpi=400)
    # plt.show()


def dict_to_plot_list(dict_:dict = None):
    """
    dict: {classname: [sths]}
    out: [ [sth: [num's perc in class]] ]
    """
    # count
    num_ = {}
    LEN_count = 0
    count_ids = []
    for class_name in dict_.keys():
        sths = dict_[class_name]
        sths = np.round(sths).astype(np.uint8)
        sths = sths[(sths>0) & (sths <= 6)]
        count_ = count_list(list(sths))
        if len(count_) == 0:
            continue
        count_ = sorted(count_.items(), key=lambda x: x[0])   #[(countid: countnum)]
        for cou in count_:
            count_ids.append(cou[0])
        LEN_count = len(count_)
        num_[class_name] = count_
    sum_ = get_sum_in_class(num_)
    perc_v = [[]] * LEN_count
    for ii in range(LEN_count):
        story_height =count_ids[ii]
        for jj in range(len(num_.keys())):
            k = list(num_.keys())[jj]
            perc_temp = list(num_[k])[ii][1] / sum_[jj]
            perc_temp = np.round(perc_temp * 100, 2)
            # print(perc_temp)
            if jj == 0:
                perc_v[ii] = [story_height, [perc_temp]]
            else:
                # perc_v[ii][0] =
                perc_v[ii][1].append(perc_temp)
    print(perc_v)
    return perc_v, num_


def get_all_dict_by_txt(txt_file):
    sth_dict = np.zeros(len(EULUC_DICT.keys()))
    data_dict = txt_to_dict(txt_root=txt_file, type_dict={"STH": 'float', "GRIDCODE": 'float'})
    # print(data_dict.keys())
    sth_arr = np.array(data_dict['STH'])
    Urban_type_arr = np.array(data_dict['GRIDCODE'])
    for K in EULUC_DICT.keys():
        class_name = EULUC_DICT[K]
        index_ = list(EULUC_DICT.keys()).index(K)
        type_ID = float(K)
        cor_sths = np.round(sth_arr[Urban_type_arr == type_ID]).astype(np.uint8)
        cor_sths = cor_sths[(cor_sths > 0) & (cor_sths <= 6)]
        counts = count_list(list(cor_sths))
        counts = sorted(counts.items(), key=lambda x: x[0])
        print(counts)
        # sth_dict[index_] = counts
    return sth_dict


def get_all_dict_perc_by_txt(txt_file):
    sth_dict = {}
    data_dict = txt_to_dict(txt_root=txt_file, type_dict={"STH": 'float', "GRIDCODE": 'float'})
    # print(data_dict.keys())
    sth_arr = np.array(data_dict['STH'])
    Urban_type_arr = np.array(data_dict['GRIDCODE'])
    for K in EULUC_DICT.keys():
        class_name = EULUC_DICT[K]
        type_ID = float(K)
        cor_sths = np.round(sth_arr[Urban_type_arr == type_ID]).astype(np.uint8)
        cor_sths = cor_sths[(cor_sths > 0) & (cor_sths <= 6)]
        counts = count_list(list(cor_sths))
        counts = sorted(counts.items(), key=lambda x: x[0])
        print(f"{class_name}:", counts)
        if len(counts) == 0:
            continue
        sth_dict[class_name] = counts

    sum_ = get_sum_in_class(sth_dict)
    # perc_ = [] * len(sth_dict["Residential"])
    perc_v = [[]] * len(sth_dict["Residential"])

    for ii in range(len(sth_dict["Residential"])):

        story_height = sth_dict["Residential"][ii][0]
        for jj in range(len(sth_dict.keys())):
            k = list(sth_dict.keys())[jj]
            perc_temp = list(sth_dict[k])[ii][1] / sum_[jj]
            perc_temp = np.round(perc_temp * 100, 2)
            # print(perc_temp)
            if jj == 0:
                perc_v[ii] = [story_height, [perc_temp]]
            else:
                # perc_v[ii][0] =
                perc_v[ii][1].append(perc_temp)
        print(perc_v)
        # perc_[ii] = perc_v
    # print(perc_v, perc_)
    # print("sum:", sum_)
    plot_multi_bar(list(sth_dict.keys()), data_dict=perc_v, title="ShenzhenTest", save_root=r'D:\Dataset\0_Lidar')
    return sth_dict


def get_all_dict_perc_by_txt_2(txt_file):
    sth_dict = {}
    data_dict = txt_to_dict(txt_root=txt_file, type_dict={"STH": 'float', "GRIDCODE": 'float'})
    # print(data_dict.keys())
    sth_arr = np.array(data_dict['STH'])
    Urban_type_arr = np.array(data_dict['GRIDCODE'])
    for K in EULUC_DICT.keys():
        class_name = EULUC_DICT[K]
        type_ID = float(K)
        sth_dict[class_name]=sth_arr[Urban_type_arr == type_ID]

    perc_v, num_ = dict_to_plot_list(sth_dict)
    plot_multi_bar(list(num_.keys()), data_dict=perc_v, title="ShenzhenTest2", save_root=r'D:\Dataset\0_Lidar')
    return sth_dict


def get_sum_in_class(dict_):
    class_sum = np.zeros(len(dict_.keys()))
    index_ = 0
    for class_name in dict_.keys():
        for v in dict_[class_name]:
            # print(v)
            class_sum[index_] += v[1]
        index_ += 1
    return class_sum


def get_mean_dict_by_txt(txt_file):
    sth_dict = {}
    data_dict = txt_to_dict(txt_root=txt_file)
    print(data_dict.keys())
    sth_arr = np.array(data_dict['STH'])
    Urban_type_arr = np.array(data_dict['GRIDCODE'])
    for K in EULUC_DICT.keys():
        class_name = EULUC_DICT[K]
        type_ID = float(K)
        cor_mean_sth = np.round(np.mean(sth_arr[Urban_type_arr==type_ID])).astype(np.uint8)
        sth_dict[class_name] = cor_mean_sth
    return sth_dict


if __name__ == '__main__':

    # get_all_dict_perc_by_txt_2(r'D:\Dataset\0_Lidar\深圳Amap\StoryHeightTable1.txt')

    # get_story_height_all(r'G:\ProductData\61cities_AMAP_Raster_wgs84_10m', r'F:\Data\61CitiesData\GEDI_',
    #                      save_root=r'F:\Data\61CitiesData\StoryHeight')
    D = Distributor(floor_root=r'F:\Data\61CitiesData\StoryHeight',
                    function_root=r'F:\Data\61CitiesData\EULUC_',
                    save_root=r'F:\Data\61CitiesData\statistic_data_storyheight',
                    mode="StoryHeight")

    # D = Distributor(floor_root=r'G:\ProductData\61cities_AMAP_Raster_wgs84_10m',
    #                 function_root=r'F:\Data\61CitiesData\EULUC_',
    #                 save_root=r'F:\Data\61CitiesData\statistic_data',
    #                 mode="Floor")
    D.get_num_all()
    D.get_num_city()
    D.get_num_all_by_class()
    D.get_num_city_by_class()
    # D.plot_dist_all(format_='bar')
    # D.plot_dist_city(format_='bar')
    # D.plot_dist_all_by_class(format_='bar')
    # D.plot_dist_city_by_class(format_='bar')

    # D.get_all_dict_by_sth()
    # D.get_city_dict_by_sth()
    D.get_all_dict_by_sth_in_perc()
    D.get_city_dict_by_sth_in_perc()
    D.plot_dist_all_by_sth()
    D.plot_dist_city_by_sth()
    # all_dict_by_class = D.num_all_by_class


