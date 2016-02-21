#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Program:
    LibreEngineering
    (LibreEngineering)
    libreengineering.pyw

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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from formwidget import FormWidget
import sys
import versions

class CivilTools(QMainWindow):
    def __init__(self, parent = None):
        super(CivilTools, self).__init__(parent)

        if sys.platform == "win32":
            self.setStyleSheet("font-family: Arial Unicode MS;")

        self.main_ui()

    def main_ui(self):
        self.win_title = u"ابزارهای مهندسین عمران"

        self.win_size = QSize(300, 200)

        self.icon_win = QIcon(":/main_resources/icons/libreengineering.png")
        self.icon_about = QIcon(":/main_resources/icons/libreengineering.png")
        self.icon_quit = QIcon(":/main_resources/icons/main/quit.png")

        self.setWindowIcon(self.icon_win)
        self.resize(self.win_size)
        self.setWindowTitle(self.win_title)

        h_spacer = QSpacerItem(2, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        v_spacer = QSpacerItem(20, 2, QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)

        self.main_widget = QWidget(self)

        self.form_widget = FormWidget(self)

        #
        # Widgets - PushButtons
        #

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.btn_about = QPushButton(self.icon_about, u"درباره", self.main_widget)
        size_policy.setHeightForWidth(self.btn_about.sizePolicy().hasHeightForWidth())
        self.btn_about.setSizePolicy(size_policy)
        self.btn_about.setMinimumSize(100, 25)
        self.btn_quit = QPushButton(self.icon_quit, u"خروج", self.main_widget)
        size_policy.setHeightForWidth(self.btn_quit.sizePolicy().hasHeightForWidth())
        self.btn_quit.setSizePolicy(size_policy)
        self.btn_quit.setMinimumSize(100, 25)
        #btn_font = QPushButton(u'فونت نرم افزار', self.main_widget)
        #btn_font.clicked.connect(self.setfont)

        #
        # Layouts
        #

        btn_layout = QHBoxLayout()
        btn_layout.sizeConstraint = QLayout.SetDefaultConstraint
        btn_layout.addItem(h_spacer)
        #btn_layout.addWidget(btn_font)
        btn_layout.addWidget(self.btn_about)
        btn_layout.addWidget(self.btn_quit)

        main_layout = QVBoxLayout(self.main_widget)
        main_layout.sizeConstraint = QLayout.SetDefaultConstraint
        main_layout.addWidget(self.form_widget)
        main_layout.addLayout(btn_layout)
        main_layout.addItem(v_spacer)

        self.main_widget.setLayout(main_layout)
        self.setCentralWidget(self.main_widget)

        #
        # SIGNALs and SLOTs
        #

        self.connect(self.btn_about, SIGNAL("clicked()"), self.action_about_triggered)
        self.connect(self.btn_quit, SIGNAL("clicked()"), self.close)

    def action_about_triggered(self):
        msg = self.win_title + u" - مجموعه ابزارها برای استفاده مهندسین عمران."
        msg += u"ورژن   " + versions.ver_civilTools + "\n\n"

        msg += u"ویژگی ها:\n\n"

        msg += u"- محاسبه ضریب زلزله مطابق با آخرین ویرایش آیین نامه ۲۸۰۰ زلزله ویرایش ۴ (ورژن {})\n".format(versions.ver_cfactor)
        msg += u"- محاسبه مشخصات مقاطع دوبل با ورق برای استفاده در ETABS 2013-2015 (ورژن {})\n".format(versions.ver_section)

        msg += "\n"

        msg += u"- نوشته شده با پیتون و کیوت\n"
        msg += u"- عدم وابستگی به سیستم عامل ( در لینوکس و ویندوز تست شده)\n"
        msg += u"- تحت لیسانس " + versions.license + "\n\n"
        msg += u"- توسعه دهنده: ابراهیم رعیت رکن آبادی"
        QMessageBox.about(self, u"درباره - " + self.win_title, msg)

    def setfont(self):
        font, ok = QFontDialog.getFont(self.font(), self)
        if ok:
            self.setFont(font);

        #self.setFont(QFontDialog.getFont(QFont("Helvetica [Cronyx]", 10), self.font()));

if __name__ == '__main__':
    app = QApplication(sys.argv)
    global defaultPointsize
    font = QFont()
    font.setFamily("Tahoma")
    if sys.platform.startswith('linux'):
        defaultPointsize = 10
        font.setPointSize(defaultPointsize)
    else:
        defaultPointsize = 9
        font.setPointSize(defaultPointsize)
    app.setFont(font)

    #if sys.platform == "win32":
    #app.setStyle("plastique")
    main_windows = []
    for a in sys.argv[1:] or [None]:
        win = CivilTools(a)
        win.setLayoutDirection(Qt.RightToLeft)
        win.show()
        main_windows.append(win)

    sys.exit(app.exec_())
