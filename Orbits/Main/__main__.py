from WholeThread import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--excel_path', type=str)
    parser.add_argument('--save_root', type=str)
    parser.add_argument('--disaster_name', type=str)
    parser.add_argument('--start_date', type=str)
    parser.add_argument('--days', type=str)
    parser.add_argument('--min_res', type=str)
    parser.add_argument('--range_locs', type=str)
    parser.add_argument('--disaster_location', type=str)
    args = parser.parse_args()

    excel_path = args.excel_path
    save_root = args.save_root
    disaster_name = args.disaster_name
    start_date = trans_str_to_list(args.start_date, typename="int")
    days = trans_str_to_list(args.days, typename="int")
    min_res = float(args.min_res)
    range_locs = [trans_str_to_list(args.range_locs, typename="float")]
    disaster_location = trans_str_to_list(args.disaster_location, typename="float")

    to_dates = []
    kml_root = os.path.join(save_root, 'KMLs')
    html_save_path = save_root
    kml_path = make_dir(os.path.join(kml_root, disaster_name))

    Widths, RES, Dome_widths, Fore_widths = read_xls_for_orbits(excel_path, "Sheet1")

    # Update TLE and generate KML
    start_date_str = trans_list_to_str(start_date)
    days_str = trans_list_to_str(days)
    cmd = r"python TLE_KMLs " \
          r"--excel {} --start {} --days {} --KML {}".format(excel_path, start_date_str, days_str, kml_path)
    os.system(cmd)

    # The other process all below
    start_dt = dt.datetime(start_date[0], start_date[1], start_date[2], start_date[3])  # 日期，list格式，到小时
    for day_num in days:
        end_dt = start_dt + dt.timedelta(days=day_num)
        to_dates.append(end_dt.date())
    O = OrbitsThread(name=disaster_name, kml_root=kml_root, from_date=start_dt.date(), to_dates=to_dates,
                     min_res=min_res, range_locs=range_locs, Widths=Widths, RES=RES, Dome_widths=Dome_widths, Fore_widths=Fore_widths)
    O.whole_thread()

    # Visualization
    Fore_names_str = trans_list_to_str(Fore_widths.keys())
    disaster_location_str = trans_list_to_str(disaster_location)
    range_path = os.path.join(kml_root.replace('KMLs', 'SHPs'), "Range", "{}.shp".format(disaster_name))
    satellite_root = os.path.join(kml_path.replace('KMLs', 'RESULTs'), "Buffer_minres{}".format(min_res))
    make_dir(html_save_path)
    html_save_path = os.path.join(html_save_path, '{}'.format(disaster_name))
    print 'HTML File have been saved to {}'.format(html_save_path)
    cmd = r"python OrbitalVision " \
          r"--name {} --range {} --location {} --Satellites {} --start {} --days {} --save_path {} " \
          r"--Fore_names {}".format(disaster_name, range_path, disaster_location_str, satellite_root,
                                    start_date_str, days_str, html_save_path, Fore_names_str)
    os.system(cmd)