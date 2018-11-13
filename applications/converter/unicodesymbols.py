# -*- coding: utf-8 -*-
"""
Program:
    Converter
    (LibreEngineering)
    unicodesymbols.py

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
from .charactermap import CharacterWidget

class UnicodeSymbols(QDialog):

    symbol_entered_signal = pyqtSignal(QTableWidgetItem, str)

    def __init__(self, cell = None, txt = None, parent = None):
        super(UnicodeSymbols, self).__init__(parent)

        self.cell = cell
        self.txt = txt

        self.unicode_symbols_ui()

    def unicode_symbols_ui(self):
        self.win_title = "LibreEngineering Converter"

        self.win_size = QSize(560, 450)
        self.txt_size = QSize(200, 25)
        self.btn_size = QSize(100, 25)

        self.icon_win = QIcon(":/converter_resources/icons/converter/converter.png")
        self.icon_clear = QIcon(":/main_resources/icons/main/clear.png")
        self.icon_save = QIcon(":/main_resources/icons/main/save.png")
        self.icon_cancel = QIcon(":/main_resources/icons/main/cancel.png")

        self.setWindowIcon(self.icon_win)
        self.setFixedSize(self.win_size)
        self.setWindowTitle("Unicode Symbols - " + self.win_title)

        h_spacer = QSpacerItem(2, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        v_spacer = QSpacerItem(20, 2, QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)

        #
        # Widgets - LineEdits
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.txt_unicode = QLineEdit("", self)
        self.txt_unicode.setReadOnly(True)
        size_policy.setHeightForWidth(self.txt_unicode.sizePolicy().hasHeightForWidth())
        self.txt_unicode.setSizePolicy(size_policy)
        self.txt_unicode.setMinimumSize(self.txt_size)
        self.txt_unicode.setText(self.txt)

        #
        # Widgets - PushButtons
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.btn_clear = QPushButton(self.icon_clear, "Clear", self)
        size_policy.setHeightForWidth(self.btn_clear.sizePolicy().hasHeightForWidth())
        self.btn_clear.setSizePolicy(size_policy)
        self.btn_clear.setMinimumSize(self.btn_size)
        self.btn_ok = QPushButton(self.icon_save, "OK", self)
        size_policy.setHeightForWidth(self.btn_ok.sizePolicy().hasHeightForWidth())
        self.btn_ok.setSizePolicy(size_policy)
        self.btn_ok.setMinimumSize(self.btn_size)
        self.btn_ok.setDefault(True)
        self.btn_cancel = QPushButton(self.icon_cancel, "Cancel", self)
        size_policy.setHeightForWidth(self.btn_cancel.sizePolicy().hasHeightForWidth())
        self.btn_cancel.setSizePolicy(size_policy)
        self.btn_cancel.setMinimumSize(self.btn_size)

        #
        # Widgets - ScrollAreas
        #

        self.scroll_area = QScrollArea()
        self.character_widget = CharacterWidget()
        self.scroll_area.setWidget(self.character_widget)

        #
        # Layouts
        #

        buttons_layout = QHBoxLayout()
        buttons_layout.sizeConstraint = QLayout.SetDefaultConstraint
        buttons_layout.addItem(h_spacer)
        buttons_layout.addWidget(self.btn_clear)
        buttons_layout.addWidget(self.btn_ok)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addItem(h_spacer)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.sizeConstraint = QLayout.SetDefaultConstraint
        self.main_layout.addWidget(self.txt_unicode)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addItem(v_spacer)
        self.main_layout.addLayout(buttons_layout)

        #
        # SIGNALs and SLOTs
        #

        self.character_widget.characterSelected.connect(self.insert_character)
        self.connect(self.btn_clear, SIGNAL("clicked()"), self.btn_clear_clicked)
        self.connect(self.btn_ok, SIGNAL("clicked()"), self.btn_ok_clicked)
        self.connect(self.btn_cancel, SIGNAL("clicked()"), self.btn_cancel_clicked)

    def btn_ok_clicked(self):
        txt = self.txt_unicode.text()
        self.symbol_entered_signal.emit(self.cell, txt)
        self.close()

    def btn_cancel_clicked(self):
        self.close()

    def btn_clear_clicked(self):
        self.txt_unicode.clear()

    def insert_character(self, character):
        self.txt_unicode.insert(character)
