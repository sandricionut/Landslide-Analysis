
import os
import arcpy
import datetime
import numpy
import shutil

# Custom libraries
from analysis import wofe, tacuda
from simulations import landslidesSimulation, demSimulation
import simulations
from future import *

if __name__ == "__main__":

    # Start
    start = datetime.datetime.now()

    weightEvidence = wofe.WofE()
    landslidesSimulate = landslidesSimulation.LandslideSimulations()
    dem_simulate = demSimulation.DemSimulations()
    terrain_analysis = tacuda.taCUDA()

    in_dem = r""
    inLULC = r""
    inLithology = r""
    initial_landslides = r""
    mask_vector = r''
    out_path = r""
    out_path_woe = r""
    arcpy.env.extent = in_dem
    mask_raster = dem_simulate.CreateMask(mask_vector, "ID", cell_size=arcpy.Raster(in_dem).meanCellHeight)

    dem_error_mean = 15
    dem_error_stdev = 9
    landslides_mapping_error_mean = 50
    landslides_mapping_error_stdev = 20
    noise_order_value=3
    out_stats_file = os.path.join(r'c:\WOE\Stats', 'prodCondI2018.txt')
    outFileResults = open(out_stats_file, "w")
    outFileResults.write("rasterName\tclass\tweightPositive\tweightNegative\tcontrast\tsumWnt\tareaClassPresence\tareaTotalPresenceMinusClass\tareaClassAbsence\tareaTotalAbsence\ts2Wp\ts2wN\tstudentized\titeration\n")
    outFileResults.flush()
    outFileResults.close()

    # Generate noise for DEM
    for i in range(0, 1000, 1):
        dem_noise = os.path.join(out_path, "demNoise{}.tif".format(str(i)))
        dem_simulate.DemNoise(inDEM=in_dem, outDEM=dem_noise, mean=dem_error_mean, stdev=dem_error_stdev, mask=mask_raster, noise_order=noise_order_value)

        # Terrain analyses
        outSlope = os.path.join(out_path, "slope{}.tif".format(str(i)))
        # outTPI = os.path.join(out_path, "twi{}.tif".format(str(i)))
        outProfileCurvature = os.path.join(out_path, "profc{}.tif".format(str(i)))
        out_plan_curvature = os.path.join(out_path, "planc{}.tif".format(str(i)))

        outSlopeR = os.path.join(out_path, "slopeR_{}.tif".format(str(i)))
        # outTPIR = os.path.join(out_path, "twiR_{}.tif".format(str(i)))
        out_profile_curvatureR = os.path.join(out_path, "profcR_{}.tif".format(str(i)))
        out_plan_curvatureR = os.path.join(out_path, "plancR_{}.tif".format(str(i)))

        # Call georsgpu for terrain analyses
        terrain_analysis.calculate(dem_noise, outSlope, command='slope')
        terrain_analysis.calculate(dem_noise, outProfileCurvature, command='profileCurvature')
        terrain_analysis.calculate(dem_noise, out_plan_curvature, command='planCurvature')
        # terrain_analysis.calculate(dem_noise, outTPI, command='tpi')

        # Evidence classification
        classesCurvature = numpy.arange(-3.0, 3.5, 0.5)
        classesSlope = numpy.arange(0, 90, 3)
        reclassCurvature = []
        reclassSlope = []
        # Add minimum curvature value - estimated
        reclassCurvature.append([-100, -3.0, 1])

        for clasa in range(1, len(classesCurvature)):
            reclassCurvature.append([round(classesCurvature[clasa - 1], 4), round(classesCurvature[clasa], 4), clasa + 1])

        for clasa in range(1, len(classesSlope)):
            reclassSlope.append([round(classesSlope[clasa - 1], 4), round(classesSlope[clasa], 4), clasa])

        # Add maximum curvature value - estimated
        reclassCurvature.append([3.0, 100, len(classesCurvature) + 1])

        outSlopeReclass = arcpy.sa.Reclassify(outSlope, 'Value',
                                              arcpy.sa.RemapRange(reclassSlope), missing_values="NODATA") * mask_raster
        outSlopeReclass.save(outSlopeR)

        outProfCurvatureReclass = arcpy.sa.Reclassify(outProfileCurvature, 'Value',
                                                      arcpy.sa.RemapRange(reclassCurvature), missing_values="NODATA") * mask_raster
        outProfCurvatureReclass.save(out_plan_curvatureR)

        out_plan_curvatureReclass = arcpy.sa.Reclassify(out_plan_curvature, 'Value',
                                                      arcpy.sa.RemapRange(reclassCurvature), missing_values="NODATA") * mask_raster
        out_plan_curvatureReclass.save(out_profile_curvatureR)

        array_evidence = [inLULC, outSlopeR, inLithology, out_profile_curvatureR, out_plan_curvatureR]

        simulated_landslides = os.path.join(out_path, 'landslides{}.shp'.format(str(i)))
        landslidesSimulate.SimulateLandslide(initial_landslides, simulated_landslides, landslides_mapping_error_mean, landslides_mapping_error_stdev)

        in_landslides = landslidesSimulate.Landslides2Raster(simulated_landslides, arcpy.Raster(in_dem), mask_raster)
        in_landslides.save(os.path.join(out_path, "lsim{}.tif".format(i)))

        priorProb = weightEvidence.priorProbability(in_landslides)

        rastersResult = weightEvidence.conditionalProbability(in_landslides, array_evidence, out_stats_file, iteration=i)

        weightEvidence.woeMap(rastersResult, arcpy.Raster(in_dem), os.path.join(out_path_woe, "woeFinal{}.tif".format(str(i))))


    #     Clear intermediate results
        arcpy.Delete_management(os.path.join(out_path, 'landslides{}.shp'.format(str(i))))
        arcpy.Delete_management(os.path.join(out_path, "lsim{}.tif".format(i)))
        arcpy.Delete_management(outSlopeR)
        arcpy.Delete_management(outSlope)
        arcpy.Delete_management(out_plan_curvatureR)
        arcpy.Delete_management(out_profile_curvatureR)
        arcpy.Delete_management(out_plan_curvature)
        arcpy.Delete_management(outProfileCurvature)
        arcpy.Delete_management(dem_noise)

    # Stop
    stop = datetime.datetime.now()

    arcpy.CheckInExtension("Spatial")