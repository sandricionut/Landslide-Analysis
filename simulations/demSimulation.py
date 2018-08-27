
import os
import arcpy
import tempfile

class DemSimulations():

    def __init__(self, in_dem, out_dem, mean, stdev, noise_order, temp_location, mask=None):
        self._in_dem = in_dem
        self._out_dem = out_dem
        self._mean = mean
        self._stdev = stdev
        self._mask = mask
        self._noise_order = noise_order
        self._temp_folder = temp_location

    # def dem_noise(self, inDEM, outDEM, mean, stdev, self._mask, noise_order):
    def dem_noise(self):
        arcpy.env.overwriteOutput = True
        arcpy.env.extent = self._in_dem
        r_metadata = arcpy.Raster(self._in_dem)
        # Process: Create Random Points
        arcpy.CreateRandomPoints_management(self._temp_folder, "randomPoints.shp", None, self._mask, "1000", "10 Meters", "POINT", "0")
        arcpy.CreateRandomRaster_management(self._temp_folder, "noise.tif", "NORMAL {} {}".format(self._mean, self._stdev), self._in_dem, r_metadata.meanCellHeight)
        # Process: Extract Values to Points
        arcpy.sa.ExtractValuesToPoints(os.path.join(self._temp_folder, "randomPoints.shp"), os.path.join(self._temp_folder, "noise.tif"), os.path.join(self._temp_folder, "PointsInterpolation.shp"), "INTERPOLATE", "VALUE_ONLY")

        # Process: Trend
        noise = arcpy.sa.Trend(in_point_features=os.path.join(self._temp_folder, "PointsInterpolation.shp"), z_field="RASTERVALU", cell_size=r_metadata.meanCellWidth, order=self._noise_order, regression_type="LINEAR", out_rms_file=None)
        # Process: Raster Calculator
        outRaster = (noise + arcpy.sa.Raster(self._in_dem)) * arcpy.Raster(self._mask)

        # arcpy.Clip_management(outRaster, in_template_dataset=self._mask, out_raster=outDEM, clipping_geometry="ClippingGeometry", maintain_clipping_extent="MAINTAIN_EXTENT")
        outRaster.save(self._out_dem)
        arcpy.Delete_management(os.path.join(self._temp_folder, "PointsInterpolation.shp"))
        arcpy.Delete_management(os.path.join(self._temp_folder, "randomPoints.shp"))
        # arcpy.Delete_management(noise)
        del noise
        return self._out_dem

    def create_mask(self, mask_vector, field, cell_size):
        mask_raster = os.path.join(tempfile.gettempdir(), "mask_dem.tif")
        arcpy.PolygonToRaster_conversion(in_features=mask_vector, value_field=field, out_rasterdataset=mask_raster, cellsize=cell_size)
        return mask_raster

    def run(self):
        self.dem_noise()

    def clear(self):
        pass

    def get_temp_location(self):
        return self._temp_folder