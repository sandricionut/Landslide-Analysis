

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
                "raster_name\tclass\tweight_positive\tweight_negative\tcontrast\tweight_negative_sum\tarea_class_presence\tarea_total_presence_minus_class\tarea_class_absence\tarea_total_absence\ts2Wp\ts2wN\tstudentized\n")
            f.close()


    def math_rasters_size(self, in_rasters, out_rasters):
        extent_rasters = []
        for raster in in_rasters:
            extent_rasters.append(raster.extent)
        return None


    def prior_probability(self, raster):

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
            tabRaster, uniqueRaster1, unique_evidence = self.cross_tab_raster(raster1, raster)
            raster_name = os.path.splitext(os.path.basename(raster))[0]
            # raster_name = raster_name.split("_")[0]
            weight_negative_sum = 0

            raster_metadata = arcpy.Raster(raster)
            np_raster = arcpy.RasterToNumPyArray(raster)

            np_rasterResult = numpy.zeros_like(np_raster, dtype=numpy.float64)
            weight_positive_array = []
            weight_negative_array = []

            for u in unique_evidence:
                #Suprafata alunecari in clasa
                weight_positive = 0.0
                weight_negative = 0.0
                s2Wp = 0.0
                s2wN = 0.0
                area_class_presence = float(tabRaster[1][unique_evidence.index(u)]) #NPIX1
                area_total_presence_minus_class = float(self._total_presence - area_class_presence) #NPIX2
                area_class_absence = float(tabRaster[0][unique_evidence.index(u)]) #NPIX3
                area_total_absence = float(self._total - self._total_presence - area_class_presence + area_class_absence + area_class_presence) #NPIX4
                try:
                    weight_negative = self.negative_weight(area_class_presence, area_total_presence_minus_class, area_class_absence, area_total_absence)
                    weight_negative_sum = weight_negative_sum + weight_negative
                    weight_negative_array.append(weight_negative)
                except:
                    weight_negative_sum = weight_negative_sum + weight_negative
                    weight_negative_array.append(weight_negative)

                try:
                    weight_positive = self.positive_weight(area_total_presence_minus_class, area_class_presence, area_total_absence, area_class_absence)
                    # weight_positive = math.log( (area_class_presence / (area_class_presence + area_total_presence_minus_class)) / ( area_class_absence / (area_class_absence + area_total_absence)) )
                    weight_positive_array.append(weight_positive)
                except:
                    weight_positive_array.append(weight_positive)

                try:
                    s2Wp = 1 / (area_class_presence) + 1 / (area_class_absence)
                except:
                    pass

                try:
                    s2wN = 1 / (area_total_presence_minus_class) + 1 / (self._total - area_class_presence - (area_class_presence + area_class_absence))
                except:
                    pass

                contrast = self.contrast(weight_positive, weight_negative)
                studentized = self.studentized(s2Wp, s2wN)

                f_results_out.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(raster_name, u, weight_positive, weight_negative, contrast, weight_negative_sum, area_class_presence, area_total_presence_minus_class, area_class_absence, area_total_absence, s2Wp, s2wN, studentized, iteration))
                f_results_out.flush()

                numpy.place(np_rasterResult, np_raster == u, contrast)

            rasters_result.append(np_rasterResult)
        f_results_out.close()
        # print(rasters_result)
        return rasters_result


    def woe_map(self, conditional_probabilities_maps, metadata, raster_name):
        woe_map = numpy.zeros_like(conditional_probabilities_maps[0])
        for raster in conditional_probabilities_maps:
            woe_map = woe_map + raster

        np_result_arcgis = arcpy.NumPyArrayToRaster(woe_map, arcpy.Point(metadata.extent.XMin, metadata.extent.YMin), metadata.meanCellWidth, metadata.meanCellHeight)
        np_result_arcgis.save(raster_name)


    def contrast(self, weight_positive, weight_negative):
        return weight_negative - weight_positive


    def positive_weight(self, area_total_presence_minus_class, area_class_presence, area_total_absence, area_class_absence):
        return math.log( (area_total_presence_minus_class / (area_total_presence_minus_class + area_class_presence) ) / (area_total_absence / (area_total_absence + area_class_absence)) )


    def negative_weight(self, area_class_presence, area_total_presence_minus_class, area_class_absence, area_total_absence):
        return math.log( (area_class_presence / (area_class_presence + area_total_presence_minus_class)) / ( area_class_absence / (area_class_absence + area_total_absence)) )


    def studentized(self, s2Wp, s2wN):
        return math.sqrt(s2Wp + s2wN)


    def cross_tab_raster(self, raster1, raster2):
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

    def cross_tab_raster2(self, raster1, raster2):

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


