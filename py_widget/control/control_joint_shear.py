from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui

import table_model

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'control_joint_shear_bc.ui'))
        self.etabs = etabs_model
        self.create_connections()
        self.main_file_path = None

    def get_file_name(self):
        return str(self.etabs.get_filename_path_with_suffix(".EDB"))

    def create_connections(self):
        self.form.check.clicked.connect(self.check)
        self.form.cancel_button.clicked.connect(self.reject)
        self.form.open_main_file_button.clicked.connect(self.open_main_file)
        self.form.structure_type_combobox.currentIndexChanged.connect(self.set_open_main_file)

    def set_open_main_file(self, index):
        st_type = self.form.structure_type_combobox.currentText()
        if st_type == 'Sway Special':
            self.form.open_main_file.setEnabled(False)
            self.form.open_main_file.setChecked(False)
        else:
            self.form.open_main_file.setEnabled(True)
            self.form.open_main_file.setChecked(True)

    def open_main_file(self):
        self.etabs.SapModel.File.OpenFile(str(self.main_file_path))
        self.accept()

    def check(self):
        self.main_file_path = self.get_file_name()
        show_js = self.form.show_js_table.isChecked()
        show_bc = self.form.show_bc_table.isChecked()
        filename = ""
        if show_js:
            filename += "js"
        if show_bc:
            filename += "bc"
        open_main_file = self.form.open_main_file.isChecked()
        structure_type = self.form.structure_type_combobox.currentText()
        df = self.etabs.create_joint_shear_bcc_file(
            filename,
            structure_type,
            open_main_file=open_main_file,
            )
        if df is None:
            return
        if show_js and show_bc:
            table_model.show_results(
                df,
                model=table_model.JointShearBCC,
                function=self.etabs.view.show_frame,
                etabs=self.etabs,
                json_file_name="JointShearAndBeamColumnCapcity",
                )
        elif show_js:
            table_model.show_results(
                df[['Story', 'Label', 'UniqueName', 'JSMajRatio', 'JSMinRatio']],
                model=table_model.JointShearBCC,
                function=self.etabs.view.show_frame,
                etabs=self.etabs,
                json_file_name="JointShear",
                )
        elif show_bc:
            table_model.show_results(
                df[['Story', 'Label', 'UniqueName', 'BCMajRatio', 'BCMinRatio']],
                model=table_model.JointShearBCC,
                function=self.etabs.view.show_frame,
                etabs=self.etabs,
                json_file_name="BeamColumnCapcity",
                )
        if open_main_file or structure_type == 'Sway Special':
            self.accept()
        else:
            self.form.open_main_file_button.setEnabled(True)
            self.form.check.setEnabled(False)

    def accept(self):
        Gui.Control.closeDialog()

    def reject(self):
        if (
            self.main_file_path is not None and
            self.main_file_path != self.get_file_name() and
            QtWidgets.QMessageBox.question(
            None,
            'Open Main File',
            'Do you want to Open Main File?',)
            ) == QtWidgets.QMessageBox.Yes:
            self.open_main_file()
        self.accept()

    def getStandardButtons(self):
        return 0