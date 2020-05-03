from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic, QtWidgets

import sys
import os
import pickle

section_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
multi_section_window, multi_section_base = uic.loadUiType(os.path.join(section_path, 'widgets', 'multi_section.ui'))


class MultiSection(multi_section_base, multi_section_window):
    def __init__(self, parent=None):
        super(MultiSection, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.width_button.clicked.connect(self.add_width)
        self.thick_button.clicked.connect(self.add_thick)
        self.dist_button.clicked.connect(self.add_dist)
        self.remove_button.clicked.connect(self.remove_items)
        self.file = os.path.join(section_path, "widgets", "d.dat")
        self.restore_numbers()

    def restore_numbers(self):

        self.data = None
        try:
            self.data = pickle.load(open(self.file, "rb"))
        except:
            pass
        if self.data:
            self.plate_lengths.clear()
            self.plate_thicks.clear()
            self.section_dist.clear()
            self.plate_lengths.addItems(self.data["plate_lengths"])
            self.plate_thicks.addItems(self.data["plate_thicks"])
            self.section_dist.addItems(self.data["section_dist"])

    def add_width(self):
        item = self.width_box.value()
        if self.plate_lengths.findItems(str(item), Qt.MatchFixedString | Qt.MatchCaseSensitive):
            return
        self.plate_lengths.addItem(str(self.width_box.value()))

    def add_thick(self):
        item = self.width_box.value()
        if self.plate_thicks.findItems(str(item), Qt.MatchFixedString | Qt.MatchCaseSensitive):
            return
        self.plate_thicks.addItem(str(self.thick_box.value()))

    def add_dist(self):
        item = self.dist_box.value()
        if self.section_dist.findItems(str(item), Qt.MatchFixedString | Qt.MatchCaseSensitive):
            return
        self.section_dist.addItem(str(self.dist_box.value()))

    def remove_items(self):
        for lw in (self.plate_lengths, self.plate_thicks, self.section_dist):
            selected_items = lw.selectedItems()
            for item in selected_items:
                lw.takeItem(lw.row(item))

    def get_items(self, qlistwidget):
        l = []
        for i in range(qlistwidget.count()):
            l.append(qlistwidget.item(i).text())

        return l

    def accept(self):
        d = {
            "plate_lengths": self.get_items(self.plate_lengths),
            "plate_thicks": self.get_items(self.plate_thicks),
            "section_dist": self.get_items(self.section_dist),
        }
        try:
            pickle.dump(d, open(self.file, "wb"))
        except:
            pass
        multi_section_base.accept(self)
