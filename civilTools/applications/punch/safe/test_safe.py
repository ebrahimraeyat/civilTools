from .safe import Safe
import unittest


class TestSafe(unittest.TestCase):
	def setUp(self):
		self.safe = Safe("./applications/punch/safe/sattari_safe.xlsx")
		self.safe.program_control()

	def test_program_control(self):
		self.assertEqual(self.safe.program_name, "SAFE 2016")
		self.assertEqual(self.safe.version, "16.0.1")
		self.assertEqual(self.safe.curr_units.force, "N")
		self.assertEqual(self.safe.curr_units.length, " mm")
		self.assertEqual(self.safe.curr_units.temp, " C")
		self.assertEqual(self.safe.concrete_code, "ACI 318-14")

	