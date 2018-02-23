
import os
import arcpy
import numpy
import tempfile


class DemSimulations():

    def __init__(self):
        pass

    def DemNoise(self, inDEM, outDEM, mean, stdev, mask, noise_order):
        arcpy.env.overwriteOutput = True
        arcpy.env.extent = inDEM
        # Process: Create Random Raster
        tempPath = tempfile.gettempdir()
        print(tempPath)
        rMetadata = arcpy.Raster(inDEM)
        # Process: Create Random Points
        arcpy.CreateRandomPoints_management(tempPath, "randomPoints.shp", None, mask, "1000", "10 Meters", "POINT", "0")
        arcpy.CreateRandomRaster_management(tempPath, "noise.tif", "NORMAL {} {}".format(mean, stdev), inDEM, rMetadata.meanCellHeight)
        # Process: Extract Values to Points
        arcpy.sa.ExtractValuesToPoints(os.path.join(tempPath, "randomPoints.shp"), os.path.join(tempPath, "noise.tif"), os.path.join(tempPath, "PointsInterpolation.shp"), "INTERPOLATE", "VALUE_ONLY")
        # Process: Trend
        noise = arcpy.sa.Trend(in_point_features=os.path.join(tempPath, "PointsInterpolation.shp"), z_field="RASTERVALU", cell_size=rMetadata.meanCellWidth, order=noise_order, regression_type="LINEAR", out_rms_file=None)
        # Process: Raster Calculator
        outRaster = (noise + arcpy.sa.Raster(inDEM)) * arcpy.Raster(mask)

        # arcpy.Clip_management(outRaster, in_template_dataset=mask, out_raster=outDEM, clipping_geometry="ClippingGeometry", maintain_clipping_extent="MAINTAIN_EXTENT")
        outRaster.save(outDEM)
        arcpy.Delete_management(os.path.join(tempPath, "PointsInterpolation.shp"))
        arcpy.Delete_management(os.path.join(tempPath, "randomPoints.shp"))
        # arcpy.Delete_management(noise)
        del noise
        return outDEM

    def CreateMask(self, mask_vector, field, cell_size):
        mask_raster = os.path.join(tempfile.gettempdir(), "mask_dem.tif")
        arcpy.PolygonToRaster_conversion(in_features=mask_vector, value_field=field, out_rasterdataset=mask_raster, cellsize=cell_size)
        return mask_raster