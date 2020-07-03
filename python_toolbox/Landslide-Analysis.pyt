
import os
import arcpy
import numpy
import math

####################################################
# Custom code


class WeightsEvidence():

    def __init__(self):

        self._NPIX1 = 0
        self._NPIX2 = 0
        self._NPIX3 = 0
        self._NPIX4 = 0
        self._noData = 255
        self._totalPresence = 0
        self._totalAbsence = 0
        self._total = 0
        self._nrows = 0
        self._ncols = 0


    def priorProbability(self, raster):

        rasterArray = arcpy.RasterToNumPyArray(raster)
        uniqueValues = numpy.unique(rasterArray, return_counts=True)

        presence = uniqueValues[1][1]
        absence = uniqueValues[1][0]
        total = presence + absence
        self._totalPresence = presence
        self._totalAbsence = absence
        self._total = total

        return presence / total


    def posteriorProbability(self, prior, conditional):
        pass

    def posteriorOdds(self, prior, conditional):
        pass


    def conditionalProbability(self, raster1, evidenceArray, out_stats_file, iteration=0):

        fResultsOut = open(os.path.normpath(os.path.join(out_stats_file)), 'a')
        rastersResult = []

        # For each raster from raster array
        for raster in evidenceArray:
            tabRaster, uniqueRaster1, uniqueEvidence = self.crossTabRaster(raster1, raster)
            rasterName = os.path.splitext(os.path.basename(raster))[0] + ".txt"
            rasterName = rasterName.split("_")[0]
            weightNegativeSum = 0

            rasterMetadata = arcpy.Raster(raster)
            npRaster = arcpy.RasterToNumPyArray(raster)

            npRasterResult = numpy.zeros_like(npRaster, dtype=numpy.float64)
            weightPositiveArray = []
            weightNegativeArray = []

            for u in uniqueEvidence:
                #Suprafata alunecari in clasa
                weightPositive = 0.0
                weightNegative = 0.0
                s2Wp = 0.0
                s2wN = 0.0
                areaClassPresence = float(tabRaster[1][uniqueEvidence.index(u)]) #NPIX1
                areaTotalPresenceMinusClass = float(self._totalPresence - areaClassPresence) #NPIX2
                areaClassAbsence = float(tabRaster[0][uniqueEvidence.index(u)]) #NPIX3
                areaTotalAbsence = float(self._total - self._totalPresence - areaClassPresence + areaClassAbsence + areaClassPresence) #NPIX4
                try:
                    weightNegative = self.negativeWeight(areaClassPresence, areaTotalPresenceMinusClass, areaClassAbsence, areaTotalAbsence)
                    weightNegativeSum = weightNegativeSum + weightNegative
                    weightNegativeArray.append(weightNegative)
                except:
                    weightNegativeSum = weightNegativeSum + weightNegative
                    weightNegativeArray.append(weightNegative)

                try:
                    weightPositive = self.positiveWeight(areaTotalPresenceMinusClass, areaClassPresence, areaTotalAbsence, areaClassAbsence)
                    # weightPositive = math.log( (areaClassPresence / (areaClassPresence + areaTotalPresenceMinusClass)) / ( areaClassAbsence / (areaClassAbsence + areaTotalAbsence)) )
                    weightPositiveArray.append(weightPositive)
                except:
                    weightPositiveArray.append(weightPositive)

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

                fResultsOut.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(rasterName, u, weightPositive, weightNegative, contrast, weightNegativeSum, areaClassPresence, areaTotalPresenceMinusClass, areaClassAbsence, areaTotalAbsence, s2Wp, s2wN, studentized, iteration))
                fResultsOut.flush()
                # print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(rasterName, u, weightPositive, weightNegative, contrast, weightNegativeSum, areaClassPresence, areaTotalPresenceMinusClass, areaClassAbsence, areaTotalAbsence, s2Wp, s2wN, studentized, iteration))

                numpy.place(npRasterResult, npRaster == u, contrast)

            rastersResult.append(npRasterResult)
        fResultsOut.close()
        # print(rastersResult)
        return rastersResult


    def woeMap(self, conditionalProbabilitiesMaps, metadata, rasterName):
        woeMap = numpy.zeros_like(conditionalProbabilitiesMaps[0])
        for raster in conditionalProbabilitiesMaps:
            woeMap = woeMap + raster

        npResultArcGIS = arcpy.NumPyArrayToRaster(woeMap, arcpy.Point(metadata.extent.XMin, metadata.extent.YMin), metadata.meanCellWidth, metadata.meanCellHeight)
        npResultArcGIS.save(rasterName)


    def contrast(self, weightPositive, weightNegative):
        return weightNegative - weightPositive


    def positiveWeight(self, areaTotalPresenceMinusClass, areaClassPresence, areaTotalAbsence, areaClassAbsence):
        return math.log( (areaTotalPresenceMinusClass / (areaTotalPresenceMinusClass + areaClassPresence) ) / (areaTotalAbsence / (areaTotalAbsence + areaClassAbsence)) )


    def negativeWeight(self, areaClassPresence, areaTotalPresenceMinusClass, areaClassAbsence, areaTotalAbsence):
        return math.log( (areaClassPresence / (areaClassPresence + areaTotalPresenceMinusClass)) / ( areaClassAbsence / (areaClassAbsence + areaTotalAbsence)) )


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



####################################################




class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Landslides src"
        self.alias = "Landslides src toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [WofE, DemSimulations, LandslidesSimulations]


class WofE(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Weight of Evidence"
        self.description = "Calculates prior, conditional and posterior probability using Weight of Evidence model"
        self.canRunInBackground = False
        self.category = "Data driven models"

    def getParameterInfo(self):
        """Define parameter definitions"""
        # A raster file with presence and absence of the studied phenomena
        in_raster = arcpy.Parameter(name = "inRaster", displayName = "Presence/Absence", datatype = "GPRasterLayer", parameterType = "Required", direction = "Input")
        # A list with rasters used as evidence
        in_list_rasters = arcpy.Parameter(name = "inListRasters", displayName = "Evidence", datatype = "GPRasterLayer", multiValue=True, parameterType = "Required", direction = "Input")
        # A list with stats for WofE src
        out_stats_file = arcpy.Parameter(name = "outStatsFile", displayName = "Output statistics file", datatype = "DETextfile", multiValue=False, parameterType = "Required", direction = "Output")
        # A list with stats for WofE src - obtained by summing up the contrasts
        out_wofe_raster = arcpy.Parameter(name = "outWofERaster", displayName = "WofE raster", datatype = "GPRasterLayer", multiValue=False, parameterType = "Required", direction = "Output")

        params = [in_raster, in_list_rasters, out_stats_file, out_wofe_raster]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The src code of the tool."""
        arcpy.AddMessage(parameters[0])
        weightEvidence = WeightsEvidence()
        result = weightEvidence.conditionalProbability(parameters[0], parameters[1], parameters[2], iteration=0)
        weightEvidence.woeMap(result, arcpy.Raster(parameters[0]), parameters[3])
        return

class DemSimulations(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "MC dem simulations"
        self.description = "Simulates digital elevation models using Monte Carlo method"
        self.canRunInBackground = False
        self.category = "Simulations"

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The src code of the tool."""
        return

class LandslidesSimulations(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "MC landslides simulations"
        self.description = "Simulates landslides using Monte Carlo method"
        self.canRunInBackground = False
        self.category = "Simulations"

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The src code of the tool."""
        return
