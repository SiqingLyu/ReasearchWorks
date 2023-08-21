import numpy as np
import os
import shapefile


def get_shp_infos(shp_path):
    file = shapefile.Reader(shp_path)
    shapes = file.shapes()  # read all the features
    records = file.records()
    fields = file.fields
    return records, fields


def get_filelist_keywords(data_path, keywords):
    FileList, allFileid = file_name(data_path, suffix = 'shp')
    #keywords = ['after','upper']
    for keyword in keywords:
        FileList_keyword = []
        for file_path in FileList:
            if keyword in file_path:
                FileList_keyword.append(file_path)
        FileList = FileList_keyword
    return FileList


def file_name(file_dir, suffix):
    '''
    eg: Listfile, allFilename = file_name(r'/www/lsq/optical')
    only for shp files
    :param file_dir: str
    :return: two List: a list of file absolute path & a list of file with no suffix
    '''
    if (os.path.isdir(file_dir)):
        L = []
        allFilename = []
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if file.split('.')[-1] != suffix:
                    continue
                formatName = os.path.splitext(file)[1]
                fileName = os.path.splitext(file)[0]
                allFilename.append(fileName)
                if (formatName == ('.' + suffix)):
                    tempPath = os.path.join(root, file)
                    L.append(tempPath)
        return L, allFilename
    else:
        print('must be folder path')


def main(data_path, keywords):
    beforewar_path = get_filelist_keywords(data_path, keywords=keywords)
    beforewar_file = beforewar_path[0]
    records, fields = get_shp_infos(beforewar_file)
    records = np.array(records)
    total_area = 0
    crop_area = 0
    for record in records:

        geoid = record[2]
        shape_area = record[4]
        total_area += shape_area
        if geoid > 0:
            crop_area += shape_area
    print("The crop Area of ", keywords , ":\n"
        ' Crop Area:', crop_area, '\n',
          'Total Area:', total_area, '\n',
          'Rate:  ', crop_area/total_area+1e-10)


if __name__ == '__main__':
    data_path = r'D:\PythonProjects\DataProcess\UkrineAnalysis'
    #keywords = ['beforewar'] # keywords[0]  should be 'beforewar' or 'afterwar'
    keywords_list = [
        ['beforewar'],['afterwar'],
        ['beforewar', 'bottom'],['afterwar', 'bottom'],
        ['beforewar', 'botsmall'],['afterwar', 'botsmall'],
        ['beforewar', 'upper'],['afterwar', 'upper'],
        ['beforewar', 'upsmall'], ['afterwar', 'upsmall']
    ]
    for keywords in keywords_list:
        main(data_path, keywords)