from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui

import table_model

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'control_joint_shear_bc.ui'))
        self.etabs = etabs_model
        self.d = d
        self.set_structure_type()
        self.create_connections()
        self.main_file_path = None

    def set_structure_type(self):
        ductilities = self.etabs.get_x_and_y_system_ductility(self.d)
        if "M" in ductilities:
            self.form.structure_type_combobox.setCurrentIndex(0)
        elif "H" in ductilities:
            self.form.structure_type_combobox.setCurrentIndex(1)
            self.form.show_bc_table.setChecked(True)

    def create_connections(self):
        self.form.check.clicked.connect(self.check)

    def check(self):
        show_js = self.form.show_js_table.isChecked()
        show_bc = self.form.show_bc_table.isChecked()
        create_js_file = not self.form.only_show_results_checkbox.isChecked()
        filename = ""
        if show_js:
            filename += "js"
        if show_bc:
            filename += "bc"
        open_main_file = True
        structure_type = self.form.structure_type_combobox.currentText()
        df = self.etabs.create_joint_shear_bcc_file(
            filename,
            structure_type,
            open_main_file=open_main_file,
            create_file=create_js_file,
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
        self.accept()

    def accept(self):
        self.form.close()

    def reject(self):
        self.accept()

    def getStandardButtons(self):
        return 0