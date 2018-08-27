
import subprocess


class taCUDA():
    pass

    def __init__(self, georsgpu_path):
        self._georsgpu = georsgpu_path

    def calculate(self, in_file, out_file, command, options=None):
        if(options is not None):
            pass
        else:
            print("{} {} {} {}".format(self._georsgpu, command, in_file, out_file))
            sincronizare = subprocess.Popen("{} {} {} {}".format(self._georsgpu, command, in_file, out_file), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        result, error = sincronizare.communicate()


    def profile_curvature(self, in_dem, out_prof_curvature):
        self.calculate(in_file=in_dem, out_file=out_prof_curvature, command="profileCurvature")


    def plan_curvature(self, in_dem, out_plan_curvature):
        self.calculate(in_file=in_dem, out_file=out_plan_curvature, command="planCurvature")


    def slope(self, in_dem, out_slope):
        self.calculate(in_file=in_dem, out_file=out_slope, command="slope")