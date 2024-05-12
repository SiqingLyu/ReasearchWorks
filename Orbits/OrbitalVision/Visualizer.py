import folium
from folium import plugins
import geopandas as gpd
from tools import *
from typing import List, Optional
from shapely.geometry import shape, GeometryCollection
from fiona.collection import Collection


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


def check_shp_file(shp_file_path):
    """检查shp文件是否包含元素。如果文件不存在或没有元素，则返回False。"""
    try:
        with Collection(shp_file_path, "r") as shp:
            # 尝试读取第一个要素
            first_feature = next(iter(shp))
            # 将第一个要素转换为shapely几何对象
            geom = shape(first_feature["geometry"])
            # 检查几何对象是否有效
            if not geom.is_valid:
                geom = GeometryCollection([geom.buffer(0)])
            return True
    except (StopIteration, ValueError, TypeError):
        # 如果无法从文件中读取要素，或要素的几何属性无法转换为shapely几何对象，则文件可能为空
        return False


if __name__ == '__main__':
    Fore_names = {
        'SENTINEL': 10,
        'LANDSAT': 30,
        'SPOT': 6,
        'IKONOS': 4,
        'WORLDVIEW': 1.8,
        'NOVASAR': 20,
        'RADARSAT': 25,
        'TERRASAR': 3,
        'TANDEM': 1,
        'ALOS': 10,
        'ARIRANG': 20,
        'COSMO': 15,
        }.keys()
    Title = "Landslide_optical"
    V = Visualizer(location=[35.43, 73.63], title=f'{Title}', zoom_start=7, crs='EPSG3857')
    V.load_esri()
    V.add_point(location=[35.404896, 72.60522], name='Landslide Spot', color="red")

    V.add_style(fill_color='white', boarder_color='black', weight=4, fill_transparency=0.0, style_sort='ROI')
    V.add_style(fill_color='black', boarder_color='grey', weight=3, fill_transparency=0.03, style_sort='Other')
    V.add_style(fill_color='red', boarder_color='grey', weight=2, fill_transparency=0.04, style_sort='China')

    V.add_shp(shp_path=r'G:\STKDATA\SHPs\Range\Landslide20240415.shp', name="Intrested Area", style_sort="ROI", if_show=True)
    from_date = 14
    for end_date in [15, 17, 19, 21]:
        file_root = rf'G:\STKDATA\{Title}\Buffer_minres10\{from_date}_{end_date}'
        filepaths, filenames = file_name_shp(file_root)
        for ii in range(len(filenames)):
            filepath = filepaths[ii]
            filename = filenames[ii]
            if not check_shp_file(filepath):
                continue
            satellite_name = filename.split('_')[0]
            if satellite_name in Fore_names:
                V.add_shp(shp_path=filepath,name='{}-{} Apr, {} Track'.format(from_date, end_date, filename),
                          style_sort="Other", if_show=True if end_date == 15 else False)
            else:
                V.add_shp(shp_path=filepath, name='{}-{} Apr, {} Track'.format(from_date, end_date, filename),
                          style_sort="China", if_show=True if end_date == 15 else False)
    V.save_map(f'{Title}.html')
