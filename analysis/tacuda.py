

import os
import sys
import arcpy
import subprocess
import tempfile


class taCUDA():
    pass

    def __init__(self):
        pass

    def calculate(self, inFile, outFile, command, options=None):
        if(options is not None):
            pass
        else:
            sincronizare = subprocess.Popen(r"d:\GitHub\GeoRsGPU\GeoRsGPU\x64\Release\GeoRsGPU.exe {} {} {}".format(command, inFile, outFile), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        result, error = sincronizare.communicate()
        # return result, error