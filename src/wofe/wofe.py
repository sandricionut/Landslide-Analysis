

import os
import arcpy
import numpy
import math

class WeigtEvidence():

    def __init__(self):

        self._NPIX1 = 0
        self._NPIX2 = 0
        self._NPIX3 = 0
        self._NPIX4 = 0
        self._noData = 255
        self._total_presence = 0
        self.__total_absence = 0
        self._total = 0
        self._nrows = 0
        self._ncols = 0

    def set_stats_file(self, in_stats):
        if (os.path.exists(in_stats)):
            f = open(in_stats, "w")
            f.write(
                "raster_name\tclass\tweightPositive\tweightNegative\tcontrast\tweight_negative_sum\tareaClassPresence\tareaTotalPresenceMinusClass\tareaClassAbsence\tarea_total_absence\ts2Wp\ts2wN\tstudentized\n")
            f.close()


    def math_rasters_size(self, in_rasters, out_rasters):
        extent_rasters = []
        for raster in in_rasters:
            extent_rasters.append(raster.extent)
        return None


    def priorProbability(self, raster):

        raster_array = arcpy.RasterToNumPyArray(raster)
        unique_values = numpy.unique(raster_array, return_counts=True)

        presence = unique_values[1][1]
        absence = unique_values[1][0]
        total = presence + absence
        self._total_presence = presence
        self.__total_absence = absence
        self._total = total

        return presence / total


    def posterior_probability(self, prior, conditional):
        pass

    def posterior_odds(self, prior, conditional):
        pass


    def conditional_probability(self, raster1, evidence_array, out_stats_file, iteration=0):

        # f_results_out = open(os.path.normpath(os.path.join(out_stats_file)), 'a')
        # self.set_stats_file(in_stats=out_stats_file)

        f_results_out = open(os.path.join(out_stats_file), 'a')
        rasters_result = []

        # For each raster from raster array
        for raster in evidence_array:
            tabRaster, uniqueRaster1, uniqueEvidence = self.crossTabRaster(raster1, raster)
            raster_name = os.path.splitext(os.path.basename(raster))[0]
            # raster_name = raster_name.split("_")[0]
            weight_negative_sum = 0

            raster_metadata = arcpy.Raster(raster)
            np_raster = arcpy.RasterToNumPyArray(raster)

            np_rasterResult = numpy.zeros_like(np_raster, dtype=numpy.float64)
            weight_positive_array = []
            weightNegativeArray = []

            for u in uniqueEvidence:
                #Suprafata alunecari in clasa
                weightPositive = 0.0
                weightNegative = 0.0
                s2Wp = 0.0
                s2wN = 0.0
                areaClassPresence = float(tabRaster[1][uniqueEvidence.index(u)]) #NPIX1
                areaTotalPresenceMinusClass = float(self._total_presence - areaClassPresence) #NPIX2
                areaClassAbsence = float(tabRaster[0][uniqueEvidence.index(u)]) #NPIX3
                area_total_absence = float(self._total - self._total_presence - areaClassPresence + areaClassAbsence + areaClassPresence) #NPIX4
                try:
                    weightNegative = self.negativeWeight(areaClassPresence, areaTotalPresenceMinusClass, areaClassAbsence, area_total_absence)
                    weight_negative_sum = weight_negative_sum + weightNegative
                    weightNegativeArray.append(weightNegative)
                except:
                    weight_negative_sum = weight_negative_sum + weightNegative
                    weightNegativeArray.append(weightNegative)

                try:
                    weightPositive = self.positiveWeight(areaTotalPresenceMinusClass, areaClassPresence, area_total_absence, areaClassAbsence)
                    # weightPositive = math.log( (areaClassPresence / (areaClassPresence + areaTotalPresenceMinusClass)) / ( areaClassAbsence / (areaClassAbsence + area_total_absence)) )
                    weight_positive_array.append(weightPositive)
                except:
                    weight_positive_array.append(weightPositive)

                try:
                    s2Wp = 1 / (areaClassPresence) + 1 / (areaClassAbsence)
                except:
                    pass

                try:
                    s2wN = 1 / (areaTotalPresenceMinusClass) + 1 / (self._total - areaClassPresence - (areaClassPresence + areaClassAbsence))
                except:
                    pass

                contrast = self.contrast(weightPositive, weightNegative)
                studentized = self.studentized(s2Wp, s2wN)

                f_results_out.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(raster_name, u, weightPositive, weightNegative, contrast, weight_negative_sum, areaClassPresence, areaTotalPresenceMinusClass, areaClassAbsence, area_total_absence, s2Wp, s2wN, studentized, iteration))
                f_results_out.flush()
                # print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(raster_name, u, weightPositive, weightNegative, contrast, weight_negative_sum, areaClassPresence, areaTotalPresenceMinusClass, areaClassAbsence, area_total_absence, s2Wp, s2wN, studentized, iteration))

                numpy.place(np_rasterResult, np_raster == u, contrast)

            rasters_result.append(np_rasterResult)
        f_results_out.close()
        # print(rasters_result)
        return rasters_result


    def woeMap(self, conditionalProbabilitiesMaps, metadata, raster_name):
        woeMap = numpy.zeros_like(conditionalProbabilitiesMaps[0])
        for raster in conditionalProbabilitiesMaps:
            woeMap = woeMap + raster

        npResultArcGIS = arcpy.NumPyArrayToRaster(woeMap, arcpy.Point(metadata.extent.XMin, metadata.extent.YMin), metadata.meanCellWidth, metadata.meanCellHeight)
        npResultArcGIS.save(raster_name)


    def contrast(self, weightPositive, weightNegative):
        return weightNegative - weightPositive


    def positiveWeight(self, areaTotalPresenceMinusClass, areaClassPresence, area_total_absence, areaClassAbsence):
        return math.log( (areaTotalPresenceMinusClass / (areaTotalPresenceMinusClass + areaClassPresence) ) / (area_total_absence / (area_total_absence + areaClassAbsence)) )


    def negativeWeight(self, areaClassPresence, areaTotalPresenceMinusClass, areaClassAbsence, area_total_absence):
        return math.log( (areaClassPresence / (areaClassPresence + areaTotalPresenceMinusClass)) / ( areaClassAbsence / (areaClassAbsence + area_total_absence)) )


    def studentized(self, s2Wp, s2wN):
        return math.sqrt(s2Wp + s2wN)


    def crossTabRaster(self, raster1, raster2):
        # print(arcpy.Raster(raster2).extent)
        # print(arcpy.Raster(raster1).extent)
        raster1 = arcpy.RasterToNumPyArray(raster1).flatten()
        raster2 = arcpy.RasterToNumPyArray(raster2).flatten()

        unique_raster1 = [ x for x in numpy.unique(raster1) if x != self._noData ]
        unique_raster2 = [ x for x in numpy.unique(raster2) if (x != self._noData and x != -128)]

        # print(numpy.unique(raster2))

        raster1_cat_len = len(unique_raster1)
        raster2_cat_len = len(unique_raster2)

        table = numpy.zeros((raster1_cat_len, raster2_cat_len))
        # print(raster1, raster2)
        # print(unique_raster1, unique_raster2)
        i = 0
        for raster1_cat in unique_raster1:
            j = 0
            for raster2_cat in unique_raster2:
                table[i, j] = ((raster1 == raster1_cat) * (raster2 == raster2_cat)).sum()
                j = j + 1
            i = i + 1

        return table, unique_raster1, unique_raster2

    def crossTabRaster2(self, raster1, raster2):

        raster1 = arcpy.RasterToNumPyArray(raster1).flatten()
        raster2 = arcpy.RasterToNumPyArray(raster2).flatten()

        unique_raster1 = numpy.unique(raster1)
        unique_raster2 = numpy.unique(raster2)

        raster1_cat_len = len(unique_raster1)
        raster2_cat_len = len(unique_raster2)

        table = numpy.zeros((raster1_cat_len, raster2_cat_len))

        i = 0
        for raster1_cat in unique_raster1:
            j = 0
            for raster2_cat in unique_raster2:
                table[i, j] = ((raster1 == raster1_cat) * (raster2 == raster2_cat)).sum()
                j = j + 1
            i = i + 1

        return table, unique_raster1, unique_raster2


