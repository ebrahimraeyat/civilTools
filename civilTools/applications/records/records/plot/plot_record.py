# -*- coding: utf-8 -*-

import pyqtgraph as pg
import numpy as np
#import os
import pandas as pd
from itertools import islice
from pandas import DataFrame
import collections
import re
#from PyQt4.QtCore import QTextStream, QFile, QIODevice
## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'c')


class Work_on_record_file(object):

    def __init__(self, record_file, dx):
        self.record_file = record_file
        self.dx = dx
        self.extract_record_prop()
        self.remove_end_incomplete_line_reshape_acc_convert_to_dataframe()
        self.calculate_density_function_with_dx()
        self.calculate_distribute_function()

    def extract_record_prop(self):
        with open(self.record_file) as record_file:
            head = list(islice(record_file, 1, 4, 2))
        earth_info = head[0].split(",")
        earthquake = earth_info[0]
        date = earth_info[1]
        station = earth_info[2]
        angle = earth_info[3]
        earth_info = head[1].split(",")
        number_of_points = earth_info[0].split()[1]
        dt = earth_info[1].split()[1]

        self.dt = Work_on_record_file.obtain_digit(dt)

        self.acc = pd.read_csv(self.record_file, delimiter=r"\s+", skiprows=4, header=None)

        self.return_dict = collections.OrderedDict([('name', earthquake),
                       ('date', date),
                       ('station', station),
                       ('angle', angle),
                       ('NPTS', number_of_points),
                       ('dt', self.dt)])
        return self.return_dict

    @staticmethod
    def obtain_digit(dt):
        return float(re.sub("[^0123456789\.]", "", dt))

    def remove_end_incomplete_line_reshape_acc_convert_to_dataframe(self):
        self.acc = self.acc.dropna(how="any")
        (row, col) = self.acc.shape
        self.n = row * col
        self.acc = self.acc.values.reshape(self.n, 1)
        time = np.arange(0, self.n * self.dt, self.dt)
        self.acc = DataFrame(self.acc, index=time)

    def calculate_density_function_with_dx(self):
        minimum = self.acc[0].min()
        maximum = self.acc[0].max()
        x_array = np.arange(minimum, maximum, self.dx)
        self.density_function = (self.acc.groupby(pd.cut(self.acc[0], x_array)).count()) \
         / self.n

    def calculate_distribute_function(self):
        self.distribute_function = self.density_function.cumsum()


if __name__ == '__main__':
    record_class = Work_on_record_file('/home/ebi/olomTahghighat/random/PEERNGARecords_Unscaled/RSN1685_NORTH151_JEN022.AT2')
    info = record_class.extract_record_prop()

    record_class.remove_end_incomplete_line_reshape_acc_convert_to_dataframe()
    record_class.group_acc_values_to_subrange_dx(.005)

