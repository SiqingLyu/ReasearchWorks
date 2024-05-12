from Visualizer import *
import argparse
import datetime as dt
from tools import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--range', type=str, default=r"test.shp", help="The range shp path")
    parser.add_argument('--location', type=str, default="35 73 ", help="The map center")
    parser.add_argument('--Satellites', type=str, default=r"all_path", help="All satellite tracks shp path")
    parser.add_argument('--start', type=str, default="2024 1 1 0 ",
                        help="The start time you want satellites to start")
    parser.add_argument('--days', type=str, default="1 2 4 7 ", help="The days you want the tracking to last")
    parser.add_argument('--name', type=str, default="Test", help="The disaster name")
    parser.add_argument('--save_path', type=str, default="Test", help="The save path name")
    parser.add_argument('--Fore_names', type=str, default="A B", help="The names of the other satellites")
    args = parser.parse_args()

    start = args.start
    start = trans_str_to_list(start, split=' ', typename='int')
    days = args.days
    days = trans_str_to_list(days, split=' ', typename='int')
    location = args.location
    location = trans_str_to_list(location, split=' ', typename='float')
    Fore_names = args.Fore_names
    Fore_names = trans_str_to_list(Fore_names, split=' ', typename='str')

    V = Visualizer(location=location, title=f'Satellite tracks in {args.name}', zoom_start=4, crs='EPSG3857')
    V.load_esri()
    V.add_point(location=location, name=f'{args.name}', color="red")
    V.add_style(fill_color='white', boarder_color='black', weight=4, fill_transparency=0.0, style_sort='ROI')
    V.add_style(fill_color='black', boarder_color='grey', weight=3, fill_transparency=0.03, style_sort='Other')
    V.add_style(fill_color='red', boarder_color='grey', weight=2, fill_transparency=0.04, style_sort='China')
    V.add_shp(shp_path=args.range, name="Intrested Area", style_sort="ROI", if_show=True)
    start_dt = dt.datetime(start[0], start[1], start[2], start[3])  # 日期，list格式，到小时
    # html_save_path = make_dir(os.path.join(args.save_path, f"{start_dt.date()}_{end_dt.date()}"))
    for day_num in days:
        end_dt = start_dt + dt.timedelta(days=day_num)
        satellite_path = make_dir(os.path.join(args.Satellites, f"{start_dt.date()}_{end_dt.date()}"))
        filepaths, filenames = file_name_shp(satellite_path)
        for ii in range(len(filenames)):
            filepath = filepaths[ii]
            filename = filenames[ii]
            if not check_shp_file(filepath):
                continue
            satellite_name = filename.split('_')[0]
            if satellite_name in Fore_names:
                V.add_shp(shp_path=filepath, name='{}-{} Apr, {} Track'.format(start_dt.date(), end_dt.date(), filename),
                          style_sort="Other", if_show=True if day_num == days[0] else False)
            else:
                V.add_shp(shp_path=filepath, name='{}-{} Apr, {} Track'.format(start_dt.date(), end_dt.date(), filename),
                          style_sort="China", if_show=True if day_num == days[0] else False)
    V.save_map(f'{os.path.join(args.save_path)}.html')