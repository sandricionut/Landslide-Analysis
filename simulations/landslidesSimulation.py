

import os
import sys
import arcpy
import random

arcpy.env.overwriteOutput = True

class LandslideSimulations():

    def __init__(self):
        pass


    def SimulateLandslide(self, landslides_feature, simulated_landslides, mean, stdev):
        arcpy.CreateFeatureclass_management(os.path.dirname(simulated_landslides), os.path.basename(simulated_landslides), "Polygon", landslides_feature)
        arcpy.AddField_management(simulated_landslides, field_name="SIM", field_type="SHORT")
        mean = mean
        stdev = stdev
        searchLandslides = arcpy.SearchCursor(landslides_feature)
        insertLandslide = arcpy.InsertCursor(simulated_landslides)
        pointArray = arcpy.Array()
        newVertex = arcpy.Point()

        geom = arcpy.Describe(landslides_feature).ShapeFieldName
        try:
            for landslide in searchLandslides:
                landslideGeometry = landslide.getValue(geom)
                simulatedLandslide = insertLandslide.newRow()
                i = 0
                for part in landslideGeometry:
                    for vertex in landslideGeometry.getPart(i):
                        if part:
                            newVertex.X = random.normalvariate(mean, stdev) + float(vertex.X)
                            newVertex.Y = random.normalvariate(mean, stdev) + float(vertex.Y)
                            pointArray.add(newVertex)
                        else:
                            arcpy.AddMessage("Internal circle")
                    i = i+1
                    simulatedLandslide.shape = pointArray
                simulatedLandslide.SIM = 1
                insertLandslide.insertRow(simulatedLandslide)
                pointArray.removeAll()
        except:
            arcpy.AddMessage(arcpy.GetMessages(0) + " " + arcpy.GetMessages(1) + " " + arcpy.GetMessages(2))
            pointArray.removeAll()

        newVertex = None
        pointArray = None
        del searchLandslides
        del insertLandslide


    def Landslides2Raster(self, landslides_feature, reference_raster, mask):
        landslidesOUT = "in_memory\\lSimR"
        arcpy.env.snapRaster = reference_raster
        arcpy.env.extent = reference_raster.extent
        # arcpy.FeatureToRaster_conversion(landslides, "tobia", landslidesOUT, cell_size=referenceRaster.meanCellWidth)
        arcpy.PolygonToRaster_conversion(landslides_feature, "SIM", out_rasterdataset=landslidesOUT, cellsize=reference_raster.meanCellWidth)
        arcpy.SetRasterProperties_management(landslidesOUT, nodata=[[1, 0]])
        return arcpy.Raster(landslidesOUT) * mask