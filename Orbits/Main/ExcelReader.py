# -*- coding: utf-8 -*-
import xlrd
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def read_excel_xls(path, sheet_name):
    workbook = xlrd.open_workbook(path, encoding_override='utf-8')  # 打开工作簿
    sheets = workbook.sheet_names()  # 获取工作簿中的所有表格
    assert sheet_name in sheets
    worksheet = workbook.sheet_by_name(sheet_name)  # 获取工作簿中所有表格中的的第一个表格
    # worksheet.encoding = 'utf-8'
    return worksheet
    # for i in range(0, worksheet.nrows):
    #     for j in range(0, worksheet.ncols):
    #         print(worksheet.cell_value(i, j), "\t", end="")  # 逐行逐列读取数据
    #     print()


def replace_ascs(s):
    ascs=['\xc2', '\xa0']
    for asc in ascs:
        s = s.replace(asc, '')
    return s


def read_xls_as_list(path, sheet):
    data = read_excel_xls(path, sheet)
    rowAmount = data.nrows
    colAmount = data.ncols
    info_list = [[]]
    for rowIndex in range(rowAmount):
        for colIndex in range(colAmount):
            s = str(data.cell_value(rowIndex, colIndex))
            info_list[rowIndex].append(replace_ascs(s))
            if ('\\' in s) & ('\n' not in s):
                print s + "has unknown chars"
        info_list.append([])
    return info_list


def read_xls_for_orbits(path, sheet):
    info_list = read_xls_as_list(path, sheet)
    widths_dict = {}
    dome_widths_dict = {}
    fore_widths_dict = {}
    res_dict = {}
    for info in info_list:
        if len(info) == 0:
            continue
        if info[0] == 'Name':
            continue
        if (len(info[2]) < 1) & (len(info[3]) < 1):
            continue

        name = info[0].replace('-', '_')
        name = name.replace(' ', '')

        if len(info[2]) != 0:  # OPT
            res_dict[name] = float(info[2])
            if info[1] == "Chinese":
                dome_widths_dict[name] = float(info[4])
            else:
                fore_widths_dict[name] = float(info[4])
        else:
            res_dict[name] = float(info[3])
            if info[1] == "Chinese":
                dome_widths_dict[name] = float(info[5])
            else:
                fore_widths_dict[name] = float(info[5])
    widths_dict.update(dome_widths_dict)
    widths_dict.update(fore_widths_dict)
    return widths_dict, res_dict, dome_widths_dict, fore_widths_dict


if __name__ == '__main__':
    a, b, c, d = read_xls_for_orbits(r'.\Satellites_info.xls', "Sheet1")
    print a,b,c,d
    # print len(a.keys()), len(b.keys()), len(c.keys()), len(d.keys())
    # print a['GF_6'], b['GF_6']
