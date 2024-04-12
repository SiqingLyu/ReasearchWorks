import arcpy
from tools import *

out_coor_system = r'C:\Users\Dell\AppData\Roaming\ESRI\Desktop10.2\ArcMap\Coordinate Systems\WGS 1984 UTM Zone 34N.prj'


Listfile, allFilename = file_name_tif(r'D:\Homework\SecondTerm\farm\Ukrine\before_war')
# print (allFilename)
# in_raster = r'D:\Homework\SecondTerm\farm\Ukrine\before_war\\' + 'Ukrine_Beforewar-0000000000-0000000000' + '.tif'
# out_raster = r'D:\Homework\SecondTerm\farm\Ukrine\before_war_UTM\\' + 'Ukrine_Beforewar-0000000000-0000000000' + '.tif'
# arcpy.ProjectRaster_management (in_raster, out_raster, out_coor_system, cell_size=10)
'''
generalize projection
'''
for i in range(len(allFilename)):
    print ("processing " + allFilename[i])
    in_raster = r'D:\Homework\SecondTerm\farm\Ukrine\before_war\\' + allFilename[i] + '.tif'
    out_raster = r'D:\Homework\SecondTerm\farm\Ukrine\before_war_UTM\\' + allFilename[i] + '.tif'
    arcpy.ProjectRaster_management(in_raster, out_raster, out_coor_system, cell_size=10)

Listfile, allFilename = file_name_tif(r'D:\Homework\SecondTerm\farm\Ukrine\after_war')
for i in range(len(allFilename)):
    print ("processing " + allFilename[i])
    in_raster = r'D:\Homework\SecondTerm\farm\Ukrine\after_war\\' + allFilename[i] + '.tif'
    out_raster = r'D:\Homework\SecondTerm\farm\Ukrine\after_war_UTM\\' + allFilename[i] + '.tif'
    arcpy.ProjectRaster_management(in_raster, out_raster, out_coor_system, cell_size=10)

# '''
# Mosaic all files to one to get Vision
# '''
# Listfile, allFilename = file_name_tif(r'D:\Desktop\prediction_after_war\home\dell\lzp\ReWrite\UKR_LUUnetpp-ukr_1')
# output_raster = [r'D:\Desktop\prediction_after_war\home\dell\lzp\ReWrite', 'UKR_afterwar.tif']
# arcpy.MosaicToNewRaster_management(Listfile, output_location=output_raster[0], raster_dataset_name_with_extension=output_raster[1],
#                                    coordinate_system_for_the_raster=out_coor_system, cellsize=10, number_of_bands=1)
# Listfile, allFilename = file_name_tif(r'D:\Homework\SecondTerm\farm\Dataset256_v2\gt')
# output_raster = [r'D:\Desktop\prediction_after_war\home\dell\lzp\ReWrite', 'UKR_beforewar.tif']
# arcpy.MosaicToNewRaster_management(Listfile, output_location=output_raster[0], raster_dataset_name_with_extension=output_raster[1],
#                                    coordinate_system_for_the_raster=out_coor_system, cellsize=10, number_of_bands=1)
