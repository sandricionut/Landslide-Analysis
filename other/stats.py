
import os
import sys
import numpy
# from sklearn.metrics import roc_auc_score
# from sklearn.metrics import average_precision_score
from sklearn import metrics
from sklearn import preprocessing
import arcpy


class Stats:


    def __init__(self, in_stats_file=None):
        if(in_stats_file is not None):
            self._in_stats_file = open(in_stats_file, "w") #in_stats_file
            # outFileResults = open(in_stats_file, "w")

    def write_header(self):
        self._in_stats_file.write("rasterName\tclass\tweightPositive\tweightNegative\tcontrast\tsumWnt\tareaClassPresence\tareaTotalPresenceMinusClass\tareaClassAbsence\tareaTotalAbsence\ts2Wp\ts2wN\tstudentized\titeration\n")
        self._in_stats_file.flush()

    def write_line(self):
        pass

    def append_to_stats_file(self):
        if(self._in_stats_file.closed):
            open(self._in_stats_file, "a")

    def close_stats_file(self):
        self._in_stats_file.close()


    def roc_auc(self, true_positive, false_positive):
        # y_true = numpy.array([0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0, 0, 0, 1, 1])
        # y_scores = numpy.array([0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0, 0.5, 0.5, 0.8, 0.25])
        y_true = numpy.array([0, 0, 1, 1])
        y_scores = numpy.array([0.5, 0.5, 0.8, 0.25])
        score = metrics.roc_auc_score(y_true, y_scores)
        print(score)

