# -*- coding: utf-8 -*-
"""
Program:
    Converter
    (LibreEngineering)
    converter_db.py

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

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select, and_
from decimal import Decimal
from scripts.sqlitefktg4sa.core import auto_assign

class ConverterDB(object):
    def __init__(self, parent = None):

        self.db = None
        self.db_connection = None

    def db_open(self, db_file):
        self.db = create_engine('sqlite:///' + db_file, convert_unicode = True)
        self.db_connection = self.db.connect()
        self.db_file = db_file

    def db_close(self):
        if self.db_connection:
            self.db_connection.close()

    def db_create(self):
        metadata = MetaData()

        tb_properties = Table('properties', metadata,
            Column('id', Integer, primary_key=True),
            Column('property', String)
            )
        tb_units = Table('units', metadata,
            Column('id', Integer, primary_key=True),
            Column('property_id', None, ForeignKey('properties.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('unit', String),
            Column('factor', String),
            Column('e', String),
            Column('ucode', String)
            )
        auto_assign(metadata, self.db)
        metadata.create_all(self.db)

    def get_property_id(self, prop):
        metadata = MetaData()
        metadata.bind = self.db

        tb_properties = Table('properties', metadata, autoload = True)

        properties_id = select([tb_properties.c.id], tb_properties.c.property == prop)
        row = self.db_connection.execute(properties_id)
        data = row.first()
        property_id_key = data[0]
        return property_id_key

    def get_properties(self):
        property_list = []

        metadata = MetaData()
        metadata.bind = self.db

        tb_properties = Table('properties', metadata, autoload = True)

        properties = select([tb_properties.c.property])
        for row in self.db_connection.execute(properties):
            property_list.append(row[0])
        return sorted(property_list)

    def get_units(self, prop):
        unit_list = []

        metadata = MetaData()
        metadata.bind = self.db

        tb_units = Table('units', metadata, autoload = True)

        property_id_key = self.get_property_id(prop)
        units = select([tb_units.c.unit], tb_units.c.property_id == property_id_key)
        for row in self.db_connection.execute(units):
            unit_list.append(row[0])
        return unit_list

    def get_data(self, prop, unit, tag):
        metadata = MetaData()
        metadata.bind = self.db

        tb_units = Table('units', metadata, autoload = True)

        property_id_key = self.get_property_id(prop)
        factors_data = select([tb_units.c.factor, tb_units.c.e, tb_units.c.ucode],
                             and_(tb_units.c.unit == unit,
                                 tb_units.c.property_id == property_id_key))
        row = self.db_connection.execute(factors_data)
        data = row.first()
        if tag == "factor":
            return data[0]
        elif tag == "e":
            return data[1]
        elif tag == "ucode":
            return data[2]
        else:
            return ""

    def delete_property(self, prop):
        metadata = MetaData()
        metadata.bind = self.db

        tb_properties = Table('properties', metadata, autoload = True)

        properties = tb_properties.delete().\
                        where(tb_properties.c.property == prop)
        if self.db_connection.execute(properties):
            return True
        else:
            return False

    def delete_unit(self, prop, unit):
        metadata = MetaData()
        metadata.bind = self.db

        tb_units = Table('units', metadata, autoload = True)

        property_id_key = self.get_property_id(prop)
        units = tb_units.delete().\
                        where(tb_units.c.unit == unit).\
                        where(tb_units.c.property_id == property_id_key)

        if self.db_connection.execute(units):
            return True
        else:
            return False

    def update_property(self, prop, new_prop):
        metadata = MetaData()
        metadata.bind = self.db

        tb_properties = Table('properties', metadata, autoload = True)

        properties = tb_properties.update().\
                    values(property = new_prop).\
                    where(tb_properties.c.property == prop)
        self.db_connection.execute(properties)

    def update_unit(self, prop, unit, new_unit_data):
        new_unit = new_unit_data[0]
        new_factor = new_unit_data[1]
        new_e = new_unit_data[2]
        new_ucode = new_unit_data[3]

        metadata = MetaData()
        metadata.bind = self.db

        tb_units = Table('units', metadata, autoload = True)

        property_id_key = self.get_property_id(prop)
        units = tb_units.update().\
                    values({tb_units.c.unit:new_unit,
                            tb_units.c.factor:new_factor,
                            tb_units.c.e:new_e,
                            tb_units.c.ucode:new_ucode}).\
                    where(tb_units.c.property_id == property_id_key).\
                    where(tb_units.c.unit == unit)
        self.db_connection.execute(units)

    def add_property(self, new_prop, new_unit_data):
        metadata = MetaData()
        metadata.bind = self.db

        tb_properties = Table('properties', metadata, autoload = True)
        tb_units = Table('units', metadata, autoload = True)

        properties = tb_properties.insert().values(property = new_prop)
        result = self.db_connection.execute(properties)
        property_id_key = result.inserted_primary_key[0]

        for data in new_unit_data:
            new_unit = data[0]
            new_factor = data[1]
            new_e = data[2]
            new_ucode = data[3]

            units = tb_units.insert().values(property_id = property_id_key, unit = new_unit, factor = new_factor, e = new_e, ucode = new_ucode)
            result = self.db_connection.execute(units)

    def add_unit(self, prop, new_unit_data):
        new_unit = new_unit_data[0]
        new_factor = new_unit_data[1]
        new_e = new_unit_data[2]
        new_ucode = new_unit_data[3]

        metadata = MetaData()
        metadata.bind = self.db

        tb_units = Table('units', metadata, autoload = True)

        property_id_key = self.get_property_id(prop)
        units = tb_units.insert().values(property_id = property_id_key, unit = new_unit, factor = new_factor, e = new_e, ucode = new_ucode)
        result = self.db_connection.execute(units)

    def save_data(self, prop, unit_from, unit_to, units_table):
        status = True
        rows = units_table.rowCount()
        for row in range(rows):
            new_prop = units_table.item(row, 0).text()
            new_unit_from = units_table.item(row, 1).text()
            new_ucode_from = units_table.item(row, 2).text()
            new_factor = units_table.item(row, 3).text()
            new_e = units_table.item(row, 4).text()
            new_unit_to = units_table.item(row, 5).text()
            new_ucode_to = units_table.item(row, 6).text()

            properties = self.get_properties()
            if prop in properties:
                units = self.get_units(prop)
                if unit_to in units:
                    factor_to = self.get_data(prop, unit_to, "factor")
                    e_to = self.get_data(prop, unit_to, "e")
                    new_unit_to_data = [new_unit_to, factor_to, e_to, new_ucode_to]
                    self.update_unit(prop, unit_to, new_unit_to_data)
                elif unit_to == "" and not new_unit_to in units:
                    status = False
                    break
                if unit_from in units:
                    factor_from = str(Decimal(factor_to) * Decimal(new_factor))
                    e_from = str(Decimal(e_to) + Decimal(new_e))
                    new_unit_from_data = [new_unit_from, factor_from, e_from, new_ucode_from]
                    self.update_unit(prop, unit_from, new_unit_from_data)
                    self.update_property(prop, new_prop)
                elif unit_from == "" and not new_unit_from in units:
                    factor_from = str(Decimal(factor_to) * Decimal(new_factor))
                    e_from = str(Decimal(e_to) + Decimal(new_e))
                    new_unit_from_data = [new_unit_from, factor_from, e_from, new_ucode_from]
                    self.add_unit(prop, new_unit_from_data)
            elif prop == "" and new_prop in properties:
                units = self.get_units(new_prop)
                if unit_to in units:
                    factor_to = self.get_data(new_prop, unit_to, "factor")
                    e_to = self.get_data(new_prop, unit_to, "e")
                    new_unit_to_data = [new_unit_to, factor_to, e_to, new_ucode_to]
                    self.update_unit(new_prop, unit_to, new_unit_to_data)
                elif unit_to == "" and not new_unit_to in units:
                    status = False
                    break
                if unit_from in units:
                    factor_from = str(Decimal(factor_to) * Decimal(new_factor))
                    e_from = str(Decimal(e_to) + Decimal(new_e))
                    new_unit_from_data = [new_unit_from, factor_from, e_from, new_ucode_from]
                    self.update_unit(new_prop, unit_from, new_unit_from_data)
                elif unit_from == "" and not new_unit_from in units:
                    factor_from = str(Decimal(factor_to) * Decimal(new_factor))
                    e_from = str(Decimal(e_to) + Decimal(new_e))
                    new_unit_from_data = [new_unit_from, factor_from, e_from, new_ucode_from]
                    self.add_unit(new_prop, new_unit_from_data)
            elif prop == "" and not new_prop in properties:
                factor_to = "1"
                e_to = "0"
                factor_from = str(Decimal(factor_to) * Decimal(new_factor))
                e_from = str(Decimal(e_to) + Decimal(new_e))
                new_unit_to_data = [new_unit_to, factor_to, e_to, new_ucode_to]
                new_unit_from_data = [new_unit_from, factor_from, e_from, new_ucode_from]
                new_unit_data = [new_unit_to_data, new_unit_from_data]
                self.add_property(new_prop, new_unit_data)
            else:
                status = False
                break
        return status
