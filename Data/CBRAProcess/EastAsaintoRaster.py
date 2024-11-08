from tools import *
import os
ResOUT = 8.9831528e-005


class EastAsian:
    def __init__(self, root=''):
        self.root = root
        self.region_root = ''
        self.shp_paths = []
        self.bboxes = {}
        self.clip_fishnets = {}

    def get_all_shps(self, region='China'):
        self.region_root = os.path.join(self.root, region)
        self.shp_paths = get_all_filenames(self.region_root, suffix='shp')
        return self.shp_paths

    def get_all_bbox(self):
        if len(self.shp_paths) == 0:
            return
        for shp_path in self.shp_paths:
            # shp_name = os.path.split(shp_path)[1]
            bbox = get_bbox(shp_path)
            self.bboxes[shp_path] = bbox
        return self.bboxes

    def to_10m_res(self, save_root):
        make_dir(save_root)
        index_ = 0
        for shp in self.shp_paths:
            index_ += 1
            print "{},  {} / {}".format(shp, index_, len(self.shp_paths))
            name_ = os.path.split(shp)[1]
            out_raster = os.path.join(save_root, name_.replace('shp', 'tif'))
            arcpy.FeatureToRaster_conversion(shp, "STATUS", out_raster, 10)

    def get_grids_for_each(self, fishnet_root):
        self.get_all_bbox()
        fishnet_files = get_all_filenames(fishnet_root, suffix='shp')
        index_i = 0
        for shp_path in self.bboxes.keys():
            index_i += 1

            # if index_i > 340:
            #     break
            if index_i != 261:
                continue

            print "processing {} / {} shpfile".format(index_i, len(self.bboxes.keys()))
            shp_bbox = self.bboxes[shp_path]
            self.clip_fishnets[shp_path] = []
            for fishnet_file in fishnet_files:
                fishnet_box = get_bbox(fishnet_file)
                if if_rectanle1_in_rectangle2(fishnet_box, shp_bbox) or if_rectanle1_in_rectangle2(shp_bbox, fishnet_box):
                    self.clip_fishnets[shp_path].append(fishnet_file)
            if not self.clip_fishnets[shp_path]:
                print shp_path, self.bboxes[shp_path]
        # print len(self.clip_fishnets)

    def clip_all(self, save_root):
        make_dir(save_root)
        ind = 0
        for shp_path in self.clip_fishnets.keys():
            ind += 1
            fishnets = self.clip_fishnets[shp_path]
            print "{}  {}/{}".format(shp_path, ind, len(self.clip_fishnets.keys()))
            for fishnet_path in fishnets:
                fishnet_name = os.path.split(fishnet_path)[1].split('.')[0]
                shp_name = os.path.split(shp_path)[1].split('.')[0]
                save_file = os.path.join(save_root, "{}_{}.shp".format(shp_name, fishnet_name))
                if os.path.isfile(save_file):
                    continue
                arcpy.Clip_analysis(shp_path, fishnet_path, save_file)


def to_wgs84_dir(filedir, save_root):
    make_dir(save_root)
    out_CS = arcpy.SpatialReference('WGS 1984')

    filepaths, filenames = file_name_shp(filedir)
    # filepaths = get_all_filenames(filedir, suffix='shp')
    for ii in range(len(filepaths)):
        filepath = filepaths[ii]
        filename = filenames[ii]
        print filepath.decode('gbk') + "{} /{}".format(ii+1, len(filepaths))
        spatial_ref = arcpy.Describe(filepath).spatialReference
        save_path = os.path.join(save_root, filename + '.shp')
        if os.path.isfile(save_path):
            continue

        if 'GCS_WGS_1984' not in spatial_ref.exportToString().split('[')[1].split(',')[0]:
            # pass
            print u"Projecting  " + filename.decode('gbk')
            arcpy.Project_management(filepath, save_path, out_CS)
        else:
            for suffix in ['.dbf', '.prj', '.shp', '.shp.xml', '.shx', '.sbn', '.sbx']:
                from_file = filepath.replace('.shp', suffix)
                print from_file, save_root
                if os.path.isfile(from_file):
                    mycopyfile(from_file, save_root)


def to_wgs84_all(fileroot):
    filepaths = get_all_filenames(fileroot, suffix='shp')
    for ii in range(len(filepaths)):
        filepath = filepaths[ii]
        spatial_ref = arcpy.Describe(filepath).spatialReference
        # print(spatial_ref.exportToString().split('[')[1].split(',')[0])
        if 'GCS_WGS_1984' not in spatial_ref.exportToString().split('[')[1].split(',')[0]:
            print(spatial_ref.exportToString().split('[')[1].split(',')[0])
            print filepath
            # for suffix in ['dbf', 'prj', 'shp', 'shp.xml', 'shx']:
            #     from_file = filepath.replace('shp', suffix)
            #     mymovefile(from_file, r'G:\ProductData\GABLE_prj2000')


if __name__ == '__main__':
    # to_wgs84_dir(r'G:\ProductData\East_Asian_buildings\China_city', r'G:\ProductData\East_Asian_buildings\China_wgs84')
    # to_wgs84_all(r'G:\ProductData\East_Asian_buildings\China_wgs84')
    # files = get_all_filenames(r'G:\ProductData\East_Asian_buildings\China_wgs84', suffix='shp')
    # print len(files)

    # bbox1 = get_bbox(r'G:\ProductData\GABLE_fishnet_0p5\85p0_28p8_85p5_29p3.shp')
    # bbox2 = get_bbox(r'G:\ProductData\East_Asian_buildings\China_wgs84\Shigatse.shp')
    # print if_rectanle1_in_rectangle2(bbox1, bbox2)
    EA = EastAsian(root=r'G:\ProductData\East_Asian_buildings')
    EA.get_all_shps(region='China_wgs84')
    EA.get_grids_for_each(fishnet_root=r'G:\ProductData\GABLE_fishnet_0p5')
    EA.clip_all(save_root=r'G:\ProductData\East_Asian_buildings\China_0p5')

    # EA.to_10m_res(save_root=r'G:\ProductData\East_Asian_buildings\China_10m')
    # res = get_all_filenames(r'G:\ProductData\East_Asian_buildings\China', suffix='shp')
    # print res