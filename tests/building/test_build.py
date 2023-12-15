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
    h1 = 26.28
    h2 = 3.55
    tx_an = 1.76
    ty_an = 1.99
    x = StructureSystem("سیستم قاب خمشی", "قاب خمشی بتن آرمه متوسط", 'X')
    x2 = StructureSystem("سیستم دیوارهای باربر", "دیوارهای برشی بتن آرمه ویژه", 'X')
    building = Building("زیاد", 1, 'II', "قم", 6, h1, None, x, x, tx_an, ty_an,
                                   x2, x2, h2, False, 2)
    tx = 0.9476
    tx2 = 0.1293
    ty = 0.9476
    ty2 = 0.1293
    assert building.tx_exp == pytest.approx(tx, abs=.001)
    assert building.ty_exp == pytest.approx(ty, abs=.001)
    assert building.tx_an == pytest.approx(tx_an, abs=.001)
    assert building.ty_an == pytest.approx(ty_an, abs=.001)
    assert building.tx_all == pytest.approx(building.tx_exp_all * 1.25, abs=.001)
    assert building.ty_all == pytest.approx(building.ty_exp_all * 1.25, abs=.001)
    assert building.building2.tx_an == pytest.approx(4, abs=.001)
    assert building.building2.ty_an == pytest.approx(4, abs=.001)
    assert building.building2.tx_exp == pytest.approx(tx2, abs=.001)
    assert building.building2.ty_exp == pytest.approx(ty2, abs=.001)
    assert building.tx_exp_all == pytest.approx((tx * h1 + tx2 * h2) / (h1 + h2), abs=.001)
    assert building.ty_exp_all == pytest.approx((ty * h1 + ty2 * h2) / (h1 + h2), abs=.001)
    assert building.bx == pytest.approx(1.20, abs=.001)
    assert building.by == pytest.approx(1.20, abs=.001)
    assert building.kx == pytest.approx(1.3423, abs=.001)
    assert building.ky == pytest.approx(1.3423, abs=.001)
    assert building.kx_drift == pytest.approx(1.630, abs=.001)
    assert building.ky_drift == pytest.approx(1.7450, abs=.001)
    assert building.results[1] == pytest.approx(0.0720, abs=.001)
    assert building.results[2]== pytest.approx(0.0720, abs=.001)
    assert building.results_drift[1] == pytest.approx(0.0534, abs=.001)
    assert building.results_drift[2]== pytest.approx(0.0489, abs=.001)
    tx *= 1.25
    tx2 *= 1.25
    ty *= 1.25
    ty2 *= 1.25
    assert building.tx == pytest.approx(tx, abs=.001)
    assert building.ty == pytest.approx(ty, abs=.001)
    assert building.building2.tx == pytest.approx(tx2, abs=.001)
    assert building.building2.ty == pytest.approx(ty2, abs=.001)
    assert building.bx_all == pytest.approx(1.30807, abs=.001)
    assert building.by_all == pytest.approx(1.30807, abs=.001)
    assert building.results_all_top[1] == pytest.approx(0.07848, abs=.001)
    assert building.results_all_top[2] == pytest.approx(0.07848, abs=.001)

def test_two_building_in_height_fahimi():
    x = StructureSystem("سیستم دیوارهای باربر", "دیوارهای برشی بتن آرمه ویژه", 'X')
    x2 = StructureSystem("سیستم قاب خمشی", "قاب خمشی بتن آرمه متوسط", 'X')
    h1 = 6.5
    h2 = 31.75
    tx = 0.2035
    tx2 = 1.1234
    ty = 0.2035
    ty2 = 1.1234
    building = Building("زیاد", 1, 'II', "قم", 2, h1, None, x, x, 4, 4,
                                   x2, x2, h2, False, 6)
    assert building.tx_exp == pytest.approx(tx, abs=.001)
    assert building.building2.tx_exp == pytest.approx(tx2, abs=.001)
    assert building.ty_exp == pytest.approx(ty, abs=.001)
    assert building.building2.ty_exp == pytest.approx(ty2, abs=.001)
    assert building.tx_exp_all == pytest.approx((tx * h1 + tx2 * h2) / (h1 + h2), abs=.001)
    assert building.ty_exp_all == pytest.approx((ty * h1 + ty2 * h2) / (h1 + h2), abs=.001)
    tx *= 1.25
    ty *= 1.25
    tx2 *= 1.25
    ty2 *= 1.25
    assert building.results_all_top[1] == pytest.approx(0.070837, abs=.001)
    assert building.results_all_top[2] == pytest.approx(0.070837, abs=.001)
    assert building.bx_all == pytest.approx(1.1806, abs=.001)
    assert building.by_all == pytest.approx(1.1806, abs=.001)

def test_building():
    x = StructureSystem("سیستم قاب خمشی", "قاب خمشی بتن آرمه متوسط", 'X')
    building = Building("زیاد", 1, 'II', "قم", 8, 26.28, None, x, x, 1.76, 1.99)
    assert building.tx_exp == pytest.approx(0.948, abs=.001)
    assert building.ty_exp == pytest.approx(0.948, abs=.001)
    assert building.tx == pytest.approx(1.185, abs=.001)
    assert building.ty == pytest.approx(1.185, abs=.001)

    assert building.kx == pytest.approx(1.342, abs=.001)
    assert building.ky == pytest.approx(1.342, abs=.001)
    assert building.bx == pytest.approx(1.2, abs=.01)
    assert building.results[0]
    assert building.results[1] == pytest.approx(0.072, abs=.001)
    assert building.results[2] == pytest.approx(0.072, abs=.001)

    # def test_Cx(self):
    #     self.assertAlmostEqual(self.myBuilding.results_drift[1], 0.1622, places=3)

    # def test_Kx(self):
    #     self.assertAlmostEqual(self.myBuilding.kx_drift, 1.00, places=2)

    # def test_Texp(self):
    #     self.assertAlmostEqual(self.myBuilding.tx_exp, .3223, places=2)

    # def test_T(self):
    #     self.assertAlmostEqual(self.myBuilding.tx_an, .40296, places=4)

    # def test_B(self):
    #     self.assertAlmostEqual(self.myBuilding.bx_drift, 2.483, places=2)

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
#         self.assertAlmostEqual(self.myBuilding.tx_exp, 0.28, places=2)

#     def test_B(self):
#         self.assertAlmostEqual(self.myBuilding.bx, 2.75, places=2)

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
#         self.assertAlmostEqual(self.myBuilding.bx, 2.75, places=2)

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
#         self.assertAlmostEqual(self.myBuilding.tx_an, 1.62, places=2)

#     def test_B(self):
#         self.assertAlmostEqual(self.myBuilding.bx_drift, 1.42, places=2)

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
