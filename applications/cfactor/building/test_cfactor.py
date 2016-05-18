#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_civiltools
----------------------------------

Tests for `civiltools` module.
"""
#import sys
import unittest
from build import *


class Test1(unittest.TestCase):

    def setUp(self):
        self.x = StructureSystem(u'سیستم دوگانه یا ترکیبی', u"قاب خمشی فولادی ویژه + مهاربندی واگرای ویژه فولادی", 'X')
        self.myBuilding = Building(u'خیلی زیاد', 1.4, 'I', 3, 12, None, self.x, self.x, u'کرج', 0.6, 0.6, True)

    def test_Cx(self):
        self.assertAlmostEqual(self.myBuilding.Cx, 0.113, places=3)

    def test_Kx(self):
        self.assertAlmostEqual(self.myBuilding.kx, 1.05, places=2)

    def test_Texp(self):
        self.assertAlmostEqual(self.myBuilding.xTexp, 0.5157, places=2)

    def test_T(self):
        self.assertEqual(self.myBuilding.xTan, 0.6)

    def test_B(self):
        self.assertAlmostEqual(self.myBuilding.Bx, 1.73, places=2)

    def test_R(self):
        self.assertEqual(self.myBuilding.xSystem.Ru, 7.5)

    def test_B1(self):
        self.assertAlmostEqual(self.myBuilding.xReflectionFactor.B1, 1.6666, places=2)

    def test_N(self):
        self.assertAlmostEqual(self.myBuilding.xReflectionFactor.N, 1.038888, places=3)


class Test2(unittest.TestCase):

    def setUp(self):
        self.x = StructureSystem(u'سیستم قاب ساختمانی', u'مهاربندی همگرای معمولی فولادی', 'X')
        self.myBuilding = Building(u'زیاد', 1, 'III', 3, 10, None, self.x, self.x, u'مشهد', 0.6, 0.6, False)

    def test_Cx(self):
        self.assertAlmostEqual(self.myBuilding.Cx, 0.2357, places=3)

    def test_Texp(self):
        self.assertAlmostEqual(self.myBuilding.xTexp, 0.28, places=2)

    def test_B(self):
        self.assertAlmostEqual(self.myBuilding.Bx, 2.75, places=2)

    def test_R(self):
        self.assertEqual(self.myBuilding.xSystem.Ru, 3.5)

    def test_B1(self):
        self.assertAlmostEqual(self.myBuilding.xReflectionFactor.B1, 2.75, places=2)

    def test_N(self):
        self.assertEqual(self.myBuilding.xReflectionFactor.N, 1)




class TestJohari(unittest.TestCase):

    def setUp(self):
        self.x = StructureSystem(u'سیستم قاب خمشی', u"قاب خمشی فولادی متوسط", 'X')
        self.myBuilding = Building(u'متوسط', 1, 'III', 5, 15.60, None, self.x, self.x, u'آبدانان', 0.6, 0.6, False)

    def test_C(self):
        self.assertAlmostEqual(self.myBuilding.Cx, 0.1375, places=3)

    def test_T(self):
        self.assertAlmostEqual(self.myBuilding.Tx, 0.627, places=2)

    def test_B(self):
        self.assertAlmostEqual(self.myBuilding.Bx, 2.75, places=2)

    def test_R(self):
        self.assertEqual(self.myBuilding.xSystem.Ru, 5)

    def test_B1(self):
        self.assertAlmostEqual(self.myBuilding.xReflectionFactor.B1, 2.75, places=2)

    def test_N(self):
        self.assertEqual(self.myBuilding.xReflectionFactor.N, 1)




if __name__ == '__main__':
    unittest.main()