

import os
import numpy
import arcpy
from other import tacuda, randomSelection
from src import wofe
import datetime

class WofESimulations():

    def __init__(self, out_woe_map, out_name_prefix):
        self._no_simulations = None
        self._out_woe_map = out_woe_map
        self._out_name_prefix = out_name_prefix

    def simulate(self, no_simulations, in_dem_sim, landslide_sim, stats_file, nominal_data, mask, noise_factor):
        # Generate noise for DEM
        # terrain_analysis = tacuda.taCUDA(georsgpu_path=georsgpu)
        start = datetime.datetime.now()
        i = no_simulations
        georsgpu = r"d:\GitHub\GeoRsGPU\GeoRsGPU\x64\Release\GeoRsGPU.exe"
        ta = tacuda.taCUDA(georsgpu_path=georsgpu)
        we = wofe.WofE()
        rs = randomSelection.RandomSelection()
        temp_location = in_dem_sim.get_temp_location()
        # for i in range(0, no_simulations, 1):
        print("Simulare: ", i)
        array_evidence = []
        # array_evidence.append(x for x in nominal_data)
        array_evidence = nominal_data
        dem_noise = in_dem_sim.dem_noise2(noise_factor=noise_factor)
        landslide_noise = landslide_sim.simulate()
        # print()
        #
        # Terrain analyses
        outSlope = os.path.join(temp_location, "slope{}.tif".format(str(i)))
        outProfileCurvature = os.path.join(temp_location, "profc{}.tif".format(str(i)))
        out_plan_curvature = os.path.join(temp_location, "planc{}.tif".format(str(i)))

        # Reclassified rasters
        outSlopeR = os.path.join(temp_location, "slopeR_{}.tif".format(str(i)))
        out_profile_curvatureR = os.path.join(temp_location, "profcR_{}.tif".format(str(i)))
        out_plan_curvatureR = os.path.join(temp_location, "plancR_{}.tif".format(str(i)))

        # Call georsgpu for terrain analyses - this can be replaced with any other terrain src software
        ta.slope(dem_noise, outSlope)
        ta.plan_curvature(dem_noise, outProfileCurvature)
        ta.profile_curvature(dem_noise, out_plan_curvature)

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

        outSlopeReclass = arcpy.sa.Reclassify(outSlope, "Value", arcpy.sa.RemapRange(reclassSlope), missing_values="NODATA") * mask
        outSlopeReclass.save(outSlopeR)

        outProfCurvatureReclass = arcpy.sa.Reclassify(outProfileCurvature, "Value", arcpy.sa.RemapRange(reclassCurvature), missing_values="NODATA") * mask
        outProfCurvatureReclass.save(out_plan_curvatureR)

        out_plan_curvatureReclass = arcpy.sa.Reclassify(out_plan_curvature, "Value", arcpy.sa.RemapRange(reclassCurvature), missing_values="NODATA") * mask
        out_plan_curvatureReclass.save(out_profile_curvatureR)

        array_evidence.append(outSlopeR)
        array_evidence.append(out_profile_curvatureR)
        array_evidence.append(out_plan_curvatureR)

        sel_landslides_train = os.path.join(temp_location, "ssltrain{}.shp".format(i))
        sel_landslides_test = os.path.join(temp_location, "ssltest{}.shp".format(i))
        sim_landslides_raster_train = os.path.join(temp_location, "ssltrain{}.tif".format(i))
        sim_landslides_raster_test = os.path.join(temp_location, "ssltest{}.tif".format(i))

        rs.random_select2(input_file=landslide_noise, out_file_train=sel_landslides_train, out_file_test=sel_landslides_test, train_size=70)

        in_landslides_train = landslide_sim.landslide2raster(in_landslides=sel_landslides_train, out_landslide=sim_landslides_raster_train, reference_raster=arcpy.Raster(dem_noise), mask=mask)
        in_landslides_test = landslide_sim.landslide2raster(in_landslides=sel_landslides_test, out_landslide=sim_landslides_raster_test, reference_raster=arcpy.Raster(dem_noise), mask=mask)
        # in_landslides.save(os.path.join(temp_location, "lsim{}.tif".format(i)))
        #
        priorProb = we.priorProbability(in_landslides_train)
        #
        rastersResult = we.conditionalProbability(in_landslides_train, array_evidence, stats_file, iteration=i)
        #
        we.woeMap(rastersResult, arcpy.Raster(dem_noise), os.path.join(self._out_woe_map, "{}_{}.tif".format(self._out_name_prefix, str(i))))

        stop = datetime.datetime.now()

        print("Timp simulare: ", stop - start)

#             Validation ROC-AUC
#             n_sim_landslides_raster_test = arcpy.RasterToNumPyArray(sim_landslides_raster_test)
        # n_raster_result = arcpy.RasterToNumPyArray(os.path.join(self._out_woe_map, "wf{}.tif".format(str(i))))
        # roc_auc = roc_auc_score(n_sim_landslides_raster_test, n_raster_result)
        # print(roc_auc)

