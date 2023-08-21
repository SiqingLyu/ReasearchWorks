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

def is_NaN(object):
    if object!=object:
        return True
    return False

def main():
    reference_authors = ["陈云浩", "刘慧平", "刘素红", "蒋卫国", "刘宝元", "符素华",
                            "张立强", "董卫华", "朱青", "宫阿都", "黄大全", "潘峰华",
                            "武建军", "唐宏", "李京", "张华", "戴特奇"]
    excelpath = r"D:\Desktop\环境遥感与智慧城市北京市重点实验室统计\学部自导统计表.xlsx"
    author_dict_en = inti_author_dict({}, reference_authors)
    author_dict_cn = inti_author_dict({}, reference_authors)
    excel = pd.read_excel(excelpath)
    titles = excel['题目']
    author_cor = excel['通信作者']
    author_awa = excel['绩效作者']
    assert len(titles)==len(author_awa) and len(author_awa) == len(author_cor)
    for ii in range(len(author_awa)):
        title = titles[ii]
        if is_NaN(author_awa[ii]):
            assert is_NaN(author_cor[ii]) is False, f"第{ii+1}条数据有问题，通讯作者和绩效作者都不存在"
            temp_name = author_cor[ii].split(',')[0]
            if is_contain_chinese(temp_name):
                author = temp_name
        # elif author_awa[ii] not in reference_authors:
        #     temp_name = author_cor[ii].split(',')[0]
        #     if is_contain_chinese(temp_name):
        #         author = temp_name
        else:
            author = author_awa[ii]
        author = author.replace(',', '')
        print(author)
        if author in reference_authors:
            if is_contain_chinese(title):
                author_dict_cn[author].append(title)
            else:
                author_dict_en[author].append(title)


    infos = []
    for ii in range(len(reference_authors)):
        author = reference_authors[ii]
        print(f'{author}老师：有{len(author_dict_cn[author])} 篇中文文章， 有{len(author_dict_en[author])}篇英文文章')
        titles_cn = []
        for item in author_dict_cn[author]:
            titles_cn.append(item)
        titles_en = []
        for item in author_dict_en[author]:
            titles_en.append(item)
        infos.append([author, len(author_dict_cn[author]), str(titles_cn), len(author_dict_en[author]), str(titles_en)])
    # print(np.array(infos))
    df = pd.DataFrame(infos)
    df.to_excel('环境遥感与智慧城市实验室老师文章统计_按照学部导出文件.xls', index=False, header=['姓名', '中文文章数量', '中文文章题目', '英文文章数量', '英文文章题目'], encoding='utf_8_sig')

if __name__ == "__main__":
    main()
