import numpy as np
from numpy import sin, cos, exp, sqrt


class Vibration:
	def __init__(self, m, k, xi, u0, v0=0, duration=40, p0=1, w=0, cp0=1):
		self.m = m
		self.k = k
		self.xi = xi
		self.u0 = u0
		self.v0 = v0
		self.duration = duration
		self.p0 = p0
		self.cp0 = cp0
		self.w = w
		self.calculate_prop()

	def calculate_prop(self):
		self.wn = np.sqrt(self.k / self.m)
		self.wd = self.wn * np.sqrt(1 - self.xi ** 2)
		self.t = np.arange(0, self.duration, .01)
		self.wnt = self.wn * self.t
		self.wdt = self.wd * self.t
		self.xiwnt = self.xi * self.wnt

	def free_output(self):
		ut = exp(-self.xiwnt) * (self.u0 * cos(self.wdt) + 
			((self.v0 + self.xi * self.wn * self.u0) / self.wd) * sin(self.wdt))
		ut_push = exp(-self.xiwnt) * sqrt(self.u0 **2 + 
			((self.v0 + self.xi * self.wn * self.u0) / self.wd) **2)
		return ut, ut_push

	def sin_output(self):
		beta = self.w / self.wn
		static = self.p0 / self.k
		makhraj = (1 - beta ** 2) ** 2 + (2 * self.xi * beta) ** 2
		C = static * (1 - beta ** 2) / makhraj
		D = static * (-2 * self.xi * beta) / makhraj
		A = self.u0 - D
		B = (self.v0 + self.xi * self.wn * A - C * self.w) / (self.wd)
		transient = exp(-self.xiwnt) * (A * cos(self.wdt) + B * sin(self.wdt))
		steady_state = C * sin(self.w * self.t) + D * cos(self.w * self.t)
		ut = transient + steady_state
		return transient, steady_state, ut

	def constant_output(self):
		A = self.u0 - self.cp0 / self.k
		B = (self.v0 + self.xi * self.wn * A) / self.wd
		ut = exp(-self.xiwnt) * (A * cos(self.wdt) + B * sin(self.wdt)) + \
			 self.cp0 / self.k
		return ut

