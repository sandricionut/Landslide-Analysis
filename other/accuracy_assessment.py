
import os
import sys
import arcpy

# def get_images():
#     lst_images = []

if __name__ == "__main__":

    path_simulari = r"d:\Personal\Temp\Simulari"
    path_simulari_norm = r"d:\Personal\Temp\SimulariNorm"
    path_simulari_zscore = r"d:\Personal\Temp\SimulariZScore"

    for dirs in os.walk(path_simulari):
    # for root, dirs, files in os.walk(path_simulari):
        # print("Root: ", root)
        # print("Basename root:", os.path.basename(root), os.path.dirname(root))
        # print("Foldere: ", dirs)
        # print("Fisiere: ", files)
        for folder in dirs[1]:
            if(folder == "N0"):
                nume_folder = os.path.basename(folder)
                cale_simulare = os.path.join(path_simulari_norm, nume_folder)
                cale_imagini = os.path.join(path_simulari, nume_folder)
                if(os.path.exists(os.path.join(path_simulari_norm, nume_folder)) != True):
                    os.mkdir(cale_simulare)

                arcpy.env.workspace = cale_imagini
                arcpy.env.overwriteOutput = True
                lst_images = arcpy.ListRasters(raster_type="TIF")
                # mean = arcpy.sa.CellStatistics(in_rasters_or_constants=lst_images, ignore_nodata="DATA", statistics_type="MEAN")
                # stdev = arcpy.sa.CellStatistics(in_rasters_or_constants=lst_images, ignore_nodata="DATA", statistics_type="STD")
                max = arcpy.sa.CellStatistics(in_rasters_or_constants=lst_images, ignore_nodata="DATA", statistics_type="MAXIMUM")
                min = arcpy.sa.CellStatistics(in_rasters_or_constants=lst_images, ignore_nodata="DATA", statistics_type="MINIMUM")

                for image in lst_images:
                    # img_zscore = (arcpy.Raster(image) - mean) / stdev
                    # img_zscore.save(os.path.join(path_simulari_zscore, image))
                    img_norm = (arcpy.Raster(image) - min) / (max - min)
                    img_norm.save(os.path.join(cale_simulare, image))