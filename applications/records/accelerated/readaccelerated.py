# -*- coding: utf-8 -*-
import pandas as pd
from itertools import islice
import collections
import re

def read_record(filename=None):
    with open(filename) as record_file:
        first, last, step = 1, 4, 2
        first_line, second_line = list(islice(record_file, first, last, step))
        line_info = first_line.split(",")
        name, date, station, angle, *_ = line_info
        line_info = second_line.split(",")
        number_of_points_string = line_info[0].split()[1]
        number_of_points = __obtain_digit(number_of_points_string)
        dt_with_second = line_info[1].split()[1]
        dt = __obtain_digit(dt_with_second)
        acc = pd.read_csv(filename, delimiter=r"\s+", skiprows=4, header=None)

        return collections.OrderedDict([('name', name),
                   ('date', date),
                   ('station', station),
                   ('angle', angle),
                   ('number_of_points', number_of_points),
                   ('dt', dt),
                   ('acc', acc)])

def __obtain_digit(dt):
    return float(re.sub("[^0123456789\.]", "", dt))

if __name__ == '__main__':
    filename = '/home/ebi/olomTahghighat/4/random/PEERNGARecords_Unscaled(1)/RSN88_SFERN_FSD262.AT2'
    info = read_record(filename)
    print(info)

