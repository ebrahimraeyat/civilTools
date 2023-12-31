from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtGui import QIcon

import FreeCADGui as Gui


civiltools_path = Path(__file__).absolute().parent.parent.parent
tick_icon = QIcon(str(civiltools_path / 'images' / 'tick.svg'))

class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'assign' / 'assigns.ui'))
        self.etabs = etabs_model
        self.fill_form()
        self.create_connections()

    def create_connections(self):
        self.form.set_end_length_offset_pushbutton.clicked.connect(self.set_end_length_offset)
        self.form.check_diaphragm_pushbutton.clicked.connect(self.check_diaphragm)
        self.form.set_diaphragm_pushbutton.clicked.connect(self.set_diaphragm)

    def set_end_length_offset(self):
        value = self.form.end_length_offset_spinbox.value()
        self.etabs.frame_obj.set_end_length_offsets(value)
        self.form.set_end_length_offset_pushbutton.setIcon(tick_icon)

    def check_diaphragm(self):
        if self.etabs.diaphragm.is_diaphragm_assigned():
            self.form.check_diaphragm_pushbutton.setIcon(tick_icon)
        else:
            QtWidgets.QMessageBox.warning(None, 'Diaphragm', 'Diaphragm did not assigned.')

    def set_diaphragm(self):
        diaph_name = self.form.diaphragm_combobox.currentText()
        if diaph_name not in self.etabs.diaphragm.names():
            self.etabs.diaphragm.add_diaphragm(diaph_name)
        self.etabs.diaphragm.set_area_diaphragms(diaph_name)
        self.form.set_diaphragm_pushbutton.setIcon(tick_icon)

    def fill_form(self):
        diaphs = self.etabs.diaphragm.names()
        if diaphs:
            self.form.diaphragm_combobox.addItems(diaphs)

    def reject(self):
        self.form.close()    

    def getStandardButtons(self):
        return 0

    