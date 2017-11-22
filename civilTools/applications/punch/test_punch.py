import unittest
from punch import Column, Foundation, Punch, ShearSteel


class Column_Test(unittest.TestCase):

	def setUp(self):
		self.column = Column(c1=300, c2=700)

	def test_column_shape_is_rec(self):
		self.assertEqual(self.column.shape, 'rec')

	def test_column_position_is_center(self):
		self.assertIs(self.column.pos, 'center')

	def test_beta(self):
		self.assertAlmostEqual(self.column.beta, 7/3, delta=.00001)

	def test_alpha_s(self):
		self.assertEqual(self.column.alpha_s, 40)


class Foundation_Test(unittest.TestCase):

	def setUp(self):
		self.fou = Foundation(fc=30, h=200, dl=10, ds=10, cover=20)

	def test_shape_is_None(self):
		self.assertIsNone(self.fou.shape)

	def test_effective_depth(self):
		self.assertEqual(self.fou.d, 165)


class Punch_Test(unittest.TestCase):
	def setUp(self):
		column = Column(c1=300, c2=700)
		fou = Foundation(fc=30, h=200, dl=10, ds=10, cover=20)
		self.punch = Punch(fou, column)
	
	def test_b0(self):
		b0 = self.punch.calculate_b0()
		self.assertEqual(b0, 2660)

	def test_Vc(self):
		Vc = self.punch.calculate_Vc()
		self.assertAlmostEqual(Vc, 558060.8, delta=0.1)


class ShearSteel_Vc_Test(unittest.TestCase):
	def setUp(self):
		self.column = Column(c1=400, c2=400)
		fou = Foundation(fc=25, h=200, dl=10, ds=10, cover=20)
		self.punch = Punch(fou, self.column)
		self.shear_steel = ShearSteel(fou, self.column, Vu=671.200, fy=300)
		self.Vc = self.shear_steel.calculate_Vc()
		self.require_Av_per_s = self.shear_steel.require_Av_per_s()

	def test_beta(self):
		self.assertEqual(self.column.beta, 1)

	def test_b0(self):
		b0 = self.punch.calculate_b0()
		self.assertEqual(b0, 2260)

	def test_Vc_without_shear_steel(self):
		Vc = self.punch.calculate_Vc()
		self.assertAlmostEqual(Vc, 466125.0, delta=0.1)

	def test_Vc_with_shear_steel(self):
		self.assertAlmostEqual(self.Vc, 310750.0, delta=.1)

	def test_require_Av_per_s(self):
		self.assertAlmostEqual(self.require_Av_per_s, 11.8, delta=.01)

	def test_max_Av_per_s(self):
		max_Av_per_s = self.shear_steel.max_Av_per_s()
		self.assertLess(self.require_Av_per_s, max_Av_per_s)

	def test_curr_Av(self):
		curr_Av = self.shear_steel.curr_Av()
		self.assertAlmostEqual(curr_Av, 904, delta=1.0)

	def test_require_dist_between_shear_reinforcement(self):
		s_req = self.shear_steel.require_dist_between_shear_reinforcement()
		self.assertAlmostEqual(s_req, 76.6, delta=.1)