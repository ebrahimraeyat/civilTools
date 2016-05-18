#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_civiltools
----------------------------------

Tests for `civiltools` module.
"""
#import sys
import unittest
from ..applications.section.sec import *


class TestSections(unittest.TestCase):

    def setUp(self):

        IPE = Ipe.createStandardIpes()
        self.IPE22 = IPE[22]
        self.IPE22.ductility = 'M'
        self.IPE22.useAs = 'Column'
        #IPE22_double = DoubleSection(IPE22, 8)
    #
        #plate1 = Plate(250, 10)
        #IPE22_double_TBPlate = AddPlateTB(IPE22_double, plate1)
    #
        #plate2 = Plate(10, 250)
        #IPE22_double_4sidePlate = AddPlateLR(IPE22_double_TBPlate, plate2)

    def test_IPE22_is_not_double(self):
        self.assertFalse(self.IPE22.isDouble)


    #IPE22.equivalentSectionI()

    #def tearDown(self):
        #pass

    #def test_000_something(self):
        #pass


if __name__ == '__main__':
    unittest.main()
