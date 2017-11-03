# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


class ProcessRecord:

    def __init__(self, record=None, dx=.05):
        self.acc = record.acc
        self.dx = dx
        self.n = 0
        self.dt = record.info_dict['dt']
        self.time_history_record = self.remove_end_incomplete_line_then_reshape_acc_convert_to_dataframe()

    def remove_end_incomplete_line_then_reshape_acc_convert_to_dataframe(self):
        acc = self.acc.dropna(how="any")
        (row, col) = acc.shape
        self.n = row * col
        acc = acc.values.reshape(self.n, 1)
        time = np.arange(0, self.n * self.dt, self.dt)
        return pd.DataFrame(acc, index=time, columns=['acc'])

    def density_function(self):
        acc = self.time_history_record[0]
        minimum = acc.min()
        maximum = acc.max()
        x_array = np.arange(minimum, maximum, self.dx)
        return (self.time_history_record.groupby(pd.cut(acc, x_array)).count()) / self.n

    def distribute_function(self):
        return self.density_function().cumsum()

    def temporal_mean(self):
        return self.time_history_record[0].mean()

    def temporal_mean_df(self):
        acc = self.time_history_record[0]
        minimum = acc.min() + self.dx / 2.
        maximum = acc.max() - self.dx / 2.
        x_array = np.arange(minimum, maximum, self.dx)
        return (x_array * self.density_function().T).mean().mean()


class EnsembleRecord:

    def __init__(self, process_records=[]):
        self.number_of_records = len(process_records)
        self.process_records = process_records
        self.ensemble_records = []

    @property
    def number_of_points(self):
        max_length = self.process_records[0].n
        for record in self.process_records:
            if record.n > max_length:
                max_length = record.n
        return max_length

    def unify_length_of_process_records(self):
        for process_record in self.process_records:
            if process_record.n < self.number_of_points:
                process_record[0] = 1




