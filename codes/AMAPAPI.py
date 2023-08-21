import requests
import json
from pymongo import MongoClient
import time

client = MongoClient('localhost', 27017)
db = client.Buildings
collection = db.table_1
polygon_list = list()


with open(r"D:\PycharmProjects\Dataprocess\codes\test.txt", 'r', encoding='UTF-8') as txt_file:
    for each_line in txt_file:
        if each_line != "" and each_line != "\n":
            fields = each_line.split("\n")
            polygon = fields[0]
            polygon_list.append(polygon)
    txt_file.close()

def getjson(polygon, page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
    }
    pa = {
        # 'key': '9605bac4f58bb50d113d0071df7c8646', #从控制台申请
        'key': '508def3891976c0b128e39b5fc469b5a', #从控制台申请
        'polygon': polygon,
        'types':'970000|990000',    #不要过多
        'city':'0531',
        'offset': 20,
        'page': page,
        'extensions': 'all',
        'output': 'JSON'
    }
    # print(polygon)
    r = requests.get(f'https://restapi.amap.com/rest/lbs/geohub/geo/feature/list?polygon={polygon}&key={pa["key"]}')
    decodejson = json.loads(r.text)
    return decodejson

for each_polygon in polygon_list:
    not_last_page = True
    page = 1
    while not_last_page:
        decodejson = getjson(each_polygon, page)
        print(decodejson)
        count = decodejson['count']
        print(each_polygon, page)
        if decodejson['pois']:
            for eachone in decodejson['pois']:
                try:
                    name = eachone['name']          #POI名称
                except:
                    name = None
                try:
                    types = eachone['type']           #POI所属类别
                except:
                    types = None
                try:
                    address = eachone['address']    #POI地址
                except:
                    address = None
                try:
                    loaction = eachone['location']   #POI坐标
                except:
                    loaction = None
                try:
                    city = eachone['cityname']    #城市
                except:
                    city = None
                try:
                    county = eachone['adname']   #区县
                except:
                    county = None
                data={
                    'name':name,
                    'types':types,
                    'address':address,
                    'location':loaction,
                    'city':city,
                    'county':county,
                    'count':count,
                    'polygon':each_polygon
                }
                collection.insert_one(data)
                time.sleep(0.2)
            page += 1
        else:
            not_last_page = False
