from pathlib import Path
import sys

civiltools_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civiltools_path))

import pytest
from building.build import (
    StructureSystem,
    Building,
)


def test_two_building_in_height():
    x = StructureSystem("سیستم قاب خمشی", "قاب خمشی بتن آرمه متوسط", 'X')
    x2 = StructureSystem("سیستم دیوارهای باربر", "دیوارهای برشی بتن آرمه ویژه", 'X')
    my_building = Building("زیاد", 1, 'II', 8, 26.28, None, x, x, "قم", 1.76, 1.99,
                                   x2, x2, 3.55)
    assert my_building.exp_period_x == pytest.approx(0.948, abs=.001)
    assert my_building.exp_period_x2 == pytest.approx(0.129, abs=.001)
    assert my_building.exp_period_y == pytest.approx(0.948, abs=.001)
    assert my_building.exp_period_y2 == pytest.approx(0.129, abs=.001)
    assert my_building.tx == pytest.approx((1.185 * 26.28 + 0.162 * 3.55) / (26.28 + 3.55), abs=.001)
    assert my_building.ty == pytest.approx((1.185 * 26.28 + 0.162 * 3.55) / (26.28 + 3.55), abs=.001)
    assert my_building.Bx == pytest.approx(1.30807, abs=.001)
    assert my_building.By == pytest.approx(1.30807, abs=.001)
    assert my_building.results[1] == pytest.approx(0.07848, abs=.001)
    assert my_building.results[2] == pytest.approx(0.07848, abs=.001)

def test_two_building_in_height_fahimi():
    x = StructureSystem("سیستم دیوارهای باربر", "دیوارهای برشی بتن آرمه ویژه", 'X')
    x2 = StructureSystem("سیستم قاب خمشی", "قاب خمشی بتن آرمه متوسط", 'X')
    h1 = 6.5
    h2 = 31.75
    tx = 0.2035
    tx2 = 1.1234
    ty = 0.2035
    ty2 = 1.1234
    my_building = Building("زیاد", 1, 'II', 8, h1, None, x, x, "قم", 4, 4,
                                   x2, x2, h2)
    assert my_building.exp_period_x == pytest.approx(tx, abs=.001)
    assert my_building.exp_period_x2 == pytest.approx(tx2, abs=.001)
    assert my_building.exp_period_y == pytest.approx(ty, abs=.001)
    assert my_building.exp_period_y2 == pytest.approx(ty2, abs=.001)
    tx *= 1.25
    ty *= 1.25
    tx2 *= 1.25
    ty2 *= 1.25
    assert my_building.tx == pytest.approx((tx * h1 + tx2 * h2) / (h1 + h2), abs=.001)
    assert my_building.ty == pytest.approx((ty * h1 + ty2 * h2) / (h1 + h2), abs=.001)
    print(my_building.tx)
    assert my_building.results[1] == pytest.approx(0.070837, abs=.001)
    assert my_building.results[2] == pytest.approx(0.070837, abs=.001)
    assert my_building.Bx == pytest.approx(1.1806, abs=.001)
    assert my_building.By == pytest.approx(1.1806, abs=.001)

def test_building():
    x = StructureSystem("سیستم قاب خمشی", "قاب خمشی بتن آرمه متوسط", 'X')
    my_building = Building("زیاد", 1, 'II', 8, 26.28, None, x, x, "قم", 1.76, 1.99)
    assert my_building.exp_period_x == pytest.approx(0.948, abs=.001)
    assert my_building.exp_period_y == pytest.approx(0.948, abs=.001)
    assert my_building.tx == pytest.approx(1.185, abs=.001)
    assert my_building.ty == pytest.approx(1.185, abs=.001)

    assert my_building.kx == pytest.approx(1.342, abs=.001)
    assert my_building.ky == pytest.approx(1.342, abs=.001)
    assert my_building.Bx == pytest.approx(1.2, abs=.01)
    assert my_building.results[0]
    assert my_building.results[1] == pytest.approx(0.072, abs=.001)
    assert my_building.results[2] == pytest.approx(0.072, abs=.001)

    # def test_Cx(self):
    #     self.assertAlmostEqual(self.myBuilding.results_drift[1], 0.1622, places=3)

    # def test_Kx(self):
    #     self.assertAlmostEqual(self.myBuilding.kx_drift, 1.00, places=2)

    # def test_Texp(self):
    #     self.assertAlmostEqual(self.myBuilding.exp_period_x, .3223, places=2)

    # def test_T(self):
    #     self.assertAlmostEqual(self.myBuilding.x_period_an, .40296, places=4)

    # def test_B(self):
    #     self.assertAlmostEqual(self.myBuilding.Bx_drift, 2.483, places=2)

    # def test_R(self):
    #     self.assertEqual(self.myBuilding.x_system.Ru, 7.5)

    # def test_B1(self):
    #     self.assertAlmostEqual(self.myBuilding.soil_reflection_drift_prop_x.B1, 2.481, places=2)

    # def test_N(self):
    #     self.assertAlmostEqual(self.myBuilding.soil_reflection_drift_prop_x.N, 1.0005, places=3)

    # def test_c_factor_drift(self):
    #     self.assertAlmostEqual(self.myBuilding.results_drift[1], .1622, places=3)
    #     self.assertAlmostEqual(self.myBuilding.results_drift[2], .1622, places=3)

    # def test_k_x_for_drift(self):
    #     self.assertAlmostEqual(self.myBuilding.kx_drift, 1.00, places=2)


