import os
import sys
import arcpy
import numpy
import math
import shutil
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")


class Tobia():

    def __init__(self):
        self._dem = None
        # self._points = None
        # self._dip_angle_field = None
        # self._dip_direction_field = None
        self._out_dip_angle = None

    def rad2deg(self, in_rad):
        return math.pi / 180

    def deg2rad(self):
        return math.pi / 180.0

    def interpolate_dip(self, in_points, in_dip_field, out_raster):
        img_template = arcpy.Raster(self._dem)
        arcpy.env.extent = img_template.extent
        arcpy.env.snapRaster = img_template
        Idw(in_points, in_dip_field, img_template.meanCellWidth, 1.5, RadiusVariable(12, 150000)).save(out_raster)
        # return self._out_dip_angle

    def calculate_chord_length(self):
        pass

    def calculate_tobia(self, in_dem, in_dip_angle, in_dip_direction, out_raster):
        #Calculate Tobia index
        slope = arcpy.sa.Slope(in_raster=self._dem, output_measurement="DEGREE", method="PLANAR") * self.deg2rad()
        slope_rad = slope * self.deg2rad()
        aspect = arcpy.sa.Aspect(in_raster=self._dem, method="PLANAR") * self.deg2rad()
        dip_angle_rad = in_dip_angle * self.deg2rad()
        dip_direction_rad = in_dip_direction * self.deg2rad()
        dip_direction_aspect_rad = (in_dip_direction - aspect) * self.deg2rad()
        tobia = (Cos(dip_angle_rad)) * (Cos(slope_rad) + (Sin(dip_direction_rad))) * Sin(slope_rad) * (Cos(dip_direction_aspect_rad))
        tobia.save(out_raster)

    def classify_tobia(self, in_raster, out_raster, no_classes=3):
        chord_length = arcpy.RasterToNumPyArray(self.calculate_chord_length()).flatten()
        slope_class = numpy.zeros_like(chord_length, dtype=numpy.int8).flatten()
        #Classification with 8 classes
        for i in range(0, len(chord_length)):
            if(chord_length[i] < 0.7654):
                if(npDipAngleRad[i] - npSlopeRad[i]) < -5:
                    npSlopesClassificationCL8[i] = 4
                elif(npDipAngleRad[i] - npSlopeRad[i]) > 5:
                    npSlopesClassificationCL8[i] = 3
                elif(((npDipAngleRad[i] - npSlopeRad[i]) <= 5) and ((npDipAngleRad[i] - npSlopeRad[i]) >= -5)):
                    npSlopesClassificationCL8[i] = 2

            elif (npChordLength[i] >= 0.7654 and npChordLength[i] < 1.8478):
                    npSlopesClassificationCL8[i] = 8
            elif (npChordLength[i] >= 1.8478):
                if(npDipAngleRad[i] - npSlopeRad[i]) < -5:
                    npSlopesClassificationCL8[i] = 5
                elif(npDipAngleRad[i] - npSlopeRad[i]) > 5:
                    npSlopesClassificationCL8[i] = 6
                elif(((npDipAngleRad[i] - npSlopeRad[i]) <= 5) and ((npDipAngleRad[i] - npSlopeRad[i]) >= -5)):
                    npSlopesClassificationCL8[i] = 7
            else:
                npSlopesClassificationCL8[i] = 1

