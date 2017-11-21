import math

pi = 3.14


class Punch:

	def __init__(self, foundation, column, b0=None, phi=0.75):
		self.foundation = foundation
		self.column = column
		self.b0 = b0
		self.phi = phi

	def __str__(self):
		def _title(title):
			line = '\n' + 20 * '-' + '\n'
			return line + title + line

		# foundation
		s = ''
		s += _title('Foundation')
		s += 'fc = {}\t MPa\n'.format(self.foundation.fc)
		s += 'd = {:0.0f}\t mm\n'.format(self.foundation.d)
		# punch
		s += _title('Punch Result')
		s += 'b0 = {:0.0f}\t mm\n'.format(self.b0)
		s += 'phi = {}\t\n'.format(self.phi)
		s += 'Vc1 = {:0.0f}\t KN\n'.format(self.__Vc1 / 1000)
		s += 'Vc2 = {:0.0f}\t KN\n'.format(self.__Vc2 / 1000)
		s += 'Vc3 = {:0.0f}\t KN\n'.format(self.__Vc3 / 1000)
		s += 'Vc = min(Vc1, Vc2, Vc3) = {:0.0f}\t KN\n'.format(self.__Vc / 1000)
		return s

	def calculate_b0(self):
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
		if not self.b0:
			self.b0 = self.calculate_b0()
		d = self.foundation.d
		beta = self.column.beta
		alpha_s = self.column.alpha_s
		fc = self.foundation.fc
		one_way_shear_capacity = math.sqrt(fc) * self.b0 * d / 6  * self.phi
		self.__Vc1 = one_way_shear_capacity * 2
		self.__Vc2 = one_way_shear_capacity * (1 + 2 / beta)
		self.__Vc3 = one_way_shear_capacity * (2 + alpha_s * d / self.b0) / 2
		self.__Vc = min(self.__Vc1, self.__Vc2, self.__Vc3)
		return self.__Vc


class ShearSteel(Punch):
	def __init__(self, foundation, column, Vu, b0=None, fy=340, phi=0.75):
		super().__init__(foundation, column, b0=b0, phi=phi)
		self.Vu = Vu
		self.fy = fy

	def __str__(self):
		def _title(title):
			line = '\n' + 20 * '-' + '\n'
			return line + title + line

		# foundation
		s = ''
		s += _title('Foundation')
		s += 'fc = {}\t MPa\n'.format(self.foundation.fc)
		s += 'd = {:0.0f}\t mm\n'.format(self.foundation.d)
		# punch
		s += _title('Punch Result')
		s += 'b0 = {:0.0f}\t mm\n'.format(self.b0)
		s += 'phi = {}\t\n'.format(self.phi)
		s += 'Vc = {:0.0f}\t KN\n'.format(self.__Vc / 1000)
		return s

	def calculate_Vc(self):
		if not self.b0:
			self.b0 = self.calculate_b0()
		d = self.foundation.d
		fc = self.foundation.fc
		self.__Vc = math.sqrt(fc) * self.b0 * d / 6
		return self.__Vc

	def calculate_shear_steel(self):
		# TODO
		pass


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
	def __init__(self, fc, h, dl, ds, cover, d=None, shape=None):
		self.fc = fc
		self.shape = shape
		self.d = d
		if not d:
			self.d = h - cover - ds - dl / 2

