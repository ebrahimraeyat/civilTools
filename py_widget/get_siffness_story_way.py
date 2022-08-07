from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui
from PySide2.QtWidgets import QMessageBox

import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'get_siffness_story_way.ui'))
        self.etabs = etabs_obj
        self.form.run.clicked.connect(self.accept)

    def accept(self):
        if self.form.radio_button_2800.isChecked():
                way = '2800'
        if self.form.radio_button_modal.isChecked():
            way = 'modal'
        if self.form.radio_button_earthquake.isChecked():
            way = 'earthquake'
        ret = self.etabs.get_story_stiffness_table(way)
        if not ret:
            err = "Please Activate Calculate Diaphragm Center of Rigidity in ETABS!"
            QMessageBox.critical(None, "Error", err)
            return None
        data, headers = ret
        import table_model
        table_model.show_results(data, headers, table_model.StoryStiffnessModel)
        self.form.close()
