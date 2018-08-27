

import arcpy
import random

class RandomSelection():

    def __init__(self):
        pass

    def percent_to_number(self, population, percent):
        # if(percent > 100):
        # assert percent < 100
        return int(percent * population / 100)

    def random_select(self, input_file, out_file, train_size=30):
        list_landslides = [row[0] for row in arcpy.da.SearchCursor(in_table=input_file, field_names=["OID@"])]
        k = self.percent_to_number(len(list_landslides), train_size)
        sample_landslides = random.sample(list_landslides, k)
        # print("OID@ IN {}".format(tuple(sample_landslides)))
        arcpy.MakeFeatureLayer_management(in_features=input_file, out_layer="random_landslides", where_clause="{} IN {}".format(arcpy.Describe(input_file).OIDFieldName, tuple(sample_landslides)))
        arcpy.CopyFeatures_management(in_features="random_landslides", out_feature_class=out_file)
        arcpy.Delete_management("random_landslides")
        # print(k, len(list_landslides))
        return out_file

    def random_select2(self, input_file, out_file_train, out_file_test, train_size=30):
        list_landslides = [row[0] for row in arcpy.da.SearchCursor(in_table=input_file, field_names=["OID@"])]
        k = self.percent_to_number(len(list_landslides), train_size)
        sample_landslides = random.sample(list_landslides, k)
        # print("OID@ IN {}".format(tuple(sample_landslides)))
        arcpy.MakeFeatureLayer_management(in_features=input_file, out_layer="random_landslides_train", where_clause="{} IN {}".format(arcpy.Describe(input_file).OIDFieldName, tuple(sample_landslides)))
        arcpy.CopyFeatures_management(in_features="random_landslides_train", out_feature_class=out_file_train)
        arcpy.Delete_management("random_landslides_train")


        arcpy.MakeFeatureLayer_management(in_features=input_file, out_layer="random_landslides_test", where_clause="{} NOT IN {}".format(arcpy.Describe(input_file).OIDFieldName, tuple(sample_landslides)))
        arcpy.CopyFeatures_management(in_features="random_landslides_test", out_feature_class=out_file_test)
        arcpy.Delete_management("random_landslides_test")
        # print(k, len(list_landslides))
        return out_file_train, out_file_test