import numpy as np
import pandas as pd
from .readaccelerated import read_record
from scipy import interpolate, integrate
import scipy

class Accelerated(object):

    def __init__(self, filename=None, direction='x', dx=.005):
        self.accelerated_info = read_record(filename)
        self.direction = direction
        self.dt = self.accelerated_info['dt']
        self.dx = dx
        self.n = 0
        self.time, self.acc = self.remove_end_incomplete_line_then_reshape_acc_convert_to_dataframe()
        self.reset_prop()
        self.dirty = False

    def __str__(self):
        max_r_tow = max(self.r_tow)
        area_of_s_w = np.trapz(self.s_w, self.ws)
        s = f'maximum R_tow = {max_r_tow}\n'
        s += f'Area of s_w = {area_of_s_w}\n'
        return s

    def reset_prop(self):
        self.time_history = pd.Series(self.acc, index=self.time, name='acc')
        self.duration = self.n * self.dt
        print(self.duration)
        self.min = min(self.acc)
        self.max = max(self.acc)
        self.x = np.arange(self.min, self.max, self.dx)
        self.density_func = self.density_function()
        self.distribute_func = self.distribute_function()
        self.tow, self.r_tow = self.autocorrolation()
        self.ws, self.s_w = self.spectral_density_function()
        self.freq, self.fourier_amplitude = self.fourier()
        self.dirty = True

    def interpolate_acceleration(self, new_dt):
        ''' interpolates acceleration with new dt'''
        self.dt = new_dt
        self.accelerated_info['dt'] = new_dt
        tck = interpolate.splrep(self.time, self.acc, s=0)
        self.time = np.arange(0, self.duration, new_dt)
        self.acc = interpolate.splev(self.time, tck, der=0)
        self.n = len(self.acc)
        self.reset_prop()

    def scale(self, sf=1):
        '''scales acceleration to sf factor '''
        self.acc = sf * self.acc / abs(self.acc).max()
        self.reset_prop()

    def remove_end_incomplete_line_then_reshape_acc_convert_to_dataframe(self):
        acc = self.accelerated_info['acc']
        acc = acc.dropna(how="any")
        row, col = acc.shape
        self.n = row * col
        acc = acc.values.reshape(self.n, 1)
        acc = acc[:,0]
        time = np.arange(0, self.n * self.dt, self.dt)
        return time, acc

    def density_function(self):
        return (self.time_history.groupby(pd.cut(self.time_history, self.x)).count()) / self.n

    def distribute_function(self):
        return self.density_function().cumsum()

    def temporal_mean(self):
        return self.acc.mean()

    def temporal_mean_df(self):
        ''' calculate temporal_mean using density_function'''
        acc = self.time_history['acc']
        minimum = acc.min() + self.dx / 2.
        maximum = acc.max() - self.dx / 2.
        x_array = np.arange(minimum, maximum, self.dx)
        return (x_array * self.density_function().T).mean().mean()

    def autocorrolation(self):
        v = self.time_history
        r_tow = np.correlate(v,v, 'full')
        tow = np.linspace(-self.duration, self.duration, len(r_tow))
        return tow, r_tow

    def spectral_density_function(self):
        ws = np.linspace(-30,30, 120)
        s_w = []
        for w in ws:
            s = np.trapz(self.r_tow * np.cos(w*self.tow), self.tow) / (2 * np.pi)
            s_w.append(s)
        return ws, s_w

    def canai_tajimi(self, s0, w0, xi0, w):
        var = (2 * xi0 * w0 * w) ** 2
        s_x = s0 * (w0 ** 4 + var) / ((w0 ** 2 - w ** 2) ** 2 + var)
        return s_x

    def canai_tajimis(self, s0, w0, xi0):
        s_w = []
        ws = np.linspace(-30, 30, 200)
        for w in ws:
            s_w.append(self.canai_tajimi(s0, w0, xi0, w))
        return ws, s_w

    def effective_duration_index(self):
        # ''' 
        # calculate effective duration of acceleration with
        # trifunac algorithm. is based on the mean-square integral
        # of amplitude which is related to the seismic energy content
        # of the ground motion ( Trifunac and Brady, 1975)
        # '''

        acc_pow2 = (self.time_history.values) ** 2
        acc_pow2_cumtrapz = integrate.cumtrapz(acc_pow2) / np.trapz(acc_pow2)
        index_5 = (acc_pow2_cumtrapz < 0.05).sum()
        index_95 = (acc_pow2_cumtrapz < 0.95).sum()
        eff_du = round((index_95 - index_5) * self.dt, 1)
        return eff_du, index_5, index_95

    def cut(self, end, start=None): 
        if end > self.n:
            extra_zeros = pd.Series(np.zeros(end - self.n), index = np.arange(self.n, end) * self.dt)
            self.time_history.append(extra_zeros)
            print(self.time_history)
            print(extra_zeros)

        time_history = self.time_history.iloc[start:end]
        self.n = len(time_history)
        self.acc = time_history.values
        duration = self.n * self.dt
        self.time = np.linspace(0, duration, self.n)
        print(f"acc={len(self.acc)}, time={len(self.time)}, dt={self.dt}, n={self.n}")    
        self.accelerated_info['number_of_points'] = self.n
        self.reset_prop()

    def fourier(self):
        n = self.nearest2coefficient()
        Y = np.fft.fft(self.acc, n)
        pyy = Y * np.conj(Y)
        pyy_real_part = np.array(pyy.real)/n
        freq = self.frequency(np.size(pyy_real_part))
        return freq, pyy_real_part[:freq.size]

    def nearest2coefficient(self):
        return 2**int(np.log(self.n)/np.log(2)+1)

    def frequency(self, n):
    #     nyquist = 1/(2.*dt)
        nyquist = 30
        freq = np.arange(5, n/2) / (n / 2.) * nyquist
        return freq

# class EnsembleRecord:

#     def __init__(self, process_records=[]):
#         self.number_of_records = len(process_records)
#         self.process_records = process_records
#         self.ensemble_records = []

#     @property
#     def number_of_points(self):
#         max_length = self.process_records[0].n
#         for record in self.process_records:
#             if record.n > max_length:
#                 max_length = record.n
#         return max_length

#     def unify_length_of_process_records(self):
#         for process_record in self.process_records:
#             if process_record.n < self.number_of_points:
#                 process_record[0] = 1




