#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np
import copy


def get_all_authors(authors_list, reference_authors):
    all_authors = []
    for authors in authors_list:
        temp_authors = authors.split(";")
        for temp_author in temp_authors:
            # temp_author = temp_author.replace(" ", "")
            if temp_author not in all_authors and temp_author in reference_authors:
                all_authors.append(temp_author)
    # print(all_authors)
    # print(len(all_authors))
    return all_authors

def inti_author_dict(author_dict, reference_authors):
    for name in reference_authors:
        author_dict[name] = []
    return author_dict



def find_multi_author(item_arr, reference_authors):
    all_multi_items = []
    all_notmulti_items = []
    for item in item_arr:
        name_list = list(item[2].split(";"))
        reference_authors_temp = copy.copy(reference_authors)
        if_ismulti = False
        # first time find an author
        for author in reference_authors_temp:
            if author in name_list:
                # print(author)
                name_list.remove(author)
                reference_authors_temp.remove(author)
        # second time find an author
        for author in reference_authors_temp:
            if author in name_list:
                # print("++++++++++++")
                if_ismulti = True
                all_multi_items.append(item)
                break

        if if_ismulti is False:
            all_notmulti_items.append(item)
    return all_notmulti_items, all_multi_items

def on_chinese(Chinese_arr, reference_authors_cn):
    author_dict = inti_author_dict({}, reference_authors_cn)
    single_auhtor_items, multi_author_items = find_multi_author(Chinese_arr, reference_authors_cn)
    print(multi_author_items)
    # print(reference_authors)
    for item in single_auhtor_items:
        names = item[2].split(";")
        for author in reference_authors_cn:
            if author in names:
                author_dict[author].append(item)
    # print(author_dict["唐宏"])
    return author_dict


def on_english(English_arr, reference_authors_en):
    author_dict = inti_author_dict({}, reference_authors_en)
    single_auhtor_items, multi_author_items = find_multi_author(English_arr, reference_authors_en)
    print(multi_author_items)
    # print(reference_authors)
    for item in single_auhtor_items:
        names = item[1].split(";")
        for author in reference_authors_en:
            if author in names:
                author_dict[author].append(item)
    # print(author_dict["Tang,Hong"])
    return author_dict


def is_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def main():
    reference_authors_cn = ["陈云浩", "刘慧平", "刘素红", "蒋卫国", "刘宝元", "符素华",
                            "张立强", "董卫华", "朱青", "宫阿都", "黄大全", "潘峰华",
                            "武建军", "唐宏", "李京", "张华", "戴特奇"]
    reference_authors_en = ["Chen,Yunhao", "Liu,Huiping", "Liu,Suhong", "Jiang,Weiguo", "Liu,Baoyuan", "Fu,Suhua",
                            "Zhang,Liqiang", "Dong,Weihua", "Zhu,Qing", "Gong,Adu", "Huang,Daquan", "Pan,Fenghua",
                            "Wu,Jianjun", "Tang,Hong", "Li,Jing", "Zhang,Hua", "Dai,Teqi"]
    Chinese_excelpath = r"D:\Desktop\环境遥感与智慧城市北京市重点实验室统计\20221026环境遥感发表中文文章目录.xlsx"
    English_excelpath = r"D:\Desktop\环境遥感与智慧城市北京市重点实验室统计\2017-2022BeijingKeyLab_forRSE&DC4.xls"
    Chinese_excel = pd.read_excel(Chinese_excelpath)
    English_excel = pd.read_excel(English_excelpath)
    for ii in range(len(English_excel['Authors'])):
        item =  English_excel['Authors'][ii]
        English_excel['Authors'][ii] = item.replace(" ", "")
    # get_all_authors(English_excel["Authors"])
    Chinese_arr = np.array(Chinese_excel)
    English_arr = np.array(English_excel)
    Chinese_author_dict = on_chinese(Chinese_arr, reference_authors_cn)
    English_author_dict = on_english(English_arr, reference_authors_en)
    infos = []
    for ii in range(len(reference_authors_cn)):
        author_cn = reference_authors_cn[ii]
        author_en = reference_authors_en[ii]
        print(f'{author_cn}老师：有{len(Chinese_author_dict[author_cn])} 篇中文文章， 有{len(English_author_dict[author_en])}篇英文文章')
        titles_cn = []
        for item in Chinese_author_dict[author_cn]:
            title = item[1]
            titles_cn.append(title)
        titles_en = []
        for item in English_author_dict[author_en]:
            title = item[2]
            titles_en.append(title)
        infos.append([author_cn, len(Chinese_author_dict[author_cn]), str(titles_cn), len(English_author_dict[author_en]), str(titles_en)])
    # print(np.array(infos))
    df = pd.DataFrame(infos)
    df.to_excel('环境遥感与智慧城市实验室老师文章统计.xls', index=False, header=['姓名', '中文文章数量', '中文文章题目', '英文文章数量', '英文文章题目'], encoding='utf_8_sig')

if __name__ == "__main__":
    main()
