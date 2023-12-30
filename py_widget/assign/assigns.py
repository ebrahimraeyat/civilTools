from pathlib import Path

from PySide2 import  QtWidgets
# from PySide2.QtWidgets import QMessageBox
from PySide2.QtGui import QPixmap
from PySide2.QtGui import QIcon

import FreeCADGui as Gui


civiltools_path = Path(__file__).absolute().parent.parent.parent

class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'assign' / 'assigns.ui'))
        self.etabs = etabs_model
        self.create_connections()

    def create_connections(self):
        self.form.end_length_offset_pushbutton.clicked.connect(self.set_end_length_offset)

    def set_end_length_offset(self):
        value = self.form.end_length_offset_spinbox.value()
        self.etabs.frame_obj.set_end_length_offsets(value)
        icon = QIcon(str(civiltools_path / 'images' / 'tick.svg'))
        self.form.end_length_offset_pushbutton.setIcon(icon)

    def reject(self):
        self.form.close()    

    def getStandardButtons(self):
        return 0

    