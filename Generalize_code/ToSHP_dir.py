from tools import *


def to_shp_outside(file_path, save_path):
    ARCPY_PATH = r'D:\ArcGIS\arcgis10.2\ArcGIS10.2\python.exe'
    cmd = rf"{ARCPY_PATH} to_shp.py " \
          rf"--save_path {save_path} --file_path {file_path}"
    os.system(cmd)


def to_shp_dir(dpath, save_root):
    make_dir(save_root)
    paths, names = file_name_tif(dpath)
    for ii in range(len(paths)):
        print("processing {}/{}".format(ii, len(paths)))
        file_path = paths[ii]
        file_name = names[ii]
        file_data = read_tif(file_path)
        if np.nanmax(file_data) == np.nanmin(file_data):
            continue
        save_path = os.path.join(save_root, file_name.replace('.', 'p') + '.shp')
        to_shp_outside(file_path, save_path)


if __name__ == '__main__':
    year = 2021
    to_shp_dir(r'G:\ProductData\CBRA\CBRA_{}_10m'.format(year),
               save_root=r'G:\ProductData\CBRA\CBRA_{}_10m_shp'.format(year))