
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

    def noise_factor_calculus(self, n, size):
        return int((n * 10) * size / 100)


    def noise_factor_dictionary(self, n):
        dictionary_nf = {0:None, 1:3, 2:5, 3:7, 4:9, 5:11, 6:14, 7:15, 8:17, 9:19, 10:21}
        return dictionary_nf[n]

    # def dem_noise(self, inDEM, outDEM, mean, stdev, self._mask, noise_order):
    def dem_noise(self, noise_factor=None):
        arcpy.env.overwriteOutput = True
        arcpy.env.extent = self._in_dem
        r_metadata = arcpy.Raster(self._in_dem)
        self._noise_order = self.noise_factor_calculus(noise_factor, r_metadata.width)
        sufix = str(noise_factor).replace(".","_")
        noise_raster = "noise{}.tif".format(sufix)
        noise_raster_path = os.path.join(self._temp_folder, noise_raster)
        n_width = self.noise_factor_calculus(noise_factor, r_metadata.width)
        neighborhood_smooth = arcpy.sa.NbrRectangle(width=n_width, height=n_width, units="CELL")
        # neighborhood_smooth = arcpy.sa.NbrCircle(radius=n_width, units="CELL")

        arcpy.CreateRandomRaster_management(self._temp_folder, noise_raster, "NORMAL {} {}".format(self._mean, self._stdev), self._in_dem, r_metadata.meanCellHeight)
        noise_smooth = arcpy.sa.FocalStatistics(in_raster=noise_raster_path, neighborhood=neighborhood_smooth, statistics_type="MEAN", ignore_nodata="DATA")
        noise_smooth.save(self._temp_folder + "\\noise_smooth{}.tif".format(sufix))
        outRaster = (noise_smooth + arcpy.sa.Raster(self._in_dem)) * arcpy.Raster(self._mask)
        outRaster.save(self._out_dem)
        # arcpy.Delete_management(points_interpolation)
        # arcpy.Delete_management(os.path.join(self._temp_folder, random_points))
        # arcpy.Delete_management(noise)
        # del noise
        return self._out_dem


    # def dem_noise(self, inDEM, outDEM, mean, stdev, self._mask, noise_order):
    def dem_noise2(self, noise_factor=None):
        arcpy.env.overwriteOutput = True
        arcpy.env.extent = self._in_dem
        r_metadata = arcpy.Raster(self._in_dem)
        self._noise_order = self.noise_factor_dictionary(noise_factor)
        sufix = str(noise_factor)
        noise_raster = "noise{}.tif".format(sufix)
        noise_raster_path = os.path.join(self._temp_folder, noise_raster)
        neighborhood_smooth = arcpy.sa.NbrRectangle(width=self._noise_order, height=self._noise_order, units="CELL")

        arcpy.CreateRandomRaster_management(self._temp_folder, noise_raster, "NORMAL {} {}".format(self._mean, self._stdev), self._in_dem, r_metadata.meanCellHeight)
        noise_smooth = arcpy.sa.FocalStatistics(in_raster=noise_raster_path, neighborhood=neighborhood_smooth, statistics_type="MEAN", ignore_nodata="DATA")
        noise_smooth.save(self._temp_folder + "\\noise_smooth{}.tif".format(sufix))
        outRaster = (noise_smooth + arcpy.sa.Raster(self._in_dem)) * arcpy.Raster(self._mask)
        outRaster.save(self._out_dem)
        # arcpy.Delete_management(points_interpolation)
        # arcpy.Delete_management(os.path.join(self._temp_folder, random_points))
        # arcpy.Delete_management(noise)
        # del noise
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