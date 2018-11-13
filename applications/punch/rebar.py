import math

pi = math.pi

class Rebar:
	def __init__(self, d, rho=7850):
		self.d = d
		self.rho = rho

	@property
	def area(self):
		return pi * self.d ** 2 / 4

	def weight_per_len(self):
		return self.area * self.rho * 1e-6