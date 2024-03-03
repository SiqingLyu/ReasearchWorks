import tifffile as tif
from tools import *
import os
import numpy as np
# import shapefile as shpf
import gc

# class CBRA_Fishnet:
#     def __init__(self, file_path):
#         self.file_path = file_path
#         self.data = shpf.Reader(fr"file_path", encoding='utf-8')
#
#     def get_start_pos(self):
#         shapes = self.data.shape(0)
#         bbox = shapes.bbox
#         print(bbox)


class CBRA_Checker:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = tif.imread(file_path)
        self.checked_points = 0

    def check_empty(self):
        if np.all(self.data == 0):
            return True
        else:
            # print(f"building pixels:{len(self.data[self.data==255])}")
            return False

    def check_glue(self, bin=500, too_big_area_thd=500):
        data = np.copy(self.data)
        check_results = np.zeros_like(data)
        height = data.shape[0]
        width = data.shape[1]
        from_h = 0
        to_h = 0
        from_w = 0
        to_w = 0

        while (from_h + bin) <= height:
            to_h = from_h + bin
            while (from_w + bin) <= width:
                to_w = from_w + bin
                data_temp = data[from_h: to_h, from_w: to_w]
                checked_data = self.check_glue_sample(data=data_temp, thd=too_big_area_thd)
                check_results[from_h: to_h, from_w: to_w] = checked_data
                from_w += bin
            from_h += bin

        # TODO: 将边界区域也纳入进来

        return check_results

    def check_glue_sample(self, data, thd):
        thd_mask = np.zeros_like(data)
        L = LabelTarget(label_data=data)
        T = L.to_target_cpu()
        if T is not None:
            areas, masks = T["area"], T["masks"]
            for ii in range(len(areas)):
                area = areas[ii]
                if area > thd:
                    self.checked_points += 1
                    mask = masks[ii]
                    thd_mask[mask] = 1
        del L
        del T
        return thd_mask


def main(file_root: str = r''):
    with open("/www/lsq/CBRA_glued_info.txt", "w") as f:
        file_paths, file_names = file_name_tif(file_root)
        save_path = r'/www/lsq/CBRA_gluecheck'
        # empty_files = []
        checked_points_all = 0
        for ii in range(len(file_paths)):
            file_path = file_paths[ii]
            file_name = file_names[ii]
            print(f'processing {file_path}')

            # if os.path.isfile(rf'{save_path}\{file_name}.tif'):
            #     continue

            Checker = CBRA_Checker(file_path=file_path)
            check_results = Checker.check_glue(bin=100, too_big_area_thd=500)
            if not np.all(check_results == 0):
                # tif.imwrite(rf'{save_path}\{file_name}.tif', data=check_results)
                print(f"{file_path} has {Checker.checked_points} glued places")
                f.write(f"{file_path} has {Checker.checked_points} glued places\n")
                checked_points_all += Checker.checked_points
            del check_results
            del Checker
            gc.collect()
            # if Checker.check_empty():
            #     empty_files.append(file_path)
            #     print(f'processing {file_path} is empty')
        f.write(f"In total, {checked_points_all} glued places\n")

        # print(empty_files)


if __name__ == '__main__':
    main(r'/www/lsq/CBRA_2018')