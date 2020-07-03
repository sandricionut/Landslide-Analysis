

import arcpy
import os
import sys
import tempfile

arcpy.env.scratchWorkspace = r""


raster_path = arcpy.GetParameterAsText(1)

obj_raster = arcpy.Raster(raster_path)
cell_width = obj_raster.meanCellWidth
cell_height = obj_raster.meanCellHeight
xmin = obj_raster.extent.XMIN
ymin = obj_raster.extent.YMIN

raster = arcpy.RasterToNumPyArray(obj_raster)

# numpy logic here
result_numpy = None

out_raster = arcpy.NumPyArrayToRaster(result_numpy, arcpy.Point(xmin, ymin), cell_height, cell_width, -9999)
out_raster.save(os.path.join(tempfile.gettempdir(), "path to name.tif"))
out_raster.save(r"in_memory\path to name.tif")