# -*- coding: utf-8 -*-
"""
Program:
    Converter
    (LibreEngineering)
    customfactors.py

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

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .unicodesymbols import UnicodeSymbols
from scripts.data_table import DataTable
import scripts.file_utils as file_utils
from .convertercalc import ConverterCalc
import sys
import resources

class CustomFactors(QDialog):
    def __init__(self, converter_db = None, parent = None):
        super(CustomFactors, self).__init__(parent)

        self.converter_db = converter_db
        self.convertercalc = ConverterCalc(self.converter_db, self)

        self.custom_ui()

    def custom_ui(self):
        self.win_title = "LibreEngineering Converter"

        self.win_size = QSize(300, 100)
        self.icon_size = QSize(15, 15)
        self.lb_size = QSize(80, 20)
        self.btn_size = QSize(20, 20)
        self.cb_size = QSize(240, 20)
        self.radio_size = QSize(80, 20)
        self.chk_size = QSize(120, 20)
        self.img_size = QSize(200, 50)

        self.icon_win = QIcon(":/converter_resources/icons/converter/converter.png")
        self.icon_omega = QIcon(":/converter_resources/icons/converter/omega.png")
        self.icon_cancel = QIcon(":/main_resources/icons/main/cancel.png")
        self.icon_save = QIcon(":/main_resources/icons/main/save.png")
        self.icon_add = QIcon(":/main_resources/icons/main/add.png")
        self.icon_remove = QIcon(":/main_resources/icons/main/remove.png")

        self.setWindowIcon(self.icon_win)
        self.resize(self.win_size)
        self.setWindowTitle("Custom Units - " + self.win_title)

        self.dbl_validator = QDoubleValidator(self)
        self.dbl_validator.setNotation(QDoubleValidator.StandardNotation)

        h_spacer = QSpacerItem(2, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        v_spacer = QSpacerItem(20, 2, QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)

        self.img = QWidget(self)

        #
        # Widgets - GroupBoxes
        #

        self.gb_property = QGroupBox("", self)
        self.gb_units = QGroupBox("", self)
        self.gb_table = QGroupBox("", self)

        #
        # Widgets - Labels
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.lb_property = QLabel("Property", self.gb_property)
        size_policy.setHeightForWidth(self.lb_property.sizePolicy().hasHeightForWidth())
        self.lb_property.setSizePolicy(size_policy)
        self.lb_property.setMinimumSize(self.lb_size)

        self.lb_from = QLabel("From", self.gb_units)
        size_policy.setHeightForWidth(self.lb_from.sizePolicy().hasHeightForWidth())
        self.lb_from.setSizePolicy(size_policy)
        self.lb_from.setMinimumSize(self.lb_size)
        self.lb_to = QLabel("To", self.gb_units)
        size_policy.setHeightForWidth(self.lb_to.sizePolicy().hasHeightForWidth())
        self.lb_to.setSizePolicy(size_policy)
        self.lb_to.setMinimumSize(self.lb_size)

        self.lb_new_val = QLabel("New / Edit Values",  self.gb_table)
        size_policy.setHeightForWidth(self.lb_new_val.sizePolicy().hasHeightForWidth())
        self.lb_new_val.setAlignment(Qt.AlignHCenter)
        self.lb_new_val.setSizePolicy(size_policy)
        self.lb_new_val.setMinimumSize(self.lb_size)

        self.lb_status = QLabel("", self)
        self.lb_exp = QLabel("", self)
        self.lb_exp.setAlignment(Qt.AlignHCenter)
        self.lb_exp.setStyleSheet("color: blue; font-weight: bold;")

        self.lb_img = QLabel(self.img)
        self.lb_img.setStyleSheet("image: url(:/converter_resources/icons/converter/converter.png);")
        self.lb_img.setMinimumSize(self.img_size)

        self.lb_img_txt = QLabel("Add / Delete / Edit Properties and Units Data", self.img)
        size_policy.setHeightForWidth(self.lb_img_txt.sizePolicy().hasHeightForWidth())
        self.lb_img_txt.setSizePolicy(size_policy)
        self.lb_img_txt.setAlignment(Qt.AlignHCenter)
        self.lb_img_txt.setStyleSheet("font-style:italic; font-size: 7pt;")
        self.lb_img_txt.setWordWrap(True)

        #
        # Widgets - ComboBoxes
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.cb_property = QComboBox(self.gb_property)
        size_policy.setHeightForWidth(self.cb_property.sizePolicy().hasHeightForWidth())
        self.cb_property.setSizePolicy(size_policy)
        self.cb_property.setMinimumSize(self.cb_size)
        self.cb_property.addItem("")

        self.cb_from = QComboBox(self.gb_units)
        size_policy.setHeightForWidth(self.cb_from.sizePolicy().hasHeightForWidth())
        self.cb_from.setSizePolicy(size_policy)
        self.cb_from.setMinimumSize(self.cb_size)
        self.cb_to = QComboBox(self.gb_units)
        size_policy.setHeightForWidth(self.cb_to.sizePolicy().hasHeightForWidth())
        self.cb_to.setSizePolicy(size_policy)
        self.cb_to.setMinimumSize(self.cb_size)

        #
        # Widgets - RadioButtons
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.radio_exist_property = QRadioButton("Existing", self.gb_property)
        self.radio_exist_property.setSizePolicy(size_policy)
        self.radio_exist_property.setMinimumSize(self.radio_size)
        self.radio_exist_property.setChecked(True)
        self.radio_new_property = QRadioButton("New", self.gb_property)
        self.radio_new_property.setSizePolicy(size_policy)
        self.radio_new_property.setMinimumSize(self.radio_size)

        self.radio_exist_units = QRadioButton("Existing", self.gb_units)
        self.radio_exist_units.setSizePolicy(size_policy)
        self.radio_exist_units.setMinimumSize(self.radio_size)
        self.radio_exist_units.setChecked(True)
        self.radio_new_units = QRadioButton("New", self.gb_units)
        self.radio_new_units.setSizePolicy(size_policy)
        self.radio_new_units.setMinimumSize(self.radio_size)

        #
        # Widgets - CheckBoxes
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.chk_del_property = QCheckBox("Delete Property", self.gb_property)
        self.chk_del_property.setSizePolicy(size_policy)
        self.chk_del_property.setMinimumSize(self.chk_size)

        self.chk_del_from_unit = QCheckBox("Delete Unit", self.gb_units)
        self.chk_del_from_unit.setSizePolicy(size_policy)
        self.chk_del_from_unit.setMinimumSize(self.chk_size)
        self.chk_del_to_unit = QCheckBox("Delete Unit", self.gb_units)
        self.chk_del_to_unit.setSizePolicy(size_policy)
        self.chk_del_to_unit.setMinimumSize(self.chk_size)

        #
        # Widgets - PushButtons
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.btn_save = QPushButton(self.icon_save, "Save", self)
        size_policy.setHeightForWidth(self.btn_save.sizePolicy().hasHeightForWidth())
        self.btn_save.setSizePolicy(size_policy)
        self.btn_save.setMinimumSize(self.btn_size)
        self.btn_cancel = QPushButton(self.icon_cancel, "Cancel", self)
        size_policy.setHeightForWidth(self.btn_cancel.sizePolicy().hasHeightForWidth())
        self.btn_cancel.setSizePolicy(size_policy)
        self.btn_cancel.setMinimumSize(self.btn_size)

        self.btn_add = QPushButton(self.icon_add, "", self.gb_table)
        self.btn_add.setIconSize(self.icon_size)
        size_policy.setHeightForWidth(self.btn_add.sizePolicy().hasHeightForWidth())
        self.btn_add.setSizePolicy(size_policy)
        self.btn_add.setMinimumSize(self.btn_size)
        self.btn_remove = QPushButton(self.icon_remove, "", self.gb_table)
        self.btn_remove.setIconSize(self.icon_size)
        size_policy.setHeightForWidth(self.btn_remove.sizePolicy().hasHeightForWidth())
        self.btn_remove.setSizePolicy(size_policy)
        self.btn_remove.setMinimumSize(self.btn_size)

        self.btn_add.setEnabled(False)
        self.btn_remove.setEnabled(False)

        #
        # Widgets - Table
        #

        self.data_table = DataTable(self)
        table_headers = ['Property', 'From Unit', 'Units', 'To Factor', 'To Power', 'To Unit', 'Units', '']
        col_widths = [150, 150, 100, 100, 60, 150, 100, 10]
        tb_size = 0
        for w in col_widths:
            tb_size += w
        self.table = self.data_table.create_table(table_headers, col_widths, tb_size)
        self.table = self.data_table.insert_row(self.table)

        #
        # Layouts
        #

        property_layout = QGridLayout(self.gb_property)
        property_layout.sizeConstraint = QLayout.SetDefaultConstraint
        property_layout.addWidget(self.lb_property, 0, 0)
        property_layout.addWidget(self.cb_property, 0, 1)
        property_layout.addWidget(self.radio_exist_property, 0, 2)
        property_layout.addWidget(self.radio_new_property, 0, 3)
        property_layout.addWidget(self.chk_del_property, 0, 4)
        property_layout.addItem(h_spacer, 0, 5, 1, 1)
        property_layout.addItem(v_spacer, 1, 0)

        units_layout = QGridLayout(self.gb_units)
        units_layout.sizeConstraint = QLayout.SetDefaultConstraint
        units_layout.addWidget(self.lb_from, 0, 0)
        units_layout.addWidget(self.cb_from, 0, 1)
        units_layout.addWidget(self.chk_del_from_unit, 0, 4)
        units_layout.addWidget(self.lb_to, 1, 0)
        units_layout.addWidget(self.cb_to, 1, 1)
        units_layout.addWidget(self.radio_exist_units, 1, 2)
        units_layout.addWidget(self.radio_new_units, 1, 3)
        units_layout.addWidget(self.chk_del_to_unit, 1, 4)
        units_layout.addItem(h_spacer, 0, 5, 2, 1)
        units_layout.addItem(v_spacer, 2, 0)

        tb_button_layout = QHBoxLayout()
        tb_button_layout.sizeConstraint = QLayout.SetDefaultConstraint
        tb_button_layout.addWidget(self.btn_add)
        tb_button_layout.addWidget(self.btn_remove)
        tb_button_layout.addItem(h_spacer)

        hb_button_layout = QHBoxLayout()
        hb_button_layout.sizeConstraint = QLayout.SetDefaultConstraint
        hb_button_layout.addWidget(self.lb_exp)
        hb_button_layout.addItem(h_spacer)
        hb_button_layout.addWidget(self.lb_status)
        hb_button_layout.addItem(h_spacer)
        hb_button_layout.addWidget(self.btn_save)
        hb_button_layout.addWidget(self.btn_cancel)

        table_layout = QVBoxLayout(self.gb_table)
        table_layout.sizeConstraint = QLayout.SetDefaultConstraint
        table_layout.addWidget(self.lb_new_val)
        table_layout.addWidget(self.table)
        table_layout.addLayout(tb_button_layout)
        table_layout.addItem(v_spacer)

        img_layout = QVBoxLayout(self.img)
        img_layout.sizeConstraint = QLayout.SetDefaultConstraint
        img_layout.addWidget(self.lb_img)
        img_layout.addWidget(self.lb_img_txt)

        main_layout = QGridLayout(self)
        main_layout.sizeConstraint = QLayout.SetDefaultConstraint
        main_layout.addWidget(self.gb_property, 0, 0)
        main_layout.addWidget(self.gb_units, 1, 0)
        main_layout.addWidget(self.img, 0, 1, 2, 1)
        main_layout.addWidget(self.gb_table, 2, 0, 1, 2)
        main_layout.addLayout(hb_button_layout, 3, 0, 1, 2)
        main_layout.addItem(h_spacer, 0, 2, 4, 1)
        main_layout.addItem(v_spacer, 4, 0)

        self.timer = QTimer(self)
        self.timer.setInterval(5000)

        #
        # SIGNALs and SLOTs
        #

        self.connect(self.timer, SIGNAL("timeout()") , self.timer_hit)
        self.connect(self.cb_property, SIGNAL("currentIndexChanged(int)"), self.property_current_index_changed)
        self.connect(self.cb_from, SIGNAL("currentIndexChanged(int)"), self.from_current_index_changed)
        self.connect(self.cb_to, SIGNAL("currentIndexChanged(int)"), self.to_current_index_changed)
        self.connect(self.radio_exist_property, SIGNAL("toggled(bool)"), self.exist_property_toggled)
        self.connect(self.radio_new_property, SIGNAL("toggled(bool)"), self.new_property_toggled)
        self.connect(self.radio_exist_units, SIGNAL("toggled(bool)"), self.exist_units_toggled)
        self.connect(self.radio_new_units, SIGNAL("toggled(bool)"), self.new_units_toggled)
        self.connect(self.btn_save, SIGNAL("clicked()"), self.btn_save_clicked)
        self.connect(self.btn_cancel, SIGNAL("clicked()"), self.close)
        self.connect(self.btn_add, SIGNAL("clicked()"), self.btn_add_clicked)
        self.connect(self.btn_remove, SIGNAL("clicked()"), self.btn_remove_clicked)
        self.connect(self.table, SIGNAL("cellChanged(int, int)") , self.table_cell_changed)
        self.connect(self.table, SIGNAL("cellClicked(int, int)") , self.table_cell_clicked)

        self.cb_property.addItems(self.converter_db.get_properties())

    def property_current_index_changed(self):
        self.cb_from.clear()
        self.cb_to.clear()
        prop = self.cb_property.currentText()
        if prop == "Temperature":
            self.clear_inputs()
            str_status = "Temperature - can't edit non linear conversion"
            self.show_status(str_status, "red")
        else:
            if prop !="":
                units = self.converter_db.get_units(prop)
                if not self.radio_new_units.isChecked():
                    self.cb_from.addItems(units)
                self.cb_to.addItems(units)
                self.data_table.insert_item(self.table, self.table.item(0, 0), prop)
            else:
                self.data_table.insert_item(self.table, self.table.item(0, 0), "")
                self.data_table.insert_item(self.table, self.table.item(0, 1), "")
                self.data_table.insert_item(self.table, self.table.item(0, 2), "")
                self.data_table.insert_item(self.table, self.table.item(0, 3), "")
                self.data_table.insert_item(self.table, self.table.item(0, 4), "")
                self.data_table.insert_item(self.table, self.table.item(0, 5), "")
                self.data_table.insert_item(self.table, self.table.item(0, 6), "")

    def from_current_index_changed(self):
        prop = self.cb_property.currentText()
        from_unit = self.cb_from.currentText()
        if prop != "" and from_unit != "" and not self.radio_new_units.isChecked():
            from_ucode = self.converter_db.get_data(prop, from_unit, "ucode")
            self.data_table.insert_item(self.table, self.table.item(0, 1), from_unit)
            self.data_table.insert_item(self.table, self.table.item(0, 2), from_ucode)
        self.convert()

    def to_current_index_changed(self):
        prop = self.cb_property.currentText()
        to_unit = self.cb_to.currentText()
        if prop != "" and to_unit != "":
            to_ucode = self.converter_db.get_data(prop, to_unit, "ucode")
            self.data_table.insert_item(self.table, self.table.item(0, 5), to_unit)
            self.data_table.insert_item(self.table, self.table.item(0, 6), to_ucode)
        self.convert()

    def exist_property_toggled(self):
        self.lb_property.setText("Property")
        self.cb_property.setEnabled(True)
        self.chk_del_property.setEnabled(True)
        self.cb_property.setCurrentIndex(0)
        self.radio_exist_units.setEnabled(True)
        self.radio_exist_units.setChecked(True)
        self.chk_del_property.setChecked(False)
        self.cb_to.setEnabled(True)
        self.lb_to.setEnabled(True)
        self.clear_inputs()
        self.btn_add.setEnabled(False)
        self.btn_remove.setEnabled(False)

    def new_property_toggled(self):
        self.lb_property.setText("New Property")
        self.cb_property.setEnabled(False)
        self.chk_del_property.setEnabled(False)
        self.radio_exist_units.setEnabled(False)
        self.radio_new_units.setChecked(True)
        self.cb_to.setEnabled(False)
        self.lb_to.setEnabled(False)
        self.chk_del_property.setChecked(False)
        self.cb_property.setCurrentIndex(0)
        self.clear_inputs()
        self.btn_add.setEnabled(True)
        self.btn_remove.setEnabled(True)

    def exist_units_toggled(self):
        self.lb_from.setEnabled(True)
        self.cb_from.setEnabled(True)
        self.chk_del_from_unit.setEnabled(True)
        self.chk_del_to_unit.setEnabled(True)
        self.chk_del_from_unit.setChecked(False)
        self.chk_del_to_unit.setChecked(False)
        self.property_current_index_changed()

    def new_units_toggled(self):
        self.lb_from.setEnabled(False)
        self.cb_from.clear()
        self.cb_from.setEnabled(False)
        self.chk_del_from_unit.setEnabled(False)
        self.chk_del_to_unit.setEnabled(False)
        self.chk_del_from_unit.setChecked(False)
        self.chk_del_to_unit.setChecked(False)
        self.data_table.insert_item(self.table, self.table.item(0, 1), "")
        self.data_table.insert_item(self.table, self.table.item(0, 2), "")
        self.data_table.insert_item(self.table, self.table.item(0, 3), "")
        self.data_table.insert_item(self.table, self.table.item(0, 4), "")

    def convert(self):
        prop = self.cb_property.currentText()
        from_unit = self.cb_from.currentText()
        to_unit = self.cb_to.currentText()
        if prop != "" and from_unit != "" and to_unit != "":
            calc_result = self.convertercalc.convert(prop, from_unit, to_unit, 0)
            factor = calc_result[1]
            e = calc_result[2]

            self.data_table.insert_item(self.table, self.table.item(0, 3), str(factor))
            self.data_table.insert_item(self.table, self.table.item(0, 4), str(e))

    def table_cell_changed(self, row, col):
        cell_prop = self.table.item(row, 0)
        cell_from_ucode = self.table.item(row, 2)
        cell_factor = self.table.item(row, 3)
        cell_e = self.table.item(row, 4)
        cell_to_ucode = self.table.item(row, 6)

        prop = ""
        from_ucode = ""
        factor = ""
        e = ""
        to_ucode = ""

        if cell_prop and cell_prop.text() != "":
            prop = cell_prop.text()
        if cell_from_ucode and cell_from_ucode.text() != "":
            from_ucode = cell_from_ucode.text()
        if cell_factor and cell_factor.text() != "":
            factor = cell_factor.text()
        if cell_e and cell_e.text() != "":
            e = cell_e.text()
        if cell_to_ucode and cell_to_ucode.text() != "":
            to_ucode = cell_to_ucode.text()

        cell = self.table.item(row, col)
        if col in [3, 4] and not self.data_table.cell_validate(self.table, cell):
            cell.setText("")
            self.show_status("Only numeric values allowed", "red")

        exp = prop + ": 1 " + from_ucode + " = " + factor + "E" + e + " " + to_ucode
        self.show_exp(exp)

    def table_cell_clicked(self, row, col):
        self.table_cell_changed(row, col)
        cell = self.table.item(row, col)
        if col == 2:
            ucode = cell.text()
            self.unicode_symbols = UnicodeSymbols(cell, ucode, self)
            self.unicode_symbols.setModal(True)
            self.unicode_symbols.show()
            self.unicode_symbols.symbol_entered_signal.connect(self.set_from_ucode)
        if col == 6:
            ucode = cell.text()
            self.unicode_symbols = UnicodeSymbols(cell, ucode, self)
            self.unicode_symbols.setModal(True)
            self.unicode_symbols.show()
            self.unicode_symbols.symbol_entered_signal.connect(self.set_to_ucode)

    def btn_add_clicked(self):
        self.data_table.insert_row(self.table)

    def btn_remove_clicked(self):
        item = self.table.currentItem()
        if item and item.isSelected():
            self.table.removeRow(item.row())

    def btn_save_clicked(self):
        try:
            if self.save_changes_dlg():
                if not file_utils.make_data_backup(self.converter_db.db_file):
                    self.show_status("Could not back up data file", "red")

                cell_prop = self.table.item(0, 0)
                cell_from_unit = self.table.item(0, 1)
                cell_from_ucode = self.table.item(0, 2)
                cell_factor = self.table.item(0, 3)
                cell_e = self.table.item(0, 4)
                cell_to_unit = self.table.item(0, 5)
                cell_to_ucode = self.table.item(0, 6)

                prop = self.cb_property.currentText()
                from_unit = self.cb_from.currentText()
                to_unit = self.cb_to.currentText()

                new_prop = ""
                new_from_unit = ""
                new_from_ucode = ""
                new_factor = ""
                new_e = ""
                new_to_unit = ""
                new_to_ucode = ""

                if cell_prop and cell_prop.text() != "":
                    new_prop = cell_prop.text()
                if cell_from_unit and cell_from_unit.text() != "":
                    new_from_unit = cell_from_unit.text()
                if cell_from_ucode and cell_from_ucode.text() != "":
                    new_from_ucode = cell_from_ucode.text()
                if cell_factor and cell_factor.text() != "":
                    new_factor = cell_factor.text()
                if cell_e and cell_e.text() != "":
                    new_e = cell_e.text()
                if cell_to_unit and cell_to_unit.text() != "":
                    new_to_unit = cell_to_unit.text()
                if cell_to_ucode and cell_to_ucode.text() != "":
                    new_to_ucode = cell_to_ucode.text()

                if self.chk_del_property.isChecked() and prop != "":
                    if self.converter_db.delete_property(prop):
                        self.close()
                    else:
                        self.show_status("Could not delete property", "red")
                elif self.chk_del_from_unit.isChecked() and from_unit != "" and self.chk_del_to_unit.isChecked() and to_unit != "":
                    if self.converter_db.delete_unit(prop, from_unit) and self.converter_db.delete_unit(prop, to_unit):
                        self.close()
                    else:
                        self.show_status("Could not delete units", "red")
                elif self.chk_del_from_unit.isChecked() and from_unit != "":
                    if self.converter_db.delete_unit(prop, from_unit):
                        self.close()
                    else:
                        self.show_status("Could not delete units", "red")
                elif self.chk_del_to_unit.isChecked() and to_unit != "":
                    if self.converter_db.delete_unit(prop, to_unit):
                        self.close()
                    else:
                        self.show_status("Could not delete unit", "red")
                elif new_prop != "" and\
                        new_from_unit != "" and\
                        new_to_unit != "" and\
                        new_from_ucode != "" and\
                        new_to_ucode != "" and\
                        new_factor != "" and\
                        new_e != "":
                    if self.converter_db.save_data(prop, from_unit, to_unit, self.table):
                        self.close()
                    else:
                        self.show_status("Could not save changes", "red")
                else:
                    self.show_status("Could not save changes, some fields are empty", "red")
        except Exception:
            exc = sys.exc_info()[1]
            QMessageBox.warning(self, "Error - " + self.win_title, "Unexpected error:\n %s" % (exc))

    def set_from_ucode(self, cell, txt):
        self.data_table.insert_item(self.table, cell, txt)

    def set_to_ucode(self, cell, txt):
        self.data_table.insert_item(self.table, cell, txt)

    def save_changes_dlg(self):
        msg = "WARNING!\n"
        msg += "You are about to make changes to converter data file.\n"
        msg += "A backup copy of the data file will be created.\n"
        msg += "Be aware that changing descriptions of existing properties and units\n"
        msg += "will stop other programs working which use the current descriptions.\n"
        msg += "Press OK to save changes or Cancel to return."
        dlg = QMessageBox(self)
        dlg.setIcon(QMessageBox.Warning)
        dlg.setWindowTitle("Save Changes - " + self.win_title)
        dlg.setText(msg)
        dlg.addButton(QMessageBox.Ok)
        dlg.addButton(QMessageBox.Cancel)
        dlg.setDefaultButton(QMessageBox.Cancel)
        button = dlg.exec_()
        if (button == QMessageBox.Ok):
            return True
        else:
            return False

    def clear_inputs(self):
        self.data_table.clear_table(self.table)

    def closeEvent(self, event):
        self.emit(SIGNAL("closed()"))

    def start_timer(self):
        self.timer.start()

    def timer_hit(self):
        self.lb_status.setText("")

    def show_status(self, msg,  color):
        self.lb_status.setStyleSheet("color: " + color + ";")
        self.lb_status.setText(msg)
        self.start_timer()

    def show_exp(self, exp):
        self.lb_exp.setText(exp)
