from tools import *


BF_city_dict = {
    "Beijing": ['Beijing'],
    "Jiangsu": ['Nanjing', 'Changzhou', 'Suzhou', 'Yangzhou', 'Nantong', 'Wuxi', 'Xuzhou'],
    "Tianjin": ['Tianjin'],
    "Guangdong": ['Guangzhou', 'Shenzhen', 'Dongguan', 'Foshan', 'Huizhou', 'Shantou', 'Zhongshan', 'Zhuhai'],
    "Chongqing": ['Chongqing'],
    "Heilongjiang": ['Harbin'],
    "Zhejiang": ['Hangzhou', 'Ningbo', 'Taizhou', 'Wenzhou', 'Jinhua', 'Jiaxing', 'Shaoxing'],
    "Yunnan": ['Kunming'],
    "Jiangxi": ['Nanchang'],
    "Shanghai": ['Shanghai'],
    "Hubei": ['Wuhan'],
    "Fujian": ['Xiamen', 'Fuzhou', 'Quanzhou'],
    "Shaanxi": ['Xian'],
    "Henan": ['Zhengzhou', 'Luoyang'],
    "HK_Macau": ['Macau', 'Hongkong'],
    "Hebei": ['Baoding', 'Shijiazhuang', 'Tangshan'],
    "Jilin": ['Changchun'],
    "Hunan": ['Changsha'],
    "Sichuan": ['Chengdu'],
    "Liaoning": ['Dalian', 'Shenyang'],
    "Neimenggu": ['Ordos', 'Hohhot'],
    "Guizhou": ['Guiyang'],
    "Hainan": ['Haikou', 'Sanya'],
    "Anhui": ['Hefei', 'Wuhu'],
    "Shandong": ['Jinan', 'Qingdao'],
    "Gansu": ['Lanzhou'],
    "Xizang": ['Lhasa'],
    "Guangxi": ['Nanning'],
    "Shanxi": ['Taiyuan'],
    "Qinghai": ['Xining'],
    "Ningxia": ['Yinchuan']
}

name_change_dict = {
    "Harbin": "Haerbin",
    "Macau": "Aomen",
    "Hongkong": "Xianggang",
    "Ordos": "Eerduosi",
    "Hohhot": "Huhehaote",
    "Lhasa": "Lasa"
}


def clip_3D_folder(BF_root, save_root):
    for province in BF_city_dict.keys():
        assert os.path.exists(r'{}\{}.shp'.format(BF_root, province.lower())), province
        for city in BF_city_dict[province]:
            clip_file = r'D:\Dataset\@62allcities\ClipROI\{}.shp'.format(city)
            if not os.path.isfile(clip_file):
                clip_file = r'D:\Dataset\@62allcities\ClipROI\{}.shp'.format(name_change_dict[city])
            assert os.path.isfile(clip_file)

            # tar_file = r'{}\{}\{}.shp'.format(BF_root, province, city)
            tar_file = r'{}\{}.shp'.format(BF_root, province.lower())
            # tar_file = r'{}\{}\{}.shp'.format(projected_root, province, city)
            # if province == "Hainan":
            #     tar_file = r'{}\{}\{}.shp'.format(BF_root, province, province)
            assert os.path.exists(tar_file), tar_file

            print u"CLIPPING  " + clip_file
            save_path = os.path.join(save_root, city + ".shp")
            if os.path.isfile(save_path):
                continue
            print clip_file, tar_file, save_path
            arcpy.Clip_analysis(tar_file, clip_file, save_path)


def clip_GABLE_folder(GABLE_root, save_root):
    for province in BF_city_dict.keys():
        # assert os.path.exists(r'{}\{}.shp'.format(BF_root, province.lower())), province
        for city in BF_city_dict[province]:

            clip_file = r'D:\Dataset\@62allcities\ClipROI\{}.shp'.format(city)
            # print clip_file

            if not os.path.isfile(clip_file):
                clip_file = r'D:\Dataset\@62allcities\ClipROI\{}.shp'.format(name_change_dict[city])
            assert os.path.isfile(clip_file)

            tar_dir = r'{}\{}'.format(GABLE_root, city)
            if not os.path.isdir(tar_dir):
                tar_dir = r'{}\{}'.format(GABLE_root, name_change_dict[city])
            assert os.path.isdir(tar_dir)

            shp_files, _ = file_name_shp(tar_dir)
            tar_file = r''
            for file_path in shp_files:
                if file_path.endswith("_all.shp"):
                    tar_file = file_path

            # assert os.path.exists(tar_file), tar_file

            print u"CLIPPING  " + clip_file
            save_path = os.path.join(save_root, city + ".shp")
            if os.path.isfile(save_path):
                continue
            print clip_file, tar_file, save_path
            arcpy.Clip_analysis(tar_file, clip_file, save_path)


def check_proj(folder):
    BF_project = arcpy.SpatialReference('GCS WGS 1984')

    unprojected_root = make_dir(r'F:\Data\3DGLOBFP\China\not_wgs84')
    not_this_proj_files = check_proj_folder(folder, suffix='shp', tar_proj='GCS_WGS_1984')
    if len(not_this_proj_files) > 0:
        for filepath in not_this_proj_files:
            file_name = os.path.split(filepath)[-1]
            for suffix in ['.dbf', '.prj', '.shp', '.shp.xml', '.shx', '.sbn', '.sbx']:
                from_file = filepath.replace('.shp', suffix)
                print from_file, unprojected_root
                if os.path.isfile(from_file):
                    mymovefile(from_file, unprojected_root)

            tar_file = os.path.join(unprojected_root, file_name)
            print u"Projecting  " + filepath
            arcpy.Project_management(tar_file, filepath, BF_project)


if __name__ == '__main__':
    BF_root = r'F:\Data\3DGLOBFP\China\CHINA'
    # save_root = make_dir(r'F:\Data\3DGLOBFP\China\61cities')
    GABLE_root = r'G:\ProductData\61cities\GABLE\GABLE_61cities'
    save_root = make_dir(r'G:\ProductData\61cities\GABLE_61cities_clip_by_AMAPROI')
    clip_GABLE_folder(GABLE_root, save_root)