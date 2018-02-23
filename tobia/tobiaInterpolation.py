
import os
import sys
import arcpy
import numpy
import math
import shutil
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

d2r = 180 / math.pi
r2d = math.pi / 180

dem = arcpy.GetParameterAsText(0)
ws = r'{}'.format(arcpy.GetParameterAsText(1))
points = arcpy.GetParameterAsText(2)
dipangle = arcpy.GetParameterAsText(3)
dipdirection = arcpy.GetParameterAsText(4)

arcpy.env.workspace = ws
imgCopy = arcpy.Raster(dem)

arcpy.env.cellSize = dem
#Slope
slope = Slope(dem, "DEGREE", 1)
#Aspect
aspect = Aspect(dem)

# Dip Angle
dipAngle = Idw(points, dipangle, imgCopy.meanCellWidth, 1.5, RadiusVariable(12, 150000))
dipAngle.save(os.path.join(ws, "dipAngleTemp"))
arcpy.Clip_management(in_raster=os.path.join(ws, "dipAngleTemp"), rectangle='{} {} {} {}'.format(imgCopy.extent.XMin, imgCopy.extent.YMin, imgCopy.extent.XMax, imgCopy.extent.YMax), 
                      out_raster=os.path.join(ws, "dipangle"), in_template_dataset=dem, nodata_value="-3.402823e+038", clipping_geometry="NONE", maintain_clipping_extent="MAINTAIN_EXTENT")
dipAngle = arcpy.Raster(os.path.join(ws, "dipangle"))

# Dip Direction
dipDirection = Idw(points, dipdirection, imgCopy.meanCellWidth, 1.5, RadiusVariable(12, 150000))
dipDirection.save(r"{}".format(ws) + "\\dipDirTemp")
arcpy.Clip_management(in_raster=os.path.join(ws, "dipDirTemp"), rectangle='{} {} {} {}'.format(imgCopy.extent.XMin, imgCopy.extent.YMin, imgCopy.extent.XMax, imgCopy.extent.YMax), 
                      out_raster=os.path.join(ws, "dipdir"), in_template_dataset=dem, nodata_value="-3.402823e+038", clipping_geometry="NONE", maintain_clipping_extent="MAINTAIN_EXTENT")
dipDirection = arcpy.Raster(os.path.join(ws, "dipdir"))

#Calculate Tobia index
slopeRad = slope / d2r
aspectRad = aspect / d2r
dipAngleRad = dipAngle / d2r
dipDirectionRad = dipDirection / d2r
slopeRad = slope / d2r
dipAngleRad = dipAngle / d2r
tobia = (Cos(dipAngleRad)) * (Cos(slopeRad) + (Sin(dipDirectionRad))) * Sin(slopeRad) * (Cos((dipDirection - aspect) / d2r))
tobia.save(arcpy.GetParameterAsText(5))

# Chord length
a = (Cos(dipDirectionRad) - Cos(aspectRad))**2
b = (Sin(dipDirectionRad) - Sin(aspectRad))**2
chordLength = SquareRoot(a + b)
chordLength.save(arcpy.GetParameterAsText(6))

#Conversion to numpy array
npChordLength = arcpy.RasterToNumPyArray(chordLength).flatten()
# npDipDirectionRad = arcpy.RasterToNumPyArray(dipDirectionRad)
# npDipDirectionRad = arcpy.RasterToNumPyArray(dipDirectionRad)
npSlopeRad = arcpy.RasterToNumPyArray(slopeRad).flatten()
npDipAngleRad = arcpy.RasterToNumPyArray(dipAngleRad).flatten()
npSlopesClassificationCL4 = numpy.zeros_like(npChordLength, dtype=numpy.int8).flatten()
npSlopesClassificationCL8 = numpy.zeros_like(npChordLength, dtype=numpy.int8).flatten()

# Classification with 4 classes
for i in range(0, len(npChordLength)):
    if(npChordLength[i] < 0.7654):
        npSlopesClassificationCL4[i] = 1
    elif (npChordLength[i] >= 0.7654 and npChordLength[i] < 1.8478):
        npSlopesClassificationCL4[i] = 2
    elif (npChordLength[i] >= 1.8478):
        npSlopesClassificationCL4[i] = 3    
slopesClassificationCL4 = arcpy.NumPyArrayToRaster(npSlopesClassificationCL4.reshape(imgCopy.height, imgCopy.width), arcpy.Point(imgCopy.extent.XMin, imgCopy.extent.YMin), imgCopy.meanCellWidth, imgCopy.meanCellHeight)
arcpy.AddField_management(in_table=slopesClassificationCL4, field_name="Classes", field_type="TEXT", field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

updateClassification = arcpy.UpdateCursor(slopesClassificationCL4)
for row in updateClassification:
    if(row.getValue('VALUE') == 1):
        row.setValue("Classes", "Cataclinal")
        updateClassification.updateRow(row)
    elif(row.getValue('VALUE') == 2):
        row.setValue("Classes", "Orthoclinal")
        updateClassification.updateRow(row)
    elif(row.getValue('VALUE') == 3):
        row.setValue("Classes", "Anaclinal")
        updateClassification.updateRow(row)
    else:
        row.setValue("Classes", "Unclasified")
        updateClassification.updateRow(row)
del updateClassification
slopesClassificationCL4.save(arcpy.GetParameterAsText(7))

#Classification with 8 classes
for i in range(0, len(npChordLength)):
    if(npChordLength[i] < 0.7654):
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
        
slopesClassificationCL8 = arcpy.NumPyArrayToRaster(npSlopesClassificationCL8.reshape(imgCopy.height, imgCopy.width), arcpy.Point(imgCopy.extent.XMin, imgCopy.extent.YMin), imgCopy.meanCellWidth, imgCopy.meanCellHeight)
arcpy.AddField_management(in_table=slopesClassificationCL8 , field_name="Classes", field_type="TEXT", field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

updateClassification = arcpy.UpdateCursor(slopesClassificationCL8)
for row in updateClassification:
    if(row.getValue('VALUE') == 1):
        row.setValue("Classes", "Unclassified")
        updateClassification.updateRow(row)
    elif(row.getValue('VALUE') == 2):
        row.setValue("Classes", "Cataclinal dip slope")
        updateClassification.updateRow(row)
    elif(row.getValue('VALUE') == 3):
        row.setValue("Classes", "Cataclinal underdip slope")
        updateClassification.updateRow(row)
    elif(row.getValue('VALUE') == 4):
        row.setValue("Classes", "Cataclinal overdip slope")
        updateClassification.updateRow(row)
    elif(row.getValue('VALUE') == 5):
        row.setValue("Classes", "Anaclinal steepened escarpment")
        updateClassification.updateRow(row)
    elif(row.getValue('VALUE') == 6):
        row.setValue("Classes", "Anaclinal subdued escarpment")
        updateClassification.updateRow(row)
    elif(row.getValue('VALUE') == 7):
        row.setValue("Classes", "Anaclinal normal escarpment")
        updateClassification.updateRow(row)
    elif(row.getValue('VALUE') == 8):
        row.setValue("Classes", "Orthoclinal")
        updateClassification.updateRow(row)
    else:
        row.setValue("Classes", "Unclasified")
        updateClassification.updateRow(row)
del updateClassification        

slopesClassificationCL8.save(arcpy.GetParameterAsText(8))

arcpy.CheckInExtension("Spatial")
