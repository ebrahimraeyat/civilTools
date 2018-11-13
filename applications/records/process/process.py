import pandas as pd
import numpy as np

class Process(object):

	def __init__(self, accelerations=None):
		'''accelerations is a dictionary '''
		self.accelerations = accelerations

	def set_properties(self):
		accelerated = [*self.accelerations.values()][0]
		self.time = accelerated.time
		self.tow = accelerated.tow
		self.ws = accelerated.ws
		self.x = accelerated.x

		self.df_accelerations = pd.DataFrame(index=self.time)
		self.df_r_tow = pd.DataFrame(index=self.tow)
		self.df_s_w = pd.DataFrame(index=self.ws)
		self.df_density_function = pd.DataFrame(index=self.x[:-1])
		for key, value in self.accelerations.items():
			self.df_accelerations[key] = value.acc
			self.df_r_tow[key] = value.r_tow
			self.df_s_w[key] = value.s_w
			self.df_density_function[key] = value.density_func
		# print(self.df_density_function)

	def reset_prop(self):
		self.ex = self.expected_pow(1)
		self.ex2 = self.expected_pow(2)
		self.ex3= self.expected_pow(3)
		self.density_func = self.density_function() 
		self.r_tow = self.autocorrolation()
		self.s_w = self.spectral_density_function()

	def expected_pow(self, n):
		return self.df_accelerations.pow(n).mean(axis=1).values

	def density_function(self):
		return self.df_density_function.mean(axis=1).values

	def autocorrolation(self):
		return self.df_r_tow.mean(axis=1).values

	def spectral_density_function(self):
		return self.df_s_w.mean(axis=1).values

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
		