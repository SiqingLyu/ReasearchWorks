"""
This code is designed to transfer problems and conditions that can fit into NSGA-II from
human-style information.
The code needs a json file as input, where satellite tle information are stored as a dict-list,
e.g., "../Satellite_TLEs.json"
@ Lyu siqing
@ 2024/5/8
"""
import ephem
import datetime as dt
from tools import *
import json


class InfosTransformer:
    """
    inputs human-style information of satellites, missions and emergencies.
    outputs the best observe plan in a week.
    """
    def __init__(self, satellites: list = None, satellite_infos: dict = None,
                 daily_missions: dict = None, emergencies: list = None,
                 save_root: str = "test_folder"):
        """
        :param satellites: a list of dict which includes satellite name and TLE
        :param satellite_infos: a dict of dict which includes satellite [Resolution, Width, Type(SAR or OPT)]
        :param daily_missions: {"satellite": [positions]}
        :param emergencies: [positions]
        """
        self.satellites = satellites
        self.properties = satellite_infos
        self.missions = daily_missions
        self.emergencies = emergencies
        self.tracks = {}   # position in this is The Satellite's under point information
        self.from_time = None
        self.to_time = None
        self.save_path = make_dir(save_root)

    def clear_tracks(self):
        self.tracks = {}

    def set_from_to(self, from_time, to_time):
        """
        :param from_time: in datetime format
        :param to_time: in datetime format
        :return:
        """
        self.from_time = from_time
        self.to_time = to_time

    def calc_tracks(self, satellite):
        """
        calculate satellite tracks in every minute from tle file
        :param satellite: dict of satellite tle
        :return: tracks in list format (position in every minute)
        """
        assert self.from_time is not None
        assert self.to_time is not None
        sat_name = satellite['satellite_name']
        line1 = satellite['tle_1']
        line2 = satellite['tle_2']
        tle_rec = ephem.readtle(sat_name, line1, line2)

        date_gap = self.to_time - self.from_time
        minutes_total = int(date_gap.total_seconds() / 60)  # get total minutes

        interval = dt.timedelta(minutes=1)  # use 1 minute as the interval

        time_list = []
        for i in range(minutes_total):
            time_list.append(self.from_time + i * interval)

        positions = []
        for t in time_list:
            tle_rec.compute(t)
            positions.append((tle_rec.sublong / ephem.degree,
                              tle_rec.sublat / ephem.degree,
                              tle_rec.elevation))
        self.tracks[sat_name] = positions
        return positions

    def get_tracks_all(self):
        self.clear_tracks()
        for satellite in self.satellites:
            self.calc_tracks(satellite)
        save_file = os.path.join(self.save_path, "all_tracks.json")
        with open(save_file, 'w') as f:
            json.dump(self.tracks, f, indent=3)
            print(f'[+] all tracks data in {save_file}')

    def get_tracks_by_resolution(self, res=10):
        self.clear_tracks()
        for satellite in self.satellites:
            if self.properties[satellite][0] > res:
                continue
            self.calc_tracks(satellite)
        save_file = os.path.join(self.save_path, f"resolution_over{res}_tracks.json")
        with open(save_file, 'w') as f:
            json.dump(self.tracks, f, indent=3)
            print(f"resolution over{res} tracks data in {save_file}")

    def get_tracks_by_type(self, typename="SAR"):
        self.clear_tracks()
        for satellite in self.satellites:
            if self.properties[satellite][2] != typename:
                continue
            self.calc_tracks(satellite)
        save_file = os.path.join(self.save_path, f"type_of_{typename}_tracks.json")
        with open(save_file, 'w') as f:
            json.dump(self.tracks, f, indent=3)
            print(f"type of {typename} tracks data in {save_file}")

    def get_tracks_week(self, from_time, res=None, typename=None):
        self.set_from_to(from_time, from_time+dt.timedelta(days=7))
        self.get_tracks_all()
        if res is not None:
            self.get_tracks_by_resolution(res)
        if typename is not None:
            self.get_tracks_by_type(typename)

    def get_tracks_day(self, from_time, res=None, typename=None):
        self.set_from_to(from_time, from_time+dt.timedelta(days=1))
        self.get_tracks_all()
        if res is not None:
            self.get_tracks_by_resolution(res)
        if typename is not None:
            self.get_tracks_by_type(typename)

    def get_track_single(self, satellite_name, from_time, to_time):
        self.clear_tracks()
        self.set_from_to(from_time, to_time)
        positions = self.calc_tracks(self.satellites[satellite_name])
        return positions


class SatellitePosition:
    """
    inputs human-style information of satellites, missions and emergencies.
    outputs the best observe plan in a week.
    """
    def __init__(self, satellite: dict = None):
        """
        :param satellites: a list of dict which includes satellite name and TLE
        """
        self.satellite = satellite
        self.tracks = []   # position in this is The Satellite's under point information
        self.from_time = None
        self.to_time = None

    def clear_tracks(self):
        self.tracks = []

    def set_from_to(self, from_time, to_time):
        """
        :param from_time: in datetime format
        :param to_time: in datetime format
        :return:
        """
        self.from_time = from_time
        self.to_time = to_time

    def calc_tracks(self, satellite, interval:int = 1):
        """
        calculate satellite tracks in every minute from tle file
        :param satellite: dict of satellite tle
        :return: tracks in list format (position in every minute)
        """
        assert self.from_time is not None
        assert self.to_time is not None
        sat_name = satellite['satellite_name']
        line1 = satellite['tle_1']
        line2 = satellite['tle_2']
        tle_rec = ephem.readtle(sat_name, line1, line2)

        date_gap = self.to_time - self.from_time
        minutes_total = int(date_gap.total_seconds() / (60*interval))  # get total minutes

        interval = dt.timedelta(minutes=interval)  # use 1 minute as the interval

        time_list = []
        for i in range(minutes_total):
            time_list.append(self.from_time + i * interval)

        positions = []
        for t in time_list:
            tle_rec.compute(t)
            positions.append((tle_rec.sublong / ephem.degree,
                              tle_rec.sublat / ephem.degree,
                              tle_rec.elevation))
        self.tracks = positions
        return positions

    def get_tracks(self, interval: int = 1):
        self.clear_tracks()
        self.calc_tracks(self.satellite, interval)
        return self.tracks

    def save_track(self, savepath):
        with open(savepath, 'w') as f:
            json.dump(self.tracks, f, indent=3)
            print(f'[+] tracks data saved in {savepath}')