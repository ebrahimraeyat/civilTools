from safe import Safe
import unittest


class TestSafe(unittest.TestCase):
	def setUp(self):
		self.safe = Safe("sattari_safe.xlsx")
		self.safe.program_control()

	def test_program_control(self):
		self.assertEqual(self.safe.program_name, "SAFE 2016")
		self.assertEqual(self.safe.version, "16.0.1")
		self.assertEqual(self.safe.curr_units.force, "N")
		self.assertEqual(self.safe.curr_units.length, " mm")
		self.assertEqual(self.safe.curr_units.temp, " C")
		self.assertEqual(self.safe.concrete_code, "ACI 318-14")

	def test_obj_geom_points(self):
		points = self.safe.obj_geom_points()
		no_of_points = len(list(points.keys()))
		coord = points[29]
		self.assertEqual(no_of_points, 84)
		self.assertEqual(coord.x, 0)
		self.assertEqual(coord.y, 5.1)
		self.assertEqual(coord.z, 0)
		self.assertEqual(coord.special, True)

		coord = points[72]
		self.assertAlmostEqual(coord.x, 4.46, places=2)
		self.assertAlmostEqual(coord.y, 11.034, places=3)
		self.assertEqual(coord.z, 0)
		self.assertEqual(coord.special, False)

	def test_obj_geom_areas(self):
		areas = self.safe.obj_geom_areas()
		no_of_areas = len(list(areas.keys()))
		self.assertEqual(no_of_areas, 16)
		point_numbers = areas[11]
		self.assertEqual(point_numbers, (76, 75, 73, 72))

		point_numbers = areas[20]
		self.assertEqual(point_numbers, (112, 113, 114, 115))

	def test_point_loads(self):
		pass

	def test_grid_lines(self):
		pass

	def test_load_cases(self):
		pass

	def test_load_combinations(self):
		pass

	def test_punching_shear(self):
		pass

	def test_slab_prop(self):
		pass

	def soil_prop(self):
		pass

	