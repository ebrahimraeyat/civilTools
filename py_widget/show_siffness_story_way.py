from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui
from PySide2.QtWidgets import QFileDialog, QMessageBox

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'show_siffness_story_way.ui'))
        # self.setupUi(self)
        # self.form = self
        self.etabs = etabs_obj
        self.form.radio_button_file.toggled.connect(self.file_toggled)
        self.form.browse_push_button.clicked.connect(self.get_file_name)

    def accept(self):
        if self.form.radio_button_2800.isChecked():
            way = '2800'
        elif self.form.radio_button_modal.isChecked():
            way = 'modal'
        elif self.form.radio_button_earthquake.isChecked():
            way = 'earthquake'
        elif self.form.radio_button_file.isChecked():
            way = 'file'
        if way != 'file':
            e_name = self.etabs.get_file_name_without_suffix()
            name = f'{e_name}_story_stiffness_{way}_table.json'
            json_file = Path(self.etabs.SapModel.GetModelFilepath()) / name
        else:
            json_file = self.form.json_line_edit.text()
        ret = self.etabs.load_from_json(json_file)
        if not ret:
            err = "Can not find the results!"
            QMessageBox.critical(self, "Error", str(err))
            return None
        data, headers = ret
        import table_model
        table_model.show_results(data, headers, table_model.StoryStiffnessModel)

    def reject(self):
        import FreeCADGui as Gui
        Gui.Control.closeDialog()

    def file_toggled(self):
        if self.form.radio_button_file.isChecked():
            self.form.json_line_edit.setEnabled(True)
            self.form.browse_push_button.setEnabled(True)
        else:
            self.form.json_line_edit.setEnabled(False)
            self.form.browse_push_button.setEnabled(False)

    def get_file_name(self):
        from pathlib import Path
        import comtypes.client
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        if not etabs:
            directory = ''
        else:
            SapModel = etabs.SapModel
            directory = str(Path(SapModel.GetModelFilename()).parent.absolute())
        filename, _ = QFileDialog.getOpenFileName(self, 'load stiffness',
                                                  directory, "json(*.json)")
        if filename == '':
            return
        self.form.json_line_edit.setText(filename)


