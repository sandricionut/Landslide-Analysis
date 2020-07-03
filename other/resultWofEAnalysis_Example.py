
# coding: utf-8

import os
import pandas
import matplotlib.pyplot as plt
import numpy

class ProcessSimulations():


    def __init__(self, conf_interval):

        self.local_percentiles = self.getPercentiles(conf_interval, quartiles=True)
        self.local_step_percentiles = (self.local_percentiles[1] - self.local_percentiles[0]) / 2
        self.local_median_value = 0.5

    def get_unique_rasters(self, pd_rasters, column):
        """ Used for identify the number of unique rasters used in simulations. It requires the Pandas dataframe and the column name where the raster names are stored """
        unique_rasters = pandas.unique(pd_rasters[column])
        return unique_rasters

    def set_rasters_analysis(self, pd_rasters, raster_name, class_column, value_column, out_path):
        """ Is used for looping over simulations for each rasters and prepare the dataset for generating fan plots """
        # Loop over each raster
        # for raster in lst_unique_rasters:
        # Filter pandas dataframe by raster name
        pd_raster_series = pd_rasters[pd_rasters.rasterName == "{}".format(raster_name)]
        # print(pd_raster_series.head())

        # Get the unique classes for each raster
        unique_classes = pd_raster_series[class_column].unique()
        # print(unique_classes)

        # Write for each raster a file
        fileOut = os.path.join(out_path, "{}_{}.csv".format(raster_name, value_column))
        if(os.path.exists(fileOut)):
            os.remove(fileOut)
        for i in range(1, simulations, 1):
            # for columns in column - columns
            t_pRaster = pd_raster_series[pd_raster_series.iteration == i][[class_column, value_column]].transpose()[1:2]
            t_pRaster.to_csv(fileOut, header=False, mode="a")


        pd_rasters_arranged = pandas.read_csv(fileOut, names=unique_classes)
        return pd_rasters_arranged, unique_classes


    def generate_uncertainty_chart(self, pd_raster_series, raster_name, lst_unique_classes, value_column, save_fig_path, save_fig_format, xlabel=None, percentiles=None):
        """ Generate fan chart for uncertainty vizualization """

        # print("Grafice: ", raster_name)

        # Create matplotlib figure and subpplots
        fig, ax = plt.subplots()

        # Calculate second quartile series
        q_median_series = pd_raster_series.quantile(self.local_median_value, axis=0)

        # Starting color - yellow
        color = (0.5, 0.5, 0.0)

        # Set the upper and lower bound equal to median value - for each raster
        q_ub = 0.975
        q_lb = 0.025
        color_step = 0.025
        if(percentiles is None):
            q_ub = max(self.local_percentiles)
            q_lb = min(self.local_percentiles)
            color_step = 1.0 / len(self.local_percentiles)
        else:
            q_ub = max(percentiles)
            q_lb = min(percentiles)
            color_step = 1.0 / len(percentiles)


        red = 1.0
        green = 1.0
        blue = 0.0

        # Loop over percentiles values
        for x in self.local_percentiles:

            q_ub = q_ub - self.local_step_percentiles
            q_lb = q_lb + self.local_step_percentiles

            if(q_lb <= q_ub):

                # q_lb_color = (q_ub, 0.0, 0.0)
                # q_ub_color = (0.0, 0.0, q_ub)
                alpha_color = q_lb
                red = 1.0
                green = green - color_step
                # blue = blue + color_step
                if(red > 1.0):
                    red = 1.0
                elif(red < 0.0):
                    red = 0.0
                if(green > 1.0):
                    green = 1.0
                elif(green < 0.0):
                    green = 0.0
                if(blue > 1.0):
                    blue = 1.0
                elif(blue < 0.0):
                    blue = 0.0

                random_color = (red, green, blue)
                # print(random_color)
                # random_color = numpy.random.rand(3,)

                q_ub_series = pd_raster_series.quantile(q_ub, axis=0)
                q_lb_series = pd_raster_series.quantile(q_lb, axis=0)

                label = "{} - {}".format(q_lb, q_ub)
                if(q_lb == 0.5 and q_ub == 0.5):
                    label = q_lb
                else:
                    label = "{} - {}".format(q_lb, q_ub)

                ax.fill_between(lst_unique_classes, q_lb_series, q_ub_series, color=random_color, alpha=0.3, interpolate=True, label=label)

                # ax.legend([(q_ub, q_lb), ], x)
                # ax.fill(lst_unique_classes, q_lb_series, "blue", lst_unique_classes, q_ub_series, "red")

        # # Plot de median value - corresponds to second quartile
        ax.plot(lst_unique_classes, q_median_series, color="yellow", linewidth=0.5, label="")
        ax.legend()

        # Save the uncertainty chart
        plt.xticks(lst_unique_class, lst_unique_class)
        plt.ylabel("{}".format(xlabel))
        plt.xlabel("{}".format(raster_name))
        plt.grid(True)
        figure_name = os.path.join(save_fig_path, '{}_{}.{}'.format(raster_name, value_column, save_fig_format))
        fig.savefig(filename=figure_name, dpi=300)

    def getPercentiles(self, conf_interval, quartiles=False):
        # min = conf_interval / 2
        # max = 1.0 - min
        min = 0
        max = 1.0
        if(quartiles is not False):
            return [min, 0.25, 0.5, 0.75, max]
        else:
            # min = conf_interval / 2
            # max = 1.0 - min
            percentiles = numpy.arange(min, max, conf_interval)
            return percentiles

    def write_percentiles(self, pd_rasters, percentiles, out_file):
        percentiles_table = pd_rasters.quantile(percentiles, axis=0)
        percentiles_table.to_csv(out_file, header=True, mode="w")

if __name__ == "__main__":

    prodCond = r""
    data_path = r""
    out_path = r""

    # percentiles = getPercentiles(0.05)
    simulations = 1000

    pandas_simulation = pandas.read_csv(os.path.join(data_path, prodCond), sep="\t")
    columns =[column for column in list(pandas_simulation)[2:-1]]

    ps = ProcessSimulations(conf_interval=0.05)

    unique_rasters = ps.get_unique_rasters(pandas_simulation, "rasterName")
    percentiles = ps.getPercentiles(conf_interval=0.05, quartiles=True)
    # print(unique_rasters)

    for raster in unique_rasters:

        print("Processing raster with name: ", raster)

        # for column in columns:
        for column in ["contrast"]:
            rasters_arranged, lst_unique_class = ps.set_rasters_analysis(pd_rasters=pandas_simulation, raster_name=raster, class_column="class", value_column=column, out_path=out_path)

            ps.generate_uncertainty_chart(rasters_arranged, raster_name=raster, lst_unique_classes=lst_unique_class, value_column=column, save_fig_path=out_path, save_fig_format="png", xlabel="Contrast", percentiles=None)

            out_file_percentiles = os.path.join(out_path, "percentiles_{}.csv".format(raster))
            ps.write_percentiles(rasters_arranged, percentiles, out_file=out_file_percentiles)