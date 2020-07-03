

import os
import sys
import arcpy
import random

arcpy.env.overwriteOutput = True

class LandslideSimulations():

    def __init__(self, in_landslides, out_landslides, mean, stdev, temp_location):
        self._in_landslides = in_landslides
        self._out_landslides = out_landslides
        self._mean = mean
        self._stdev = stdev
        self._temp_folder = temp_location


    # def simulate(self, landslides_feature, simulated_landslides, mean, stdev):
    def simulate(self):
        # print(os.path.dirname(self._out_landslides), os.path.basename(self._out_landslides))
        arcpy.CreateFeatureclass_management(out_path=os.path.dirname(self._out_landslides), out_name=os.path.basename(self._out_landslides), geometry_type="Polygon", template=self._in_landslides)
        arcpy.AddField_management(in_table=self._out_landslides, field_name="SIM", field_type="SHORT")
        mean = self._mean
        stdev = self._stdev
        searchLandslides = arcpy.SearchCursor(self._in_landslides)
        insertLandslide = arcpy.InsertCursor(self._out_landslides)
        pointArray = arcpy.Array()
        newVertex = arcpy.Point()

        geom = arcpy.Describe(self._in_landslides).ShapeFieldName
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
        return self._out_landslides


    def landslide2raster(self, in_landslides, out_landslide, reference_raster, mask):
        temp_landslides = os.path.join(self._temp_folder, "lsimr.tif")
        arcpy.env.snapRaster = reference_raster
        arcpy.env.extent = reference_raster.extent
        # arcpy.FeatureToRaster_conversion(landslides, "tobia", landslidesOUT, cell_size=referenceRaster.meanCellWidth)
        arcpy.PolygonToRaster_conversion(in_features=in_landslides, value_field="SIM", out_rasterdataset=temp_landslides, cellsize=reference_raster.meanCellWidth)
        arcpy.SetRasterProperties_management(temp_landslides, nodata=[[1, 0]])
        out_temp_landslies = arcpy.Raster(temp_landslides) * mask
        out_temp_landslies.save(out_landslide)
        # temp_landslides= None
        arcpy.Delete_management(temp_landslides)
        return out_landslide