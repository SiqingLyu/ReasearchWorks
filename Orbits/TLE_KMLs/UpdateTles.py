import json
import requests
import argparse
import os
from ExcelReader import *


def download_tle(tle_urls, save_file):
    tle_json = []
    print(f"Downloading TLEs, please wait ......")
    for url in tle_urls:
        # print(f"requiring from {url}")
        request = requests.get(url)
        tmp_dict = {}
        name = url.split('NAME=')[1].split('&')[0]

        if len(request.text.split('\n')) < 3:
            print(f"Can not find TLE for {name}")
            continue
        for i in request.text.split('\n'):
            try:
                if i[0] == '1':
                    tmp_dict['tle_1'] = i.strip()
                elif i[0] == '2':
                    tmp_dict['tle_2'] = i.strip()
                else:
                    tmp_dict['satellite_name'] = i.strip()

                if "tle_1" in tmp_dict and "tle_2" in tmp_dict and "satellite_name" in tmp_dict:
                    tle_json.append(tmp_dict)
                    tmp_dict = {}
                else:
                    pass
            except:
                pass
    with open(f'{save_file}', 'w') as f:
        json.dump(tle_json, f, indent=3)
        print(f'[+] Downloaded TLE data in {save_file}')


def update_tles(excel_path, sheet, json_save_file):
    if not os.path.isfile(excel_path):
        print(f"{excel_path} does not exist!")
        pass
    else:
        sat_list = read_xls_as_list(excel_path, sheet)

        urls = []
        for sat in sat_list:
            if len(sat) == 0:
                continue
            if sat[0] == 'Name':
                continue
            urls.append(f'https://celestrak.org/NORAD/elements/gp.php?NAME={sat[0]}&FORMAT=TLE')
        download_tle(urls, json_save_file)

