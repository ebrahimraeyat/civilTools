# -*- coding: utf-8 -*-
"""
Program:
    CivilTools
    (CivilTools)
    formwidget.py

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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import resources.resources
import sys
from applications.cfactor.MainWindow import Cfactor
from applications.section.MainWindow import Window


class FormWidget(QWidget):
    def __init__(self, parent=None):
        super(FormWidget, self).__init__(parent)

        self.form_ui()

    def form_ui(self):

        h_spacer = QSpacerItem(2, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        v_spacer = QSpacerItem(20, 2, QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)

        self.btn_size = QSize(200, 60)
        self.icon_size = QSize(40, 40)

        #
        # Icons
        #

        self.icon_cfactor = QIcon(":/cfactor_resources/icons/cfactor/cfactor.png")
        self.icon_section = QIcon(":/section_resources/icons/section/2IPEPL.png")

        self.img = QWidget(self)

        #
        # Widgets - Tabs
        #

        self.select_tab_widget = QTabWidget(self)
        self.eng_tab = QWidget()
        self.multimedia_tab = QWidget()
        self.select_tab_widget.addTab(self.eng_tab, "Engineering")
        #self.select_tab_widget.addTab(self.multimedia_tab, "Other")

        #
        # Widgets - Labels
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        s = u"<b>ابزارهای مهندسین عمران</b><br />مجموعه ابزارهای کدباز برای مهندسین عمران تحت لیسانس  GPLv3"
        self.lb_app = QLabel(self.img)
        self.lb_app.setTextFormat(Qt.RichText)
        self.lb_app.setText(s)
        size_policy.setHeightForWidth(self.lb_app.sizePolicy().hasHeightForWidth())
        self.lb_app.setSizePolicy(size_policy)
        self.lb_app.setAlignment(Qt.AlignHCenter)
        self.lb_app.setStyleSheet("font-style:italic; font-size: 10pt;")
        self.lb_app.setWordWrap(True)
        self.lb_app.setMinimumSize(QSize(200, 40))

        self.lb_img = QLabel(self.img)
        picture = QPixmap(":/main_resources/icons/libreengineering.png")
        self.lb_img.setPixmap(picture)
        self.lb_img.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        #
        # Widgets - Buttons
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.btn_cfactor = QPushButton(self.icon_cfactor, u"ضریب زلزله", self.eng_tab)
        self.btn_cfactor.setToolTip("cfactor calculation")
        size_policy.setHeightForWidth(self.btn_cfactor.sizePolicy().hasHeightForWidth())
        self.btn_cfactor.setSizePolicy(size_policy)
        self.btn_cfactor.setMinimumSize(self.btn_size)
        self.btn_cfactor.setIconSize(self.icon_size)
        self.btn_section = QPushButton(self.icon_section, u"مشخصات مقاطع", self.eng_tab)
        self.btn_section.setToolTip("section calculation")
        size_policy.setHeightForWidth(self.btn_section.sizePolicy().hasHeightForWidth())
        self.btn_section.setSizePolicy(size_policy)
        self.btn_section.setMinimumSize(self.btn_size)
        self.btn_section.setIconSize(self.icon_size)

        #self.btn_codec = QPushButton(self.icon_codec, "Codec", self.eng_tab)
        #self.btn_codec.setToolTip("Audio, Video and Image Codec")
        #size_policy.setHeightForWidth(self.btn_codec.sizePolicy().hasHeightForWidth())
        #self.btn_codec.setSizePolicy(size_policy)
        #self.btn_codec.setMinimumSize(self.btn_size)
        #self.btn_codec.setIconSize(self.icon_size)
        #self.btn_translit = QPushButton(self.icon_translit, "Translit", self.eng_tab)
        #self.btn_translit.setToolTip("Keyboard Key Translation")
        #size_policy.setHeightForWidth(self.btn_translit.sizePolicy().hasHeightForWidth())
        #self.btn_translit.setSizePolicy(size_policy)
        #self.btn_translit.setMinimumSize(self.btn_size)
        #self.btn_translit.setIconSize(self.icon_size)

        #
        # Layouts
        #

        eng_btn_layout = QGridLayout(self.eng_tab)
        eng_btn_layout.sizeConstraint = QLayout.SetDefaultConstraint
        eng_btn_layout.addWidget(self.btn_section, 0, 0)
        eng_btn_layout.addWidget(self.btn_cfactor, 1, 0)
        eng_btn_layout.addItem(h_spacer, 0, 3, 4, 1)
        eng_btn_layout.addItem(v_spacer, 4, 0)

        #multimedia_btn_layout = QGridLayout(self.multimedia_tab)
        #multimedia_btn_layout.sizeConstraint = QLayout.SetDefaultConstraint
        #multimedia_btn_layout.addWidget(self.btn_codec, 0, 0)
        #multimedia_btn_layout.addWidget(self.btn_translit, 0, 1)
        #multimedia_btn_layout.addItem(h_spacer, 0, 2)
        #multimedia_btn_layout.addItem(h_spacer, 0, 3, 1, 1)
        #multimedia_btn_layout.addItem(v_spacer, 1, 0)

        img_layout = QVBoxLayout(self.img)
        img_layout.sizeConstraint = QLayout.SetDefaultConstraint
        img_layout.addWidget(self.lb_img)
        img_layout.addWidget(self.lb_app)

        main_layout = QHBoxLayout(self)
        main_layout.sizeConstraint = QLayout.SetDefaultConstraint
        main_layout.addWidget(self.select_tab_widget)
        main_layout.addWidget(self.img)

        #
        # SIGNALs ans SLOTs
        #

        self.connect(self.btn_cfactor, SIGNAL("clicked()"), self.btn_cfactor_clicked)
        self.connect(self.btn_section, SIGNAL("clicked()"), self.btn_section_clicked)
        #self.connect(self.btn_codec, SIGNAL("clicked()"), self.btn_codec_clicked)
        #self.connect(self.btn_translit, SIGNAL("clicked()"), self.btn_translit_clicked)

    def btn_cfactor_clicked(self):
        cfactor = Cfactor(self)
        cfactor.show()

    def btn_section_clicked(self):
        section = Window(self)
        section.show()

    def btn_codec_clicked(self):
        codec = Codec(self)
        codec.show()

    def btn_translit_clicked(self):
        translit = Translit(self)
        translit.show()

