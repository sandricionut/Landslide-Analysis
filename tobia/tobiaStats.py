

import os
import sys
import arcpy
import numpy
import scipy
import datetime

arcpy.env.overwriteOutput = True

def feature2Raster(inFeatureClass, referenceRaster, landslide=False):
    # inRasters must be as dictionary {path:'',valueField:'',name:''}
    refRaster = arcpy.Raster(referenceRaster)
    arcpy.env.extent = refRaster.extent
    arcpy.env.snapRaster = refRaster
    outRaster = r"d:\Personal\Temp\{}".format(inFeatureClass['name'])
    if(landslide):
        colFields = arcpy.ListFields(inFeatureClass['path'])
        if(inFeatureClass['classField'].upper() not in [x.name.upper() for x in arcpy.ListFields(inFeatureClass['path'])]):
            arcpy.AddField_management(inFeatureClass['path'], field_name="{}".format(inFeatureClass['classField']), field_type="SHORT")

        with arcpy.da.UpdateCursor(inFeatureClass['path'], field_names=["{}".format(inFeatureClass['classField'])]) as cursor:
            for row in cursor:
                row[0] = 1
                cursor.updateRow(row)
        arcpy.PolygonToRaster_conversion(inFeatureClass['path'], value_field="{}".format(inFeatureClass['classField']), out_rasterdataset=outRaster, cellsize=refRaster.meanCellWidth)
        out = {}
        out['noData'] = arcpy.Raster(outRaster).noDataValue
        out['path'] = outRaster
        out['classField'] = inFeatureClass['classField']
        out['name'] = inFeatureClass['name']
        return out
    else:
        try:
            arcpy.PolygonToRaster_conversion(inFeatureClass['path'], value_field="{}".format(inFeatureClass['classField']), out_rasterdataset=outRaster, cellsize=refRaster.meanCellWidth)
        except:
            print('Eroare')
            print(arcpy.GetMessages(2))
        out = {}
        out['noData'] = arcpy.Raster(outRaster).noDataValue
        out['path'] = outRaster
        out['classField'] = inFeatureClass['classField']
        out['name'] = inFeatureClass['name']
        # print('NoData: ', arcpy.Raster(outRaster).noDataValue)
        return out

def prepareForWriting(landslides, rastersArray):
    # Must be dictionaries
    dataArray = []
    # Landslides
    lArray = arcpy.RasterToNumPyArray(landslides).flatten()
    vlandslides = [x for x in lArray]
    dataArray.append(vlandslides)
    uniqueClasses = {}
    uniqueClasses[int(landslides.noDataValue)] = 'No landslide'
    uniqueClasses[1] = 'Landslide'
    tLandslides = [uniqueClasses[x] for x in lArray]
    dataArray.append(tLandslides)

    # Iteration over conditional factors
    for raster in rastersArray:
        uniqueClasses = {}
        with arcpy.da.SearchCursor(raster['path'], field_names=["VALUE", "{}".format(raster['classField'])], sql_clause=("DISTINCT", None)) as cursor:
            for row in cursor:
                uniqueClasses[row[0]] = row[1]
        # print(raster['name'])
        uniqueClasses[int(raster['noData'])] = 'NAN'
        fArray = arcpy.RasterToNumPyArray(raster['path']).flatten()
        # print(numpy.unique(t, return_counts=True))
        fClasses = [uniqueClasses[x] for x in fArray]
        dataArray.append(fClasses)
    return zip(*dataArray)

def writeToTextFile(dataArray, outFile):
    outFileText = open(outFile, "w")
    for row in numpy.array(list(dataArray)):
        # outFileText.write("{}\t{}\t'{}'\n".format(row[0], row[1], row[2]))
        outFileText.write("{}\n".format("\t".join(numpy.array(list(row)))))
        outFileText.flush()
    outFileText.close()


