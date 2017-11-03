# -*- coding: utf-8 -*-
import pandas as pd
from itertools import islice
import collections
import re


class ReadRecord:

    def __init__(self, filename=None):
        self.filename = filename
        self.extract_record_prop()

    def extract_record_prop(self):
        with open(self.filename) as record_file:
            two_line_head_of_filename = list(islice(record_file, 1, 4, 2))
        first_line_head_info = two_line_head_of_filename[0].split(",")
        name = first_line_head_info[0]
        date = first_line_head_info[1]
        station = first_line_head_info[2]
        angle = first_line_head_info[3]
        two_line_head_info = two_line_head_of_filename[1].split(",")
        number_of_points_string = two_line_head_info[0].split()[1]
        number_of_points = ReadRecord.obtain_digit(number_of_points_string)
        dt_with_second = two_line_head_info[1].split()[1]
        dt = ReadRecord.obtain_digit(dt_with_second)
        acc = pd.read_csv(self.filename, delimiter=r"\s+", skiprows=4, header=None)

        self.info_dict = collections.OrderedDict([('name', name),
                       ('date', date),
                       ('station', station),
                       ('angle', angle),
                       ('number_of_points', number_of_points),
                       ('dt', dt),
                       ('acc', acc)])

    @property
    def acc(self):
        return self.info_dict['acc']

    @staticmethod
    def obtain_digit(dt):
        return float(re.sub("[^0123456789\.]", "", dt))
