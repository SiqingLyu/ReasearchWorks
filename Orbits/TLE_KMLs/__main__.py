from tle_calc import *
from UpdateTles import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--excel', type=str, default=r"D:\PythonProjects\Arcmap\Orbits\Main\Satellites_info.xls", help="The Satellites' excel path")
    parser.add_argument('--sheet', type=str, default=r"Sheet1", help="The Sheet name of Excel")
    parser.add_argument('--TLEs', type=str, default=r'Satellite_TLEs.json', help="The json file which save the TLEs")
    parser.add_argument('--start', type=str, default=[2024, 1, 1, 0], help="The start time you want satellites to start")
    parser.add_argument('--days', type=str, default=[1, 2, 4, 7], help="The days you want the tracking to last")
    parser.add_argument('--KML', type=str, default='G:\STKDATA\KMLs\WholeThreadTest', help="where you want to save kml")
    args = parser.parse_args()

    start = args.start
    start = start.split(' ')
    days = args.days
    days = days.split(' ')

    start_ = []
    days_ = []
    for s in start:
        if len(s) == 0:
            continue
        start_.append(int(s))
    for d in days:
        if len(d) == 0:
            continue
        days_.append(int(d))

    print("——————————Updating TLE files————————————")
    update_tles(excel_path=args.excel, sheet=args.sheet, json_save_file=args.TLEs)
    print("————————Transfering TLE to KMLs————————")
    tle_kmls(json_file=args.TLEs, start_date=start_, last_days=days_, kml_root=args.KML)
