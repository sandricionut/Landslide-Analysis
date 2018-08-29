
import os
import arcpy
import datetime
import numpy

# Custom libraries
from analysis import wofe, tacuda, randomSelection
from simulations import landslidesSimulation, demSimulation, woefSimulation

if __name__ == "__main__":

    # Start
    start = datetime.datetime.now()

    arcpy.CheckOutExtension("Spatial")

    # Setup
    weightEvidence = wofe.WofE()

    # Input parameters
    indem = r"D:\Personal\Temp\DateInitiale\dem.tif"
    inlulc = r"D:\Personal\Temp\DateInitiale\landUse.tif"
    inlithology = r"D:\Personal\Temp\DateInitiale\lithology.tif"
    initial_landslides = r"D:\Personal\Temp\DateInitiale\WOEDB.gdb\DeplasariTerenBayes"
    # mask_vector = r"d:\Personal\Temp\DateInitiale\Masca.shp"
    mask_raster = r"D:\Personal\Temp\DateInitiale\Masca_PolygonToRaster.tif"
    out_path_temp = r"d:\Personal\Temp\Temporar"
    out_path_stats= r"d:\Personal\Temp\Stats"
    out_path_woe = r"d:\Personal\Temp\Simulari"
    arcpy.env.extent = indem

    dem_error_mean = 15
    dem_error_stdev = 9
    landslides_mapping_error_mean = 50
    landslides_mapping_error_stdev = 20
    # noise_order_value=3
    out_stats_file = os.path.join(out_path_stats, "prodCondI2018.txt")
    noise_values = numpy.arange(0.5,5.5,0.5)
    for noise_value in noise_values:
        # mask_raster = dem_simulate.CreateMask(mask_vector, "ID", cell_size=arcpy.Raster(in_dem).meanCellHeight)
        dem_simulate = demSimulation.DemSimulations(in_dem=indem, out_dem=r"d:\Personal\Temp\Temporar\demsim.tif", mean=landslides_mapping_error_mean, stdev=landslides_mapping_error_stdev, noise_order=noise_value, temp_location=out_path_temp, mask=mask_raster)
        # dem_simulate.run()
        landslide_simulate = landslidesSimulation.LandslideSimulations(in_landslides=initial_landslides, out_landslides=r"d:\Personal\Temp\Temporar\ls.shp", mean=landslides_mapping_error_mean, stdev=landslides_mapping_error_stdev, temp_location=out_path_temp)

        wofe_m = woefSimulation.WofESimulations(out_woe_map=out_path_woe, out_name_prefix="wf_{}".format(str(noise_value)))
        wofe_m.simulate(2, in_dem_sim=dem_simulate, landslide_sim=landslide_simulate, stats_file=out_stats_file, nominal_data=[inlulc, inlithology], mask=mask_raster)


    # for file in os.listdir(out_path_temp):
    #     os.remove(os.path.join(out_path_temp, file))

    # Stop
    stop = datetime.datetime.now()

    arcpy.CheckInExtension("Spatial")