# class Test2(unittest.TestCase):

#     def setUp(self):
#         self.x = StructureSystem(u'سیستم قاب ساختمانی', u'مهاربندی همگرای معمولی فولادی', 'X')
#         self.myBuilding = Building(u'زیاد', 1, 'III', 3, 10, None, self.x, self.x, u'مشهد', 0.6, 0.6, False)

#     def test_Cx(self):
#         self.assertAlmostEqual(self.myBuilding.results[1], 0.2357, places=3)

#     def test_Texp(self):
#         self.assertAlmostEqual(self.myBuilding.exp_period_x, 0.28, places=2)

#     def test_B(self):
#         self.assertAlmostEqual(self.myBuilding.Bx, 2.75, places=2)

#     def test_R(self):
#         self.assertEqual(self.myBuilding.x_system.Ru, 3.5)

#     def test_B1(self):
#         self.assertAlmostEqual(self.myBuilding.soil_reflection_prop_x.B1, 2.75, places=2)

#     def test_N(self):
#         self.assertEqual(self.myBuilding.soil_reflection_prop_x.N, 1)


# class TestJohari(unittest.TestCase):

#     def setUp(self):
#         self.x = StructureSystem(u'سیستم قاب خمشی', u"قاب خمشی فولادی متوسط", 'X')
#         self.myBuilding = Building(u'متوسط', 1, 'III', 5, 15.60, None, self.x, self.x, u'آبدانان', 0.65, 0.65, False)

#     def test_C(self):
#         self.assertAlmostEqual(self.myBuilding.results[1], 0.1375, places=3)

#     def test_T(self):
#         self.assertAlmostEqual(self.myBuilding.Tx, 0.65, places=2)

#     def test_B(self):
#         self.assertAlmostEqual(self.myBuilding.Bx, 2.75, places=2)

#     def test_R(self):
#         self.assertEqual(self.myBuilding.x_system.Ru, 5)

#     def test_B1(self):
#         self.assertAlmostEqual(self.myBuilding.soil_reflection_prop_x.B1, 2.75, places=2)

#     def test_N(self):
#         self.assertEqual(self.myBuilding.soil_reflection_prop_x.N, 1)


# class TestDavoodabadi(unittest.TestCase):

#     def setUp(self):
#         self.x = StructureSystem(u'سیستم قاب خمشی', u"قاب خمشی بتن آرمه متوسط", 'X')
#         self.myBuilding = Building(u'زیاد', 1, 'III', 5, 16.80, None, self.x, self.x, u'قم', 1.62, 1.39, True)

#     def test_C(self):
#         self.assertAlmostEqual(self.myBuilding.results_drift[1], 0.0852, places=3)
#         self.assertAlmostEqual(self.myBuilding.results_drift[2], 0.0953, places=3)

#     def test_T(self):
#         self.assertAlmostEqual(self.myBuilding.x_period_an, 1.62, places=2)

#     def test_B(self):
#         self.assertAlmostEqual(self.myBuilding.Bx_drift, 1.42, places=2)

#     def test_R(self):
#         self.assertEqual(self.myBuilding.x_system.Ru, 5)

#     def test_B1(self):
#         self.assertAlmostEqual(self.myBuilding.soil_reflection_drift_prop_x.B1, 1.19, places=2)

#     def test_N(self):
#         self.assertAlmostEqual(self.myBuilding.soil_reflection_drift_prop_x.N, 1.195, places=2)

#     def test_c_factor_drift(self):
#         self.assertAlmostEqual(self.myBuilding.results_drift[1], .0852, places=3)
#         self.assertAlmostEqual(self.myBuilding.results_drift[2], .0953, places=3)



# if __name__ == '__main__':
#     unittest.main()
