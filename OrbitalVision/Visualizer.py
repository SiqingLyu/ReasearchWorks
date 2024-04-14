import folium
from folium import plugins
import geopandas as gpd
from tools import *
from typing import List, Optional


class Visualizer:
    def __init__(self, location: List[float] = None, title: str = '', zoom_start: int = 7, crs: str = 'EPSG3857'):
        """
        This Visualizer is to visualize the satellite orbits for emergency disaster
        :param location: the position that user want the center of the map to be
        :param title: the title of the map
        :param zoom_start: the zoom level when the html firstly shows up
        :param crs: the coordinate system of the map
        """
        if location is None:
            location = [41, 118] # set a default position
        self.map = folium.Map(
            location=location,
            attr=title,
            zoom_start=zoom_start, crs=crs)
        self.default_style = lambda x: {
            'fillColor': 'red',
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.2
        }
        self.style_dicts = {}

    def load_esri(self):
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Esri Satellite',
            overlay=True,
            control=True,
            # show=True,
        ).add_to(self.map)

    def add_point(self, location: List = None, name: str = '', color: str = '', **kwargs):
        folium.Marker(
            location=location,
            popup=name,
            icon=folium.Icon(color=color, icon='info-sign'),
            **kwargs
        ).add_to(self.map)

    def add_shp(self, shp_path: str = '', name: str = '', style_sort: str = '', if_show: bool = False):
        assert style_sort in self.style_dicts.keys(), f"{style_sort} has no style format"
        assert self.style_dicts[style_sort] is not None, f"{style_sort} has no style format"
        shp_data = gpd.read_file(shp_path)
        self.map.add_child(folium.GeoJson(data=shp_data,
                                          style_function=self.style_dicts[style_sort],
                                          show=if_show,
                                          name=name))

    def add_style(self, fill_color: str = '', boarder_color: str = '', weight: int = 2, fill_transparency: float = 1.0,
                  style_sort: str = ''):
        self.style_dicts[style_sort] = lambda x: {
            'fillColor': fill_color,
            'color': boarder_color,
            'weight': weight,
            'fillOpacity': fill_transparency
        }

    def save_map(self, save_path: str = '', if_controller: bool = True):
        if if_controller:
            folium.LayerControl().add_to(self.map)
        self.map.save(save_path)


if __name__ == '__main__':
    V = Visualizer(location=[34.9042, 73.6418], title='Test', zoom_start=7, crs='EPSG3857')
    V.load_esri()
    V.save_map('Test.html')