if __name__ == "__main__":

    start = datetime.datetime.now()
    for zona in ['Oltet', 'Lovistea', 'Glodeni']:
        for type in ['landslides_body', 'landslides_sources']:
            # inTobia = r"d:\Dropbox\TOBIA\Date\{}\Rezultate\slope7".format(zona)
            if(zona == 'Oltet'):
                # inLandslides = r"d:\Dropbox\TOBIA\Date\{}\Vectori\{}.shp".format(zona, 'landslides_sources')
                colnameLithology = "Litol_v2".upper()
                colnameLandslides = "tobia".upper()
                colnameTobia = "CLASSES"
                pathTobia = r"d:\Dropbox\TOBIA\Date\{}\Rezultate\slope7".format(zona)
                pathLandslides = r"d:\Dropbox\TOBIA\Date\{}\Vectori\{}.shp".format(zona, type)
                pathLithology = r"D:\Dropbox\TOBIA\Date\Oltet\Vectori\Geologie_Oltet.shp"

                # Lithology Oltet
                lithology = {}
                lithology['path'] = pathLithology
                lithology['classField'] = colnameLithology
                lithology['name'] = "lit{}".format(zona)
                outLithology = feature2Raster(lithology, pathTobia)

                # Tobia Oltet
                tobia = {}
                tobia['path'] = pathTobia
                tobia['classField'] = colnameTobia
                tobia['name'] = "tobia{}".format(zona)
                tobia['noData'] = 255

                # Landslides
                tLandslides = {}
                tLandslides['path'] = pathLandslides
                tLandslides['classField'] = colnameLandslides
                tLandslides['name'] = "oLandslides"
                outLandslides = feature2Raster(tLandslides, pathTobia, landslide=True)

                # WoE


                # dataArray = prepareForWriting(arcpy.Raster(outLandslides['path']), [outLithology, tobia])
                # outFile = r"d:\Dropbox\TOBIA\Date\{}_{}.txt".format(zona, type)
                # writeToTextFile(dataArray, outFile)


            elif(zona == 'Lovistea'):
                # inLandslides = r"d:\Dropbox\TOBIA\Date\{}\Vectori\{}.shp".format(zona, 'landslides_sources')
                colnameLithology = "Litol_v2".upper()
                colnameLandslides = "tobia".upper()
                colnameTobia = "CLASSES"
                pathTobia = r"d:\Dropbox\TOBIA\Date\{}\Rezultate\slope7".format(zona)
                pathLandslides = r"d:\Dropbox\TOBIA\Date\{}\Vectori\{}.shp".format(zona, type)
                pathLithology = r"D:\Dropbox\TOBIA\Date\Lovistea\Vectori\Geology.shp"

                # Lithology Oltet
                lithology = {}
                lithology['path'] = pathLithology
                lithology['classField'] = colnameLithology
                lithology['name'] = "lit{}".format(zona)
                outLithology = feature2Raster(lithology, pathTobia)

                # Tobia Oltet
                tobia = {}
                tobia['path'] = pathTobia
                tobia['classField'] = colnameTobia
                tobia['name'] = "tobia{}".format(zona)
                tobia['noData'] = 255

                # Landslides
                tLandslides = {}
                tLandslides['path'] = pathLandslides
                tLandslides['classField'] = colnameLandslides
                tLandslides['name'] = "oLandslides"
                outLandslides = feature2Raster(tLandslides, pathTobia, landslide=True)

                # dataArray = prepareForWriting(arcpy.Raster(outLandslides['path']), [outLithology, tobia])
                # outFile = r"d:\Dropbox\TOBIA\Date\{}_{}.txt".format(zona, type)
                # writeToTextFile(dataArray, outFile)


            elif(zona == 'Glodeni'):
                # inLandslides = r"d:\Dropbox\TOBIA\Date\{}\Vectori\{}.shp".format(zona, 'landslides_sources')
                colnameLithology = "Litol_v3".upper()
                colnameLandslides = "tobia".upper()
                colnameTobia = "CLASSES"
                pathTobia = r"d:\Dropbox\TOBIA\Date\{}\Rezultate\slope7".format(zona)
                pathLandslides = r"d:\Dropbox\TOBIA\Date\{}\Vectori\{}.shp".format(zona, type)
                pathLithology = r"d:\Dropbox\TOBIA\Date\Glodeni\Vectori\Geologia_Glodeni.shp"

                # Lithology Oltet
                lithology = {}
                lithology['path'] = pathLithology
                lithology['classField'] = colnameLithology
                lithology['name'] = "lit{}".format(zona)
                outLithology = feature2Raster(lithology, pathTobia)

                # Tobia Oltet
                tobia = {}
                tobia['path'] = pathTobia
                tobia['classField'] = colnameTobia
                tobia['name'] = "tobia{}".format(zona)
                tobia['noData'] = 255

                # Landslides
                tLandslides = {}
                tLandslides['path'] = pathLandslides
                tLandslides['classField'] = colnameLandslides
                tLandslides['name'] = "oLandslides"
                outLandslides = feature2Raster(tLandslides, pathTobia, landslide=True)

                # dataArray = prepareForWriting(arcpy.Raster(outLandslides['path']), [outLithology, tobia])
                # outFile = r"d:\Dropbox\TOBIA\Date\{}_{}.txt".format(zona, type)
                # writeToTextFile(dataArray, outFile)

    stop = datetime.datetime.now()
    print(stop - start)