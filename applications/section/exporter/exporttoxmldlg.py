from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic, QtWidgets

import sys
import os
import itertools

import sec

section_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
export_xml_window, xml_base = uic.loadUiType(os.path.join(section_path, 'widgets', 'export_xml.ui'))

useAsDict = {'Beam': 'B', 'Column': 'C', 'Brace': 'C'}
ductilityDict = {'Medium': 'M', 'High': 'H'}


class ExportToXml(xml_base, export_xml_window):
    def __init__(self, sections, parent=None):
        super(ExportToXml, self).__init__()
        self.setupUi(self)
        self.sections = sections
        self.xml_button.clicked.connect(self.select_file)

    def accept(self):
        filename = self.xml_path_line.text()
        if not filename:
            return
        if not filename.endswith('xml'):
            filename += '.xml'

        ductilities = [ductilityDict[item.text()] for item in self.ductility_list.selectedItems()]
        useAss = [useAsDict[item.text()] for item in self.use_as_list.selectedItems()]
        states = [f'{state[0]}{state[1]}' for state in itertools.product(useAss, ductilities)]

        sections = []
        for section in self.sections:
            if section.name[-2:] in states:
                sections.append(section)
        sec.Section.exportXml(filename, sections)

        xml_base.accept(self)

    def select_file(self):
        self.xml_path_line.setText(QFileDialog.getSaveFileName(filter="xml(*.xml)")[0])
