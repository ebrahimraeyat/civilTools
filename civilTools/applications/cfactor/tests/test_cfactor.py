#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_civiltools
----------------------------------

Tests for `civiltools` module.
"""
#import sys
import unittest
from ..building.build import *


class Test1(unittest.TestCase):

    def setUp(self):
        self.x = StructureSystem(u'سیستم دوگانه یا ترکیبی', u"قاب خمشی فولادی ویژه + مهاربندی واگرای ویژه فولادی", 'X')
        self.myBuilding = Building(u'خیلی زیاد', 1.4, 'I', 3, 12, None, self.x, self.x, u'کرج', 0.6, 0.6, True)

    def test_Cx(self):
        self.assertAlmostEqual(self.myBuilding.results_drift[1], 0.113, places=3)

    def test_Kx(self):
        self.assertAlmostEqual(self.myBuilding.kx_drift, 1.05, places=2)

    def test_Texp(self):
        self.assertAlmostEqual(self.myBuilding.exp_period_x, 0.5157, places=2)

    def test_T(self):
        self.assertEqual(self.myBuilding.x_period_an, 0.6)

    def test_B(self):
        self.assertAlmostEqual(self.myBuilding.Bx_drift, 1.73, places=2)

    def test_R(self):
        self.assertEqual(self.myBuilding.x_system.Ru, 7.5)

    def test_B1(self):
        self.assertAlmostEqual(self.myBuilding.soil_reflection_drift_prop_x.B1, 1.6666, places=2)

    def test_N(self):
        self.assertAlmostEqual(self.myBuilding.soil_reflection_drift_prop_x.N, 1.038888, places=3)

    def test_c_factor_drift(self):
        self.assertAlmostEqual(self.myBuilding.results_drift[1], .113, places=3)
        self.assertAlmostEqual(self.myBuilding.results_drift[2], .113, places=3)

    def test_k_x_for_drift(self):
        self.assertAlmostEqual(self.myBuilding.kx_drift, 1.05, places=2)


class Test2(unittest.TestCase):

    def setUp(self):
        self.x = StructureSystem(u'سیستم قاب ساختمانی', u'مهاربندی همگرای معمولی فولادی', 'X')
        self.myBuilding = Building(u'زیاد', 1, 'III', 3, 10, None, self.x, self.x, u'مشهد', 0.6, 0.6, False)

    def test_Cx(self):
        self.assertAlmostEqual(self.myBuilding.results[1], 0.2357, places=3)

    def test_Texp(self):
        self.assertAlmostEqual(self.myBuilding.exp_period_x, 0.28, places=2)

    def test_B(self):
        self.assertAlmostEqual(self.myBuilding.Bx, 2.75, places=2)

    def test_R(self):
        self.assertEqual(self.myBuilding.x_system.Ru, 3.5)

    def test_B1(self):
        self.assertAlmostEqual(self.myBuilding.soil_reflection_prop_x.B1, 2.75, places=2)

    def test_N(self):
        self.assertEqual(self.myBuilding.soil_reflection_prop_x.N, 1)


class TestJohari(unittest.TestCase):

    def setUp(self):
        self.x = StructureSystem(u'سیستم قاب خمشی', u"قاب خمشی فولادی متوسط", 'X')
        self.myBuilding = Building(u'متوسط', 1, 'III', 5, 15.60, None, self.x, self.x, u'آبدانان', 0.65, 0.65, False)

    def test_C(self):
        self.assertAlmostEqual(self.myBuilding.results[1], 0.1375, places=3)

    def test_T(self):
        self.assertAlmostEqual(self.myBuilding.Tx, 0.65, places=2)

    def test_B(self):
        self.assertAlmostEqual(self.myBuilding.Bx, 2.75, places=2)

    def test_R(self):
        self.assertEqual(self.myBuilding.x_system.Ru, 5)

    def test_B1(self):
        self.assertAlmostEqual(self.myBuilding.soil_reflection_prop_x.B1, 2.75, places=2)

    def test_N(self):
        self.assertEqual(self.myBuilding.soil_reflection_prop_x.N, 1)


class TestDavoodabadi(unittest.TestCase):

    def setUp(self):
        self.x = StructureSystem(u'سیستم قاب خمشی', u"قاب خمشی بتن آرمه متوسط", 'X')
        self.myBuilding = Building(u'زیاد', 1, 'III', 5, 16.80, None, self.x, self.x, u'قم', 1.62, 1.39, True)

    def test_C(self):
        self.assertAlmostEqual(self.myBuilding.results_drift[1], 0.0852, places=3)
        self.assertAlmostEqual(self.myBuilding.results_drift[2], 0.0953, places=3)

    def test_T(self):
        self.assertAlmostEqual(self.myBuilding.x_period_an, 1.62, places=2)

    def test_B(self):
        self.assertAlmostEqual(self.myBuilding.Bx_drift, 1.42, places=2)

    def test_R(self):
        self.assertEqual(self.myBuilding.x_system.Ru, 5)

    def test_B1(self):
        self.assertAlmostEqual(self.myBuilding.soil_reflection_drift_prop_x.B1, 1.19, places=2)

    def test_N(self):
        self.assertAlmostEqual(self.myBuilding.soil_reflection_drift_prop_x.N, 1.195, places=2)

    def test_c_factor_drift(self):
        self.assertAlmostEqual(self.myBuilding.results_drift[1], .0852, places=3)
        self.assertAlmostEqual(self.myBuilding.results_drift[2], .0953, places=3)



if __name__ == '__main__':
    unittest.main()