#
# # Chord length
# a = (Cos(dipDirectionRad) - Cos(aspectRad))**2
# b = (Sin(dipDirectionRad) - Sin(aspectRad))**2
# chordLength = SquareRoot(a + b)
# chordLength.save(arcpy.GetParameterAsText(6))
#
# #Conversion to numpy array
# npChordLength = arcpy.RasterToNumPyArray(chordLength).flatten()
# # npDipDirectionRad = arcpy.RasterToNumPyArray(dipDirectionRad)
# # npDipDirectionRad = arcpy.RasterToNumPyArray(dipDirectionRad)
# npSlopeRad = arcpy.RasterToNumPyArray(slopeRad).flatten()
# npDipAngleRad = arcpy.RasterToNumPyArray(dipAngleRad).flatten()
# npSlopesClassificationCL4 = numpy.zeros_like(npChordLength, dtype=numpy.int8).flatten()
# npSlopesClassificationCL8 = numpy.zeros_like(npChordLength, dtype=numpy.int8).flatten()
#
# # Classification with 4 classes
# for i in range(0, len(npChordLength)):
#     if(npChordLength[i] < 0.7654):
#         npSlopesClassificationCL4[i] = 1
#     elif (npChordLength[i] >= 0.7654 and npChordLength[i] < 1.8478):
#         npSlopesClassificationCL4[i] = 2
#     elif (npChordLength[i] >= 1.8478):
#         npSlopesClassificationCL4[i] = 3
# slopesClassificationCL4 = arcpy.NumPyArrayToRaster(npSlopesClassificationCL4.reshape(imgCopy.height, imgCopy.width), arcpy.Point(imgCopy.extent.XMin, imgCopy.extent.YMin), imgCopy.meanCellWidth, imgCopy.meanCellHeight)
# arcpy.AddField_management(in_table=slopesClassificationCL4, field_name="Classes", field_type="TEXT", field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
#
# updateClassification = arcpy.UpdateCursor(slopesClassificationCL4)
# for row in updateClassification:
#     if(row.getValue('VALUE') == 1):
#         row.setValue("Classes", "Cataclinal")
#         updateClassification.updateRow(row)
#     elif(row.getValue('VALUE') == 2):
#         row.setValue("Classes", "Orthoclinal")
#         updateClassification.updateRow(row)
#     elif(row.getValue('VALUE') == 3):
#         row.setValue("Classes", "Anaclinal")
#         updateClassification.updateRow(row)
#     else:
#         row.setValue("Classes", "Unclasified")
#         updateClassification.updateRow(row)
# del updateClassification
# slopesClassificationCL4.save(arcpy.GetParameterAsText(7))
#
#
# slopesClassificationCL8 = arcpy.NumPyArrayToRaster(npSlopesClassificationCL8.reshape(imgCopy.height, imgCopy.width), arcpy.Point(imgCopy.extent.XMin, imgCopy.extent.YMin), imgCopy.meanCellWidth, imgCopy.meanCellHeight)
# arcpy.AddField_management(in_table=slopesClassificationCL8 , field_name="Classes", field_type="TEXT", field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
#
# updateClassification = arcpy.UpdateCursor(slopesClassificationCL8)
# for row in updateClassification:
#     if(row.getValue('VALUE') == 1):
#         row.setValue("Classes", "Unclassified")
#         updateClassification.updateRow(row)
#     elif(row.getValue('VALUE') == 2):
#         row.setValue("Classes", "Cataclinal dip slope")
#         updateClassification.updateRow(row)
#     elif(row.getValue('VALUE') == 3):
#         row.setValue("Classes", "Cataclinal underdip slope")
#         updateClassification.updateRow(row)
#     elif(row.getValue('VALUE') == 4):
#         row.setValue("Classes", "Cataclinal overdip slope")
#         updateClassification.updateRow(row)
#     elif(row.getValue('VALUE') == 5):
#         row.setValue("Classes", "Anaclinal steepened escarpment")
#         updateClassification.updateRow(row)
#     elif(row.getValue('VALUE') == 6):
#         row.setValue("Classes", "Anaclinal subdued escarpment")
#         updateClassification.updateRow(row)
#     elif(row.getValue('VALUE') == 7):
#         row.setValue("Classes", "Anaclinal normal escarpment")
#         updateClassification.updateRow(row)
#     elif(row.getValue('VALUE') == 8):
#         row.setValue("Classes", "Orthoclinal")
#         updateClassification.updateRow(row)
#     else:
#         row.setValue("Classes", "Unclasified")
#         updateClassification.updateRow(row)
# del updateClassification
#
# slopesClassificationCL8.save(arcpy.GetParameterAsText(8))
#
# arcpy.CheckInExtension("Spatial")