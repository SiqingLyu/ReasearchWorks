import folium
from folium import plugins
import geopandas as gpd
# define the national map
from tools import *

Fore_names = [
    'SENTINEL',
    'LANDSAT',
    'SPOT',
    'IKONOS',
]

style_function_dome = lambda x: {
        'fillColor': 'red',
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.2
    }

style_function_fore = lambda x: {
        'fillColor': 'black',
        'color': 'grey',
        'weight': 2,
        'fillOpacity': 0.4
    }

m = folium.Map(
    location=[34.9042, 73.6418],
    attr='HR Satellite Tracks around Glacier collapse',
    zoom_start=7, crs='EPSG3857')


tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = True,
        control = True,
        # show=True,
       ).add_to(m)

folium.Marker(
    location=[34.9042, 73.6418],
    popup='Glacier collapse',
    icon=folium.Icon(color='red', icon='info-sign')
).add_to(m)

for end_date in [24, 26, 28, 30]:
    file_root = r'F:\STKDATA\Buffer_minres10\23_{}'.format(end_date)
    filepaths, filenames = file_name_shp(file_root)
    for ii in range(len(filenames)):
        filepath = filepaths[ii]
        filename = filenames[ii]
        satellite = gpd.read_file(filepath)
        satellite_name = filename.split('_')[0]
        if satellite_name in Fore_names:
            m.add_child(folium.GeoJson(data=satellite, style_function=style_function_fore,
                                       show=True if end_date == 24 else False,
                                       name='23-{} Mar, {} Track'.format(end_date, filename)))
        else:
            m.add_child(folium.GeoJson(data=satellite, style_function = style_function_dome,
                                       show=True if end_date == 24 else False,
                                       name='23-{} Mar,  {} Track'.format(end_date, filename)))

# folium.raster_layers.ImageOverlay(
#     image="https://upload.wikimedia.org/wikipedia/commons/f/f4/Mercator_projection_SW.jpg",
#     name="I am a jpeg",
#     bounds=[[-82, -180], [82, 180]],
#     opacity=1,
#     interactive=False,
#     cross_origin=False,
#     zindex=1,
#     alt="Wikipedia File:Mercator projection SW.jpg",
# ).add_to(m)

folium.LayerControl().add_to(m)
# save national map
m.save('Glacier_collapse_all_satellites.html')