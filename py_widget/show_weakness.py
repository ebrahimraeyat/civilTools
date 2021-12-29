from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui
from PySide2.QtWidgets import QFileDialog, QMessageBox

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'show_weakness.ui'))
        # self.setupUi(self)
        # self.form = self
        self.etabs = etabs_obj
        self.directory = str(Path(self.etabs.SapModel.GetModelFilename()).parent)
        self.set_filenames()
        self.create_connections()

    def accept(self):
        use_json_file = self.form.file_groupbox.isChecked()
        dir_ = 'x' if self.form.x_radio_button.isChecked() else 'y'
        if use_json_file:
            json_file = Path(self.form.json_file.text())
        else:
            json_file = Path(self.etabs.SapModel.GetModelFilepath()) / f'columns_pmm_beams_rebars_{dir_}.json'
        if json_file.exists():
            import table_model
            ret = self.etabs.load_from_json(json_file)
            data, headers, data2, headers2 = ret
            table_model.show_results(data, headers, table_model.ColumnsRatioModel)
            table_model.show_results(data2, headers2, table_model.BeamsRebarsModel)
        else:
            err = "Please first get weakness ration, then show it!"
            QMessageBox.critical(self, "Error", str(err))
            return None

    def reject(self):
        import FreeCADGui as Gui
        Gui.Control.closeDialog()

    def set_filenames(self):
        f = Path(self.etabs.SapModel.GetModelFilename())
        if self.form.x_radio_button.isChecked():
            self.form.json_file.setText(str(f.with_name('columns_pmm_beams_rebars_x.json')))
        elif self.form.y_radio_button.isChecked():
            self.form.json_file.setText(str(f.with_name('columns_pmm_beams_rebars_y.json')))
        
    def create_connections(self):
        self.form.weakness_button.clicked.connect(self.get_filename)
        self.form.x_radio_button.toggled.connect(self.set_filenames)
        self.form.y_radio_button.toggled.connect(self.set_filenames)
        self.form.file_groupbox.toggled.connect(self.change_frame_enable)

    def change_frame_enable(self):
        if self.form.file_groupbox.isChecked():
            self.form.dir_frame.setEnabled(False)
        else:
            self.form.dir_frame.setEnabled(True)

    def get_filename(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'select *.json file',
                                                  self.directory, "Results(*.json)")
        if filename == '':
            return
        self.form.json_file.setText(filename)

