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
        self.fill_functions()
        self.create_connections()

    def fill_groups(self):
        groups = list(self.etabs.group.names())
        sectioncut_group = "sectioncut"
        if sectioncut_group not in groups:
            groups.insert(0, sectioncut_group)
        self.form.group.addItems(groups)
        i = self.form.group.findText(sectioncut_group)
        self.form.group.setCurrentIndex(i)

    def fill_functions(self):
        funcs = self.etabs.func.response_spectrum_names()
        self.form.function_combobox.addItems(funcs)

    def create_connections(self):
        self.form.prefix_name.editingFinished.connect(self.check_prefix)
        self.form.accept_pushbutton.clicked.connect(self.accept)

    def check_prefix(self):
        if len(self.form.prefix_name.text()) < 1:
            self.form.prefix_name.setText('SEC')

    def accept(self):
        angles_inc = self.form.angles_inc.value()
        angles = range(0, 180, angles_inc)
        if self.form.cuts_groupbox.isChecked():
            group = self.form.group.currentText()
            groups = self.etabs.group.names()
            if group not in groups:
                self.etabs.group.add(group)
            prefix_name = self.form.prefix_name.text()
            self.etabs.database.create_section_cuts(group, prefix_name, angles)
        
        if self.form.spec_groupbox.isChecked():
            prefix_name = self.form.spec_prefix_name.text()
            ecc = self.form.ecc_spinbox.value()
            func = self.form.function_combobox.currentText()
            self.etabs.load_cases.add_angular_load_cases(func, range(0, 180, angles_inc), prefix_name, ecc)
        QMessageBox.information(
            None,
            'Successfull',
            f'Successfully written to etabs file.\nPlease Update Group assignment in "{group}" Group.')
        self.reject()

    def reject(self):
        self.form.close()    

    def getStandardButtons(self):
        return 0