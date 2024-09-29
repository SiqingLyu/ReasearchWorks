from tools import *


def main(save_file):
    dict1 = read_json(r'F:\Data\Sentinel-2\China_0p5\total_info_dict.json')
    dict2 = read_json(r'F:\Data\Sentinel-2\China_0p5\total_info_dict2.json')
    dict3 = {}
    for season in ["spring", "summer", "autumn", "winter", "all"]:
        dict3_season = {}
        season_dict1 = dict1[season]
        season_dict2 = dict2[season]
        for lon_lat in season_dict1.keys():
            dict3_season[lon_lat] = season_dict1[lon_lat]
        for lon_lat in season_dict2.keys():
            assert lon_lat not in dict3_season.keys()
            dict3_season[lon_lat] = season_dict2[lon_lat]
        dict3[season] = dict3_season
    write_json(save_file, dict3)


if __name__ == '__main__':
    main(r'F:\Data\Sentinel-2\China_0p5\all_info_dict.json')
