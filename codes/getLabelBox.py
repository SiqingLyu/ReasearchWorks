import tifffile as tif
import numpy as np

BACKGOUND = 0


def get_boxes_maskes(tif_path):
    data = tif.imread(tif_path)  # 读取tif文件
    data_temp = np.copy(data)  # 备份数据
    data_compare = np.copy(data)  # 备份数据
    width = data_temp.shape[0]
    height = data_temp.shape[1]
    boxes = []
    maskes = []
    num = 1
    '''
        以下循环主要思路是：遍历找到第一个不为背景的像素，
        对此像素递归寻找所有相连区域，将区域内每个像素的坐标保存，
        最终得到外接矩形框坐标, 同时获取每个独立区域的mask
    '''
    for i in range(width):
        for j in range(height):
            if data_temp[i][j] != BACKGOUND:
                # 获取当前连通区域的BOX
                xmin, ymin, xmax, ymax, data_temp = find_box(data_temp, i, j)
                if xmin == xmax:
                    continue
                box = [xmin, ymin, xmax, ymax]
                if xmin < 0 :
                    continue
                # 得到mask
                mask = data_temp ^ data_compare  # 异或运算
                data_compare = np.copy(data_temp)
                #保存mask和box
                boxes.append(box)
                maskes.append(mask)
                num += 1

                print("第{0}个对象，矩形框轮廓（xmin, ymin, xmax, ymax）：".format(num), box)

    boxes = np.array(boxes)
    maskes = np.array(maskes)
    return boxes, maskes


def find_box(data, x, y):
    data_temp = np.copy(data)
    x_list, y_list = find_xy(data_temp, x, y)
    xmin = min(x_list)
    xmax = max(x_list)
    ymin = min(y_list)
    ymax = max(y_list)
    return xmin, ymin, xmax, ymax, data_temp


# def find_box_4(data, x, y):
#
#     data_temp = np.copy(data)
#     xmin = find_xmin(data_temp, x, y) + 1
#     data_temp = np.copy(data)
#     xmax = find_xmax(data_temp, x, y) - 1
#     data_temp = np.copy(data)
#     ymin = find_ymin(data_temp, x, y) + 1
#     data_temp = np.copy(data)
#     ymax = find_ymax(data_temp, x, y) - 1
#     return xmin,ymin,xmax,ymax,data_temp


def find_xy(data, x, y, turn_mode = 4):
    '''
    this function is to get all the (x,y) in one conneted region in data field
    for example:
    input:
        data:
            [ [1 1 0 0 0 0 ]
              [0 1 0 0 1 1 ]
              [1 1 0 0 0 1 ]
              [0 0 0 1 0 0 ] ]
        x: 0
        y: 0
    output:
        x_list = [0, 0, 1, 2, 2]
        y_list = [0, 1, 1, 1, 0]
    in this output you can find the coordinates of the Minimum Bounding Rectangle
    :param data: in array type
    :param x: parameter x & y must be a place where data is not 0 if you want to have a result
    :param y:
    :param turn_mode: leave it as a default
    :return:
    '''
    x_list = []
    y_list = []
    while (data[x][y] != BACKGOUND):
        data[x][y] = BACKGOUND
        x_list.append(x)
        y_list.append(y)
        if y + 1 < data.shape[1]:
            if data[x][y+1] != BACKGOUND:
                if turn_mode != 0:
                    x_list_temp, y_list_temp = find_xy(data, x, y+1, 1)
                    x_list += x_list_temp
                    y_list += y_list_temp
        if y + 2 < data.shape[1]:
            if data[x][y+2] != BACKGOUND:
                if turn_mode != 0:
                    x_list_temp, y_list_temp = find_xy(data, x, y+2, 1)
                    x_list += x_list_temp
                    y_list += y_list_temp
        if y - 1 >= 0:
            if data[x][y-1] != BACKGOUND:
                if turn_mode != 1:
                    x_list_temp, y_list_temp = find_xy(data, x, y - 1, 0)
                    x_list += x_list_temp
                    y_list += y_list_temp
        if y - 2 >= 0:
            if data[x][y-2] != BACKGOUND:
                if turn_mode != 1:
                    x_list_temp, y_list_temp = find_xy(data, x, y - 2, 0)
                    x_list += x_list_temp
                    y_list += y_list_temp
        if x + 1 < data.shape[0]:
            if data[x+1][y] != BACKGOUND:
                if turn_mode != 2:
                    x_list_temp, y_list_temp = find_xy(data, x + 1, y, 3)
                    x_list += x_list_temp
                    y_list += y_list_temp
        if x + 2 < data.shape[0]:
            if data[x+2][y] != BACKGOUND:
                if turn_mode != 2:
                    x_list_temp, y_list_temp = find_xy(data, x + 2, y, 3)
                    x_list += x_list_temp
                    y_list += y_list_temp
        if turn_mode != 3:
            if x - 1 <= -1:
                # print("到最上边了")
                x_list.append(0)
            x -= 1
            turn_mode = 2
    return x_list, y_list

