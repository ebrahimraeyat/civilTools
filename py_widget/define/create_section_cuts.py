from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'create_section_cuts.ui'))
        self.etabs = etabs_model
        self.fill_groups()
        self.create_connections()

    def fill_groups(self):
        groups = self.etabs.group.names()
        self.form.group.addItems(groups)
        self.form.group.setCurrentIndex(self.form.group.count() - 1)

    def create_connections(self):
        self.form.prefix_name.editingFinished.connect(self.check_prefix)

    def check_prefix(self):
        if len(self.form.prefix_name.text()) < 1:
            self.form.prefix_name.setText('SEC')

    def accept(self):
        group = self.form.group.currentText()
        groups = self.etabs.group.names()
        if not group in groups:
            self.etabs.group.add(group)
        prefix_name = self.form.prefix_name.text()
        angles_inc = self.form.angles_inc.value()
        angles = range(0, 180, angles_inc)
        self.etabs.database.create_section_cuts(group, prefix_name, angles)
        QMessageBox.information(None, 'Successfull','Successfully written to etabs file.')