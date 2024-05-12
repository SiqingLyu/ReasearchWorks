# coding=UTF-8
import PySimpleGUI as sg
import os
import webbrowser
import time


def trans_list_to_str(l, split=' '):
    s = '"'
    for item in l:
        s += str(item) + split
    # s = s[-1]
    s += '"'
    return s


if __name__ == '__main__':

    ARCPY_PATH = r'D:\ArcGIS\arcgis10.2\ArcGIS10.2\python.exe'
    sg.theme('LightGreen')
    # 窗体界面布局
    # 此处InputText、Input、I都表示输入文本框
    layout = [
        [sg.Text('请输入数据', size=(40, 1), justification='center')],
        [sg.Text('卫星数据excel文件： ', size=(15, 1)), sg.InputText(size=(30, 1), key='excel_path')],
        [sg.Text('保存文件位置：      ', size=(15, 1)), sg.InputText(size=(30, 1), key='save_root')],
        [sg.Text('灾害名称：          ', size=(15, 1)), sg.InputText(size=(30, 1), key='disaster_name')],
        [sg.Text('规划开始日期：      ', size=(15, 1)), sg.InputText(size=(30, 1), key='start_date')],
        [sg.Text('规划天数：          ', size=(15, 1)), sg.InputText(size=(30, 1), key='days')],
        [sg.Text('要求最小分辨率：     ', size=(15, 1)), sg.InputText(size=(30, 1), key='min_res')],
        [sg.Text('索取范围（Lon_min, Lat_min, Lon_max, Lat_max）： ', size=(50, 1))],
        [sg.InputText(size=(55, 1), key='range_locs')],
        [sg.Text('灾害中心位置：       ', size=(15, 1)), sg.InputText(size=(30, 1), key='disaster_location')],
        [sg.Button('确定', size=(15, 1), key='start_button'), sg.Button('取消', size=(10, 1), key='cancel_button'),
         sg.Text(' ', size=(10, 1)), sg.Button('更改arcpy设置', size=(10, 1), key='arcpy_change')]

    ]

    # 窗体显示
    window = sg.Window('面向巴基斯坦灾害应急响应的卫星轨道统计系统', layout)

    # 消息循环
    while True:
        event, values = window.read(timeout=20)
        # print(event,values)
        if event == 'Exit' or event == sg.WIN_CLOSED or event == 'cancel_button':
            break
        if event == 'arcpy_change':
            ARCPY_PATH = sg.popup_get_file('Please enter the python.exe path of arcpy')
        if event == 'start_button':
            start_time = time.time()

            excel_path = values['excel_path']
            save_root = values['save_root']
            disaster_name = values['disaster_name']
            start_date = '"' + values['start_date'] + '"'
            days = '"' + values['days'] + '"'
            min_res = values['min_res']
            range_locs = '"' + values['range_locs'] + '"'
            disaster_location = '"' + values['disaster_location'] + '"'

            sg.popup('数据输入成功，程序开始运行')
            cmd = rf"{ARCPY_PATH} Main " \
                  rf"--excel_path {excel_path} --save_root {save_root} --disaster_name {disaster_name} --start_date {start_date} " \
                  rf"--days {days} --min_res {min_res} --range_locs {range_locs} --disaster_location {disaster_location}"
            os.system(cmd)

            sg.popup('程序执行完成！')
            html_path = os.path.join(save_root, disaster_name+'.html')
            html_file_path = os.path.abspath(html_path)
            webbrowser.open('file://' + html_file_path)

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"程序运行时间：{elapsed_time}秒")
            # break

    window.close()
