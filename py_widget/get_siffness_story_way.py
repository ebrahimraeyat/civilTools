from pathlib import Path

import pandas as pd

from PySide import QtGui
import FreeCADGui as Gui
import FreeCAD
from PySide.QtGui import QMessageBox

import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtGui.QWidget):
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
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        char_len = int(p.GetFloat('table_max_etabs_model_name_length', 200))
        import table_model
        df = pd.DataFrame(ret[0], columns=ret[1])
        table_model.show_results(df, table_model.StoryStiffnessModel,
                                 etabs=self.etabs,
                                 json_file_name=f"StoryStiffness{way.capitalize()} {self.etabs.get_file_name_without_suffix()[:char_len]}")
        self.form.close()
