# -*- coding: utf-8 -*-
"""
Program:
    Converter
    (LibreEngineering)
    mainwindow.py

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
from decimal import Decimal
from .customfactors import CustomFactors
from .converter_db import ConverterDB
from .convertercalc import ConverterCalc
import scripts.file_utils as file_utils
import versions
import sys
import resources

class Converter(QMainWindow):
    def __init__(self, parent = None):
        super(Converter, self).__init__(parent)

        self.version = versions.ver_converter

        self.db_file = ""
        self.script_path = sys.path[0]
        self.read_settings()

        self.converter_db = ConverterDB(self)

        self.main_ui()

    def read_settings(self):
        if sys.platform == "win32":
            settings = QSettings(self.script_path + "/data/converter/converter.ini", QSettings.IniFormat)
        else:
            settings = QSettings(QDir.homePath() + "/.LibreEngineering/converter.conf", QSettings.NativeFormat)
        settings.beginGroup("init_settings")
        self.db_file = settings.value("db_file", self.script_path + "/data/converter/converter.sqlite")
        settings.endGroup()

    def main_ui(self):
        self.win_title = "LibreEngineering Converter"

        self.win_size = QSize(300, 300)
        self.lb_size = QSize(60, 20)
        self.txt_size = QSize(160, 20)
        self.cb_size = QSize(240, 20)
        self.spin_size = QSize(50, 20)

        self.icon_win = QIcon(":/converter_resources/icons/converter/converter.png")
        self.icon_swap = QIcon(":/converter_resources/icons/converter/swap.png")
        self.icon_custom = QIcon(":/converter_resources/icons/converter/custom.png")
        self.icon_quit = QIcon(":/main_resources/icons/main/quit.png")
        self.icon_about = QIcon(":/main_resources/icons/main/about.png")
        self.icon_qt = QIcon(":/main_resources/icons/qt.png")

        self.setWindowIcon(self.icon_win)
        self.resize(self.win_size)
        self.setWindowTitle(self.win_title)

        self.dbl_validator = QDoubleValidator(self)
        self.dbl_validator.setNotation(QDoubleValidator.StandardNotation)

        h_spacer = QSpacerItem(2, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        v_spacer = QSpacerItem(20, 2, QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)

        self.main_widget = QWidget(self)

        #
        # Actions
        #

        self.action_swap = QAction(self.icon_swap, "&Swap Units", self)
        self.action_custom = QAction(self.icon_custom, "C&ustom Factors", self)
        self.action_quit = QAction(self.icon_quit, "&Quit", self)
        self.action_about = QAction(self.icon_about, "&About", self)

        #
        # MenuBar
        #

        self.menu_bar = QMenuBar(self)
        self.menu_bar.Enabled = True
        self.setMenuBar(self.menu_bar)

        self.menu_file = QMenu("&File", self.menu_bar);
        self.menu_tools = QMenu("&Tools", self.menu_bar);
        self.menu_help = QMenu("&Help", self.menu_bar);

        self.menu_bar.addMenu(self.menu_file)
        self.menu_bar.addMenu(self.menu_tools)
        self.menu_bar.addMenu(self.menu_help)

        self.menu_file.addAction(self.action_quit)
        self.menu_tools.addAction(self.action_swap)
        self.menu_tools.addAction(self.action_custom)
        self.menu_help.addAction(self.action_about)
        self.menu_help.addAction(QIcon(self.icon_qt), "About &Qt", qApp.aboutQt)

        #
        # ToolBar
        #

        self.tool_bar = QToolBar(self)
        self.tool_bar.addAction(self.action_swap)
        self.tool_bar.addAction(self.action_custom)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.action_about)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.action_quit)
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)

        #
        # StatusBar
        #

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        #
        # Widgets - GroupBoxes
        #

        self.gb_property = QGroupBox("Property", self.main_widget)
        self.gb_units = QGroupBox("Units", self.main_widget)
        self.gb_result = QGroupBox("Result", self.main_widget)

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
        self.lb_input = QLabel("Input", self.gb_result)
        size_policy.setHeightForWidth(self.lb_input.sizePolicy().hasHeightForWidth())
        self.lb_input.setSizePolicy(size_policy)
        self.lb_input.setMinimumSize(self.lb_size)
        self.lb_output = QLabel("Output", self.gb_result)
        size_policy.setHeightForWidth(self.lb_output.sizePolicy().hasHeightForWidth())
        self.lb_output.setSizePolicy(size_policy)
        self.lb_output.setMinimumSize(self.lb_size)
        self.lb_decimals = QLabel("Decimals", self.gb_result)
        size_policy.setHeightForWidth(self.lb_decimals.sizePolicy().hasHeightForWidth())
        self.lb_decimals.setSizePolicy(size_policy)
        self.lb_decimals.setMinimumSize(self.lb_size)
        self.lb_input_unit = QLabel("", self.gb_result)
        size_policy.setHeightForWidth(self.lb_input_unit.sizePolicy().hasHeightForWidth())
        self.lb_input_unit.setSizePolicy(size_policy)
        self.lb_input_unit.setMinimumSize(self.lb_size)
        self.lb_output_unit = QLabel("", self.gb_result)
        size_policy.setHeightForWidth(self.lb_output_unit.sizePolicy().hasHeightForWidth())
        self.lb_output_unit.setSizePolicy(size_policy)
        self.lb_output_unit.setMinimumSize(self.lb_size)

        #
        # Widgets - LineEdits
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.txt_input = QLineEdit("1", self.gb_result)
        size_policy.setHeightForWidth(self.txt_input.sizePolicy().hasHeightForWidth())
        self.txt_input.setSizePolicy(size_policy)
        self.txt_input.setMinimumSize(self.txt_size)
        self.txt_input.setMaxLength(21)
        self.txt_input.setValidator(self.dbl_validator)
        self.txt_input.selectAll()
        self.txt_input.setFocus()

        palette = QPalette()
        palette.setColor(QPalette.Base, QColor("#CDCDCD"))
        palette.setColor(QPalette.Text, QColor("#0000FF"))

        self.txt_output = QLineEdit("", self.gb_result)
        size_policy.setHeightForWidth(self.txt_output.sizePolicy().hasHeightForWidth())
        self.txt_output.setSizePolicy(size_policy)
        self.txt_output.setMinimumSize(self.txt_size)
        self.txt_output.setReadOnly(True)
        self.txt_output.setPalette(palette)

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
        self.cb_from = QComboBox(self.gb_units)
        size_policy.setHeightForWidth(self.cb_from.sizePolicy().hasHeightForWidth())
        self.cb_from.setSizePolicy(size_policy)
        self.cb_from.setMinimumSize(self.cb_size)
        self.cb_to = QComboBox(self.gb_units)
        size_policy.setHeightForWidth(self.cb_to.sizePolicy().hasHeightForWidth())
        self.cb_to.setSizePolicy(size_policy)
        self.cb_to.setMinimumSize(self.cb_size)

        #
        # Widgets - SpinBoxes
        #

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.spin_decimals = QSpinBox(self.gb_result)
        self.spin_decimals.setSizePolicy(size_policy)
        self.spin_decimals.setMinimumSize(self.spin_size)
        self.spin_decimals.setRange(0, 10)
        self.spin_decimals.setValue(2)

        #
        # Layouts
        #

        property_layout = QGridLayout(self.gb_property)
        property_layout.sizeConstraint = QLayout.SetDefaultConstraint
        property_layout.addWidget(self.lb_property, 0, 0)
        property_layout.addWidget(self.cb_property, 0, 1)
        property_layout.addItem(h_spacer, 0, 2)

        units_layout = QGridLayout(self.gb_units)
        units_layout.sizeConstraint = QLayout.SetDefaultConstraint
        units_layout.addWidget(self.lb_from, 0, 0)
        units_layout.addWidget(self.cb_from, 0, 1)
        units_layout.addItem(h_spacer, 0, 2)
        units_layout.addWidget(self.lb_to, 1, 0)
        units_layout.addWidget(self.cb_to, 1, 1)
        units_layout.addItem(h_spacer, 1, 2)

        result_layout = QGridLayout(self.gb_result)
        result_layout.sizeConstraint = QLayout.SetDefaultConstraint
        result_layout.addWidget(self.lb_input, 0, 0)
        result_layout.addWidget(self.txt_input, 0, 1)
        result_layout.addWidget(self.lb_input_unit, 0, 2)
        result_layout.addWidget(self.lb_output, 1, 0)
        result_layout.addWidget(self.txt_output, 1, 1)
        result_layout.addWidget(self.lb_output_unit, 1, 2)
        result_layout.addWidget(self.lb_decimals, 2, 0)
        result_layout.addWidget(self.spin_decimals, 2, 1)
        result_layout.addItem(h_spacer, 2, 2)

        main_layout = QGridLayout(self.main_widget)
        main_layout.sizeConstraint = QLayout.SetDefaultConstraint
        main_layout.addWidget(self.gb_property, 0, 0)
        main_layout.addWidget(self.gb_units, 1, 0)
        main_layout.addWidget(self.gb_result, 2, 0)
        main_layout.addItem(h_spacer, 0, 1, 3, 1)
        main_layout.addItem(v_spacer, 3, 0)

        self.main_widget.setLayout(main_layout)
        self.setCentralWidget(self.main_widget)

        #
        # SIGNALs & SLOTs
        #
        self.action_quit.triggered.connect(self.Quit)
    
        # self.connect(self.action_swap, SIGNAL("triggered()"), self.action_swap_triggered)
        # self.connect(self.action_about, SIGNAL("triggered()"), self.action_about_triggered)
        # self.connect(self.action_custom, SIGNAL("triggered()"), self.action_custom_triggered)
        # self.connect(self.cb_property, SIGNAL("currentIndexChanged(int)"), self.property_changed)
        # self.connect(self.cb_from, SIGNAL("currentIndexChanged(int)"), self.from_changed)
        # self.connect(self.cb_to, SIGNAL("currentIndexChanged(int)"), self.to_changed)
        # self.connect(self.txt_input, SIGNAL("textChanged(QString)"), self.input_changed)
        # self.connect(self.spin_decimals, SIGNAL("valueChanged(int)"), self.decimals_changed)

        if not file_utils.find_data_file(self.db_file):
            f = file_utils.select_data_file(self, "factors", self.win_title, self.script_path)
            if f:
                self.db_file = f
                self.converter_db.db_open(self.db_file)
            else:
                self.converter_db.db_open(self.db_file)
                self.converter_db.db_create()
        else:
            self.converter_db.db_open(self.db_file)

        self.get_properties()

    def get_properties(self):
        properties = self.converter_db.get_properties()
        self.cb_property.clear()
        self.cb_property.addItem("")
        self.cb_property.addItems(properties)

    def property_changed(self):
        self.cb_from.clear()
        self.cb_to.clear()
        prop = self.cb_property.currentText()
        if prop != "":
            units = self.converter_db.get_units(prop)
            self.cb_from.addItems(units)
            self.cb_to.addItems(units)

    def from_changed(self):
        prop = self.cb_property.currentText()
        from_unit = self.cb_from.currentText()
        if prop != "" and from_unit != "":
            self.lb_input_unit.setText(self.converter_db.get_data(prop, from_unit, "ucode"))
        self.convert()
        self.txt_input.selectAll()
        self.txt_input.setFocus()

    def to_changed(self):
        prop = self.cb_property.currentText()
        to_unit = self.cb_to.currentText()
        if prop != "" and to_unit != "":
            self.lb_output_unit.setText(self.converter_db.get_data(prop, to_unit, "ucode"))
        self.convert()
        self.txt_input.selectAll()
        self.txt_input.setFocus()

    def input_changed(self, text):
        self.convert()

    def decimals_changed(self):
        self.convert()
        decimals = self.spin_decimals.value()
        value = self.txt_output.text()
        if value:
            self.txt_output.setText(self.set_decimals(value, decimals))

    def convert(self):
        calc = ConverterCalc(self.converter_db, self)
        prop = self.cb_property.currentText()
        from_unit = self.cb_from.currentText()
        to_unit = self.cb_to.currentText()
        from_val = self.txt_input.text()
        decimals = self.spin_decimals.value()
        if prop != "" and from_unit != "" and to_unit != "" and from_val != "":
            if prop == "Temperature":
                result = calc.convert_temp(from_unit, to_unit, from_val)
                output = self.set_decimals(result, decimals)
                str_status = "Temperature"
            else:
                calc_result = calc.convert(prop, from_unit, to_unit, from_val)
                result = calc_result[0]
                factor = calc_result[1]
                e = calc_result[2]
                from_ucode = calc_result[3]
                to_ucode = calc_result[4]

                output = self.set_decimals(result, decimals)

                str_status = prop + ": 1 " + from_ucode + " = " + str(factor) + "E" + str(e) + " " + to_ucode

            self.txt_output.setText(output)
            self.show_status(str_status)

    def set_decimals(self, value, decimals):
        rnd_value = round(Decimal(str(value)), decimals)
        return str(rnd_value)

    def Quit(self):
        self.write_settings()
        self.converter_db.db_close()
        self.close()

    def write_settings(self):
        if sys.platform == "win32":
            settings = QSettings(self.script_path + "/data/converter/converter.ini", QSettings.IniFormat)
        else:
            settings = QSettings(QDir.homePath() + "/.LibreEngineering/converter.conf", QSettings.NativeFormat)
        settings.beginGroup("init_settings")
        settings.setValue("db_file", self.db_file)
        settings.endGroup()

    def action_about_triggered(self):
        msg = self.win_title + " - International System of Units Converter\n\n"
        msg += "Version " + versions.ver_converter + "\n\n"
        msg += versions.copyright + "\n\n"
        msg += "Distributed under " + versions.license
        QMessageBox.about(self, "About - " + self.win_title, msg)

    def action_swap_triggered(self):
        from_index = self.cb_from.currentIndex()
        to_index = self.cb_to.currentIndex()
        self.txt_input.setText(self.txt_output.text())
        self.cb_to.setCurrentIndex(from_index)
        self.cb_from.setCurrentIndex(to_index)

    def action_custom_triggered(self):
        data_dlg = CustomFactors(self.converter_db, self)
        data_dlg.setModal(True)
        data_dlg.show()
        self.connect(data_dlg, SIGNAL("closed()"), self.custom_dlg_closed)

    def custom_dlg_closed(self):
        self.reset_ui()
        self.get_properties()

    def reset_ui(self):
        self.cb_property.clear()
        self.cb_to.clear()
        self.cb_from.clear()
        self.lb_input_unit.clear()
        self.lb_output_unit.clear()
        self.txt_input.setText("1")
        self.txt_output.setText("")
        self.spin_decimals.setValue(2)

    def show_status(self, str_status):
        self.status_bar.setStyleSheet("color: blue")
        self.status_bar.showMessage(str_status)
