

import os
import sys
import arcpy
import arcpy.sa

arcpy.CheckOutExtension('Spatial')

lstRasters = arcpy.GetParameterAsText(0)

landslides = arcpy.GetParameterAsText(1)
landslidesInfo = arcpy.Describe(landslides)
# arcpy.AddMessage(landslidesInfo)

lstRastersEVP = []

for raster in lstRasters.split(";"):
    arcpy.AddMessage(raster)
    name, ext = os.path.splitext(os.path.basename(os.path.normpath(raster)))
    lRaster = ["{}".format(raster), "{}".format(name)]
    lstRastersEVP.append(lRaster)
    
arcpy.AddMessage(lstRastersEVP)

if(landslidesInfo.shapeType == "Point"):
    arcpy.AddMessage("Punct")
    arcpy.sa.ExtractMultiValuesToPoints(landslides, lstRastersEVP)
elif(landslidesInfo.shapeType == "Polygon"):
    arcpy.AddMessage("Poligon")
    arcpy.AddError("Geometry type not supported. Must be Point")
else:
    arcpy.AddError("Geometry type not supported. Must be Point")

arcpy.CheckInExtension('Spatial')