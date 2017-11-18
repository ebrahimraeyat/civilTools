import math

pi = 3.14


class Punch:

	def __init__(self, foundation, column, phi=0.75):
		self.foundation = foundation
		self.column = column
		self.phi = phi

	def _calculate_b0(self):
		if self.column.shape == 'rec':
			if self.column.pos == 'center':
				a = self.column.c1 + self.foundation.d
				b = self.column.c2 + self.foundation.d
				return 2 * (a + b)
			elif self.column.pos == 'edge':
				a = self.column.c1 + self.foundation.d / 2
				b = self.column.c2 + self.foundation.d
				return 2 * a + b
			elif self.column.pos == 'corner':
				a = self.column.c1 + self.foundation.d / 2
				b = self.column.c2 + self.foundation.d / 2
				return a + b

		elif self.column.shape == 'circle':
			# TODO
			r = self.column.radius + self.foundation.d / 2
			return 2 * pi * r

	def calculate_Vc(self):
		b0 = self._calculate_b0()
		d = self.foundation.d
		beta = self.column.beta
		alpha_s = self.column.alpha_s
		fc = self.foundation.fc
		one_way_shear_capacity = math.sqrt(fc) * b0 * d / 6
		Vc1 = one_way_shear_capacity * 2
		Vc2 = one_way_shear_capacity * (1 + 2 / beta)
		Vc3 = one_way_shear_capacity * (2 + alpha_s * d / b0) / 2
		return min(Vc1, Vc2, Vc3) * self.phi


class ShearSteel(Punch):
	def __init__(self, foundation, column, Vu, fy=340, phi=0.75):
		super().__init__(foundation, column, phi)
		self.Vu = Vu
		self.fy = fy

	def calculate_Vc(self):
		b0 = self.calculate_b0()
		d = self.foundation.d
		fc = self.foundation.fc
		one_way_shear_capacity = math.sqrt(fc) * b0 * d / 6
		return one_way_shear_capacity


class Column:
	alpha_ss = {'center':40, 'edge':30, 'corner':20}
	def __init__(self, shape='rec', pos='center', **kwargs):
		self.shape = shape
		self.pos = pos
		self.alpha_s = Column.alpha_ss[pos]
		self.kwargs = kwargs
		self._dimentions()

	@property
	def beta(self):
		if self.shape is 'rec':
			c1 = self.c1
			c2 = self.c2
			beta = c1 / c2
			if beta < 1:
				beta = c2 / c1
		return beta

	def _dimentions(self):
		if self.shape is 'rec':
			self.c1 = self.kwargs['c1']
			self.c2 = self.kwargs['c2']

		elif self.shape is 'circle':
			self.radius = self.kwargs['radius']

	def area(self):
		if self.shape is 'rec':
			return self.c1 * self.c2

		elif self.shape is 'circle':
			return pi * self.radius ** 2


class Foundation:
	def __init__(self, fc, h, dl, ds, cover, shape=None):
		self.fc = fc
		self.shape = shape
		self.d = h - cover - ds - dl / 2