if __name__ == "__main__":

    cale_simulari = r"d:\Personal\Temp\SimulariNorm"
    cale_alunecari = r"d:\Personal\Temp\SimulariAlunecari"
    fisier_stats = r"d:\Personal\Temp\ROC.txt"
    # masca = r"d:\Personal\Temp\DateInitiale\Masca_PolygonToRasterInt.tif"
    fisier = open(fisier_stats, "w")

    arcpy.CheckInExtension("spatial")
    arcpy.env.overwriteOutput = True

    # wofe_array = arcpy.RasterToNumPyArray(cale_simulari).flatten()
    # alunecari_array = arcpy.RasterToNumPyArray(cale_alunecari).flatten()
    # masca_array = arcpy.RasterToNumPyArray(masca).flatten().astype(int)
    #
    # alunecari_array_masked = numpy.ma.masked_where(masca_array == 0, alunecari_array)
    # wofe_array_masked = numpy.ma.masked_where(masca_array == 0, wofe_array)
    #
    # fisier.write("{}\n".format([x for x in masca_array]))
    # fisier.write("{}\n".format([x for x in alunecari_array_masked]))
    # fisier.write("{}\n".format([x for x in wofe_array_masked]))
    # #
    # # alunecari_array_masked_modificat = numpy.where(alunecari_array == 0 and masca_array == 1, 0, alunecari_array_masked)
    # # y_true = numpy.array([0, 0, 1, 1])
    # # y_scores = numpy.array([0.5, 0.5, 0.8, 0.25])
    # # score = metrics.roc_auc_score(y_true, y_scores)
    # # print(score)
    # # print(alunecari_array_masked)
    # print(numpy.unique(alunecari_array_masked.astype(int)))
    # print(metrics.roc_auc_score(numpy.array(alunecari_array_masked), numpy.array(wofe_array_masked)))
    #
    # roc_value = average_precision_score(y_true=alunecari_array_masked, y_score=wofe_array_masked, average='weighted')
    # roc_value = metrics.roc_auc_score(y_true=preprocessing.label_binarize(y=alunecari_array_masked, classes=[0,1], neg_label=0, pos_label=1), y_score=wofe_array_masked, average='weighted')
    # fpr, tpr, thresholds = metrics.roc_curve(alunecari_array_masked, wofe_array_masked, pos_label=2)
    # metrics.auc(fpr, tpr)

    # limita = r"d:\Personal\Temp\Teste\Limita.shp"
    # imgCopy = arcpy.Raster(r"d:\Personal\Temp\Teste\limita.tif")
    # arcpy.env.snapRaster = imgCopy

    masca = r"D:\Personal\Temp\DateInitiale\Masca_PolygonToRaster.tif"

    for i in range(0, 11, 1):
        for j in range(0,100,1):
            # s.roc_auc(None, None)
            wofe_sim_folder = os.path.join(cale_simulari, "N{}".format(i))
            wofe_nume = "wf_{}_{}.tif".format(i, j)
            wofe_fara_masca = os.path.join(wofe_sim_folder, wofe_nume)
            # wofe_sim_folder = os.path.join(cale_simulari, "N{}".format(i))

            alunecari_nume = "ssltest{}.tif".format(j)
            # alunecari = arcpy.sa.Int(os.path.join(wofe_sim_folder, wofe_nume))

            alunecari = arcpy.Raster(masca) * arcpy.Raster(os.path.join(cale_alunecari, alunecari_nume))
            wofe = arcpy.Raster(masca) * arcpy.Raster(wofe_fara_masca)

            ref_raster = arcpy.Raster(wofe_fara_masca)

            wofe_array = arcpy.RasterToNumPyArray(wofe).flatten()
            alunecari_array = arcpy.RasterToNumPyArray(alunecari).flatten()
            masca_array = arcpy.RasterToNumPyArray(masca).flatten()

            # alunecari_array_masked = numpy.ma.masked_where(masca_array == 0, alunecari_array)
            # wofe_array_masked = numpy.ma.masked_where(masca_array == 0, wofe_array)

            wmasca = arcpy.NumPyArrayToRaster(numpy.array(wofe_array.reshape(ref_raster.height, ref_raster.width)), arcpy.Point(X=ref_raster.extent.XMin, Y=ref_raster.extent.YMin), x_cell_size=ref_raster.meanCellWidth, y_cell_size=ref_raster.meanCellHeight)

            amasca = arcpy.NumPyArrayToRaster(numpy.array(alunecari_array.reshape(ref_raster.height, ref_raster.width)), arcpy.Point(X=ref_raster.extent.XMin, Y=ref_raster.extent.YMin), x_cell_size=ref_raster.meanCellWidth, y_cell_size=ref_raster.meanCellHeight) * arcpy.Raster(masca)




            #
            # amasca.save(r"d:\Personal\Temp\Teste\amasca.tif")
            # wmasca.save(r"d:\Personal\Temp\Teste\wmasca.tif")
            #
            # arcpy.SetRasterProperties_management(r"d:\Personal\Temp\Teste\amasca.tif", data_type="GENERIC", nodata=[[1, 255]])
            # arcpy.SetRasterProperties_management(r"d:\Personal\Temp\Teste\wmasca.tif", data_type="GENERIC", nodata=[[1, 255]])

            # print(arcpy.Describe(wmasca).noDataValue)
            # nodata_wmasca = arcpy.Describe(r"d:\Personal\Temp\Teste\wmasca.tif").noDataValue
            # nodata_amasca = arcpy.Describe(r"d:\Personal\Temp\Teste\amasca.tif").noDataValue

            # print("No data: ", nodata_wmasca, nodata_amasca)
            wofe_array = arcpy.RasterToNumPyArray(wmasca).flatten()
            alunecari_array = arcpy.RasterToNumPyArray(amasca).flatten()

            # alunecari_array_masked = numpy.ma.masked_where(alunecari_array == 65535, alunecari_array)
            # wofe_array_masked = numpy.ma.masked_where(wofe_array < 0, wofe_array)

            alunecari_array_masked = alunecari_array[alunecari_array != 65535]
            wofe_array_masked = wofe_array[(wofe_array >= 0.0) & (wofe_array <= 1.0)]

            # print("W unique:", numpy.unique(alunecari_array_masked), alunecari_array_masked.shape)
            # print("W unique:", numpy.unique(wofe_array_masked), wofe_array_masked.shape)
            try:
                roc_value = metrics.roc_auc_score(numpy.array(alunecari_array_masked), numpy.array(wofe_array_masked))
                # print(roc_value)

                fisier.write("{}\t{}\t{}\n".format(i, j, roc_value))
                fisier.flush()
            except Exception as e:
                print("E: ", e)
                pass

            # sys.exit()

        # sys.exit()
    #
    fisier.close()

    arcpy.CheckOutExtension("spatial")