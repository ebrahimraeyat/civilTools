# -*- coding: utf-8 -*-
"""
Program:
    Converter
    (LibreEngineering)
    convertercalc.py

Author:
    Alex Borisov <>

Copyright (c) 2010-2013 Alex Borisov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import math
from decimal import Decimal

class ConverterCalc(object):
    def __init__(self, converter_db = None, parent = None):
        self.converter_db = converter_db

    def convert(self, prop, from_unit, to_unit, from_val):
        str_from_factor = self.converter_db.get_data(prop, from_unit, "factor")
        str_to_factor = self.converter_db.get_data(prop, to_unit, "factor")
        str_from_e = self.converter_db.get_data(prop, from_unit, "e")
        str_to_e = self.converter_db.get_data(prop, to_unit, "e")
        from_ucode = self.converter_db.get_data(prop, from_unit, "ucode")
        to_ucode = self.converter_db.get_data(prop, to_unit, "ucode")

        from_factor = Decimal(str_from_factor) * Decimal(pow(10, Decimal(str_from_e)))
        to_factor = Decimal(str_to_factor) * Decimal(pow(10, Decimal(str_to_e)))
        result = Decimal(from_val) * from_factor / to_factor
        factor = round(Decimal(str_from_factor) / Decimal(str_to_factor), 6)
        e = Decimal(str_from_e) - Decimal(str_to_e)

        calc_result = [result, factor, e, from_ucode, to_ucode]

        return calc_result

    def convert_temp(self, from_unit, to_unit, from_val):
        input = float(from_val)
        output = 0

        if from_unit == "kelvin":
            input *= 1
        elif from_unit == "degree Celsius":
            input += 273.15
        elif from_unit == "degree centigrade":
            input += 273.15
        elif from_unit == "degree Fahrenheit":
            input = (input + 459.67) / 1.8
        elif from_unit == "degree Rankine":
            input /= 1.8

        if to_unit == "kelvin":
            output = input
        elif to_unit == "degree Celsius":
            output = input - 273.15
        elif to_unit == "degree centigrade":
            output = input - 273.15
        elif to_unit == "degree Fahrenheit":
            output = (input  * 1.8) - 459.67
        elif to_unit == "degree Rankine":
            output = input * 1.8

        return str(output)
