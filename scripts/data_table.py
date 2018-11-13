# -*- coding: utf-8 -*-
"""
Program:
    Data Table
    (LibreEngineering)
    data_table.py

Author:
    Alex Borisov <>

Copyright (c) 2010-2012 Alex Borisov

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

from PyQt5 import QtGui, QtCore, QtWidgets

class DataTable(QtCore.QObject):

    cb_index_changed_signal = QtCore.pyqtSignal(QtGui.QWidget)

    def __init__(self, parent = None):
        QtCore.QObject.__init__(self)

        self.dbl_validator = QtGui.QDoubleValidator(parent)
        self.dbl_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        self.signalMapper = QtCore.QSignalMapper()
        self.signalMapper.mapped[QtGui.QWidget].connect(self.on_signalMapper_mapped)

    def create_table(self, headers, col_widths, tb_width):
        table = QtGui.QTableWidget()

        table.setColumnCount(len(headers))
        table.setMinimumSize(tb_width, 100)
        table.setShowGrid(True)

        font = QtGui.QFont("Sans-serif", 8)
        table.horizontalHeader().setStyleSheet("font-family: Sans-serif; font-size: 7pt; font-weight: bold;")
        table.setFont(font)

        v_header = table.verticalHeader()
        v_header.setVisible(True)

        h_header = table.horizontalHeader()
        h_header.setStretchLastSection(True)
        table.setHorizontalHeaderLabels(headers)
        for col in range(table.columnCount()):
            table.setColumnWidth(col, col_widths[col])

        table.setSortingEnabled(True)

        return table

    def insert_row(self, table):
        rows = table.rowCount()
        table.insertRow(rows)
        self.set_row_items(table)
        self.resize_rows(table)
        return table

    def set_row_items(self, table):
        rows = table.rowCount()
        cols = table.columnCount()
        for col in range(cols):
            table.setItem(rows - 1, col, QtGui.QTableWidgetItem(''))
        return table

    def insert_row_cb(self, table, cb_col):
        rows = table.rowCount()
        table.insertRow(rows)
        self.set_row_items_cb(table, cb_col)
        self.resize_rows(table)
        return table

    def set_row_items_cb(self, table, cb_col):
        rows = table.rowCount()
        cols = table.columnCount()
        for col in range(cols):
            if col in cb_col:
                cb = QtGui.QComboBox()
                cb.currentIndexChanged.connect(self.signalMapper.map)
                table.setCellWidget(rows - 1, col, cb)
                cb.row = rows - 1
                cb.column = col
                self.signalMapper.setMapping(cb, cb)
            else:
                table.setItem(rows - 1, col, QtGui.QTableWidgetItem(''))
        return table

    def on_signalMapper_mapped(self, cb):
        self.cb_index_changed_signal.emit(cb)

    def add_cb_items(self, table, row, cb_col, items):
        cb = table.cellWidget(row, cb_col)
        cb.clear()
        cb.addItem("")
        cb.addItems(items)
        return table

    def resize_rows(self, table):
        rows = table.rowCount()
        for row in range(rows):
            table.setRowHeight(row, 18)
        return table

    def insert_item(self, table, cell, txt):
        if table.rowCount() == 0:
            self.insert_row(table)
        cell.setText(txt)
        return table

    def cell_validate(self, table, cell):
        if self.dbl_validator.validate(cell.text(), 0)[0] == QtGui.QValidator.Invalid:
            return False
        else:
            return True

    def clear_table(self, table):
        rows = table.rowCount()
        for row in range(rows):
            table.removeRow(rows-1-row)
        self.insert_row(table)
        return table
