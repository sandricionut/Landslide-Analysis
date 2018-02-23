
import arcpy
from analysis import wofe

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Landslides analysis"
        self.alias = "Landslides analysis toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [WofE, DemSimulations, LandslidesSimulations]


class WofE(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Weight of Evidence"
        self.description = "Calculates prior, conditional and posterior probability using Weight of Evidence model"
        self.canRunInBackground = False
        self.category = "Data drive models"

    def getParameterInfo(self):
        """Define parameter definitions"""
        # A raster file with presence and absence of the studied phenomena
        in_raster = arcpy.Parameter(name = "inRaster", displayName = "Presence/Absence", datatype = "GPRasterLayer", parameterType = "Required", direction = "Input")
        # A list with rasters used as evidence
        in_list_rasters = arcpy.Parameter(name = "inListRasters", displayName = "Evidence", datatype = "GPRasterLayer", multiValue=True, parameterType = "Required", direction = "Input")
        # A list with stats for WofE analysis
        out_stats_file = arcpy.Parameter(name = "outStatsFile", displayName = "Output statistics file", datatype = "DETextfile", multiValue=False, parameterType = "Required", direction = "Output")
        # A list with stats for WofE analysis - obtained by summing up the contrasts
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
        """The source code of the tool."""
        arcpy.AddMessage(parameters[0])
        weightEvidence = wofe.WofE()
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
        """The source code of the tool."""
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
        """The source code of the tool."""
        return