# def find_ymax(data, x, y, turn_mode = 4):
#     ymax_bot_temp = 0
#     ymax_up_temp = 0
#     y_back_temp = 0
#
#     while (data[x][y] != BACKGOUND):
#
#         data[x][y] = BACKGOUND
#         # print(x, y)
#         if x + 1 < data.shape[0]:
#             if data[x + 1][y] != BACKGOUND:
#                 if turn_mode != 0:
#                     ymax_bot_temp = find_ymax(data, x+1, y, 1)
#                     # print("向下：",ymax_bot_temp)
#                 # print(ymax_temp)
#         if x - 1 >= 0:
#             if data[x - 1][y] != BACKGOUND:
#                 if turn_mode != 1:
#                     ymax_up_temp= find_ymax(data, x-1, y, 0)
#                     # print("向上：",ymax_up_temp)
#         if y - 1 >= 0 :
#             if data[x][y-1] != BACKGOUND:
#                 if turn_mode != 2:
#                     y_back_temp = find_ymax(data, x, y-1, 3)
#                     # print("向后：",y_back_temp)
#
#         # if y + 1 < data.shape[1]:
#         #     if data[x][y+1] != BACKGOUND:
#         #         if turn_mode != 3:
#         #             ymax_temp= find_ymax(data, x, y+1, 2)
#         #             print("向右：",ymax_temp)
#         if turn_mode != 3:
#             if y + 1 == data.shape[1]:
#                 # print("到最右边了")
#                 return y + 1
#             y+=1
#             turn_mode = 2
#             # print("向右：", y)
#     ymax = max(ymax_bot_temp, ymax_up_temp)
#     ymax = max(ymax, y_back_temp)
#     ymax = max(ymax, y)
#     # print()
#     return ymax
#
#
# def find_ymin(data, x, y, turn_mode = 4):
#     ymin_bot_temp = data.shape[1]
#     ymin_up_temp = data.shape[1]
#     y_back_temp = data.shape[0]
#
#     while (data[x][y] != BACKGOUND):
#
#         data[x][y] = BACKGOUND
#         # print(x, y)
#         if x + 1 < data.shape[0]:
#             if data[x + 1][y] != BACKGOUND:
#                 if turn_mode != 0:
#                     ymin_bot_temp = find_ymin(data, x+1, y, 1)
#                     # print("向下：",ymin_bot_temp)
#         if x - 1 >= 0:
#             if data[x - 1][y] != BACKGOUND:
#                 if turn_mode != 1:
#                     ymin_up_temp= find_ymin(data, x-1, y, 0)
#                     # print("向上：",ymin_up_temp)
#         if y + 1 < data.shape[1] :
#             if data[x][y+1] != BACKGOUND:
#                 if turn_mode != 2:
#                     y_back_temp= find_ymin(data, x, y+1, 3)
#                     # print("向后：",y_back_temp)
#
#         if turn_mode != 3:
#             if y - 1 == -1:
#                 # print("到最左边了")
#                 return y - 1
#             y-=1
#             turn_mode = 2
#             # print("向右：", y)
#     ymin = min(ymin_bot_temp, ymin_up_temp)
#     ymin = min(ymin, y_back_temp)
#     ymin = min(ymin, y)
#     # print()
#     return ymin
#
#
# def find_xmax(data, x, y, turn_mode = 4):
#     xmax_right_temp = 0
#     xmax_left_temp = 0
#     x_back_temp = 0
#
#     while (data[x][y] != BACKGOUND):
#
#         data[x][y] = BACKGOUND
#         # print(x, y)
#         if y + 1 < data.shape[1]:
#             if data[x][y+1] != BACKGOUND:
#                 if turn_mode != 0:
#                     xmax_right_temp = find_xmax(data, x, y+1, 1)
#                     # print("向右", xmax_right_temp)
#                 # print(ymax_temp)
#         if y - 1 >= 0:
#             if data[x][y-1] != BACKGOUND:
#                 if turn_mode != 1:
#                     xmax_left_temp = find_xmax(data, x, y-1, 0)
#                     # print("向左", xmax_left_temp)
#
#         if x - 1 >= 0:
#             if data[x-1][y] != BACKGOUND:
#                 if turn_mode != 2:
#                     x_back_temp = find_xmax(data, x-1, y, 3)
#                     # print("向后：",x_back_temp)
#         if turn_mode != 3:
#             if x + 1 == data.shape[0]:
#                 # print("到最下边了")
#                 return x + 1
#
#             x+=1
#             turn_mode = 2
#     xmax = max(xmax_right_temp, xmax_left_temp)
#     xmax = max(xmax, x_back_temp)
#
#     xmax = max(xmax, x)
#     # print()
#     return xmax
#
#
# def find_xmin(data, x, y, turn_mode = 4):
#     xmin_right_temp = data.shape[0]
#     xmin_left_temp = data.shape[0]
#     x_back_temp = data.shape[1]
#     while (data[x][y] != BACKGOUND):
#         # print("x :", x)
#
#         data[x][y] = BACKGOUND
#         # print(x, y)
#         if y + 1 < data.shape[1]:
#             if data[x][y+1] != BACKGOUND:
#                 if turn_mode != 0:
#                     xmin_right_temp = find_xmin(data, x, y+1, 1)
#                     # print("1", xmin_right_temp)
#                 # print(ymax_temp)
#         if y - 1 >= 0:
#             if data[x][y-1] != BACKGOUND:
#                 if turn_mode != 1:
#                     xmin_left_temp = find_xmin(data, x, y-1, 0)
#                     # print("0", xmin_left_temp)
#         if x + 1 < data.shape[0]:
#             if data[x+1][y] != BACKGOUND:
#                 if turn_mode != 2:
#                     x_back_temp = find_xmin(data, x+1, y, 3)
#                     # print("向后：",y_back_temp)
#         if turn_mode != 3:
#             if x - 1 == -1:
#                 # print("到最上边了")
#                 return x - 1
#             x-=1
#             turn_mode = 2
#
#     xmin = min(xmin_right_temp, xmin_left_temp)
#     xmin = min(xmin, x_back_temp)
#
#     xmin = min(xmin, x)
#     # print()
#     return xmin

if __name__ == '__main__':
    tif_path = 'D:\PythonProjects\DataProcess\Data\label_bkas0\Aomen_0_0.tif'
    boxes, maskes = get_boxes_maskes(tif_path)
    tif.imsave("TEST.tif", maskes)
