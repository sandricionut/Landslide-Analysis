
import os
import sys
import numpy
from sklearn.metrics import roc_auc_score


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
        score = roc_auc_score(y_true, y_scores)
        print(score)



if __name__ == "__main__":


    s = Stats()
    s.roc_auc(None, None)