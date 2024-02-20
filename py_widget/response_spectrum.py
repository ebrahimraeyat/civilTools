from pathlib import Path

from PySide2 import  QtWidgets, QtCore
import FreeCADGui as Gui
from PySide2.QtWidgets import QMessageBox

civiltools_path = Path(__file__).absolute().parent.parent

from exporter import civiltools_config


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'response_spectrum.ui'))
        self.etabs = etabs_obj
        # self.fill_100_30_fields(d)
        # self.select_spect_loadcases()
        self.load_config(d)
        self.create_connections()

    def create_connections(self):
        self.form.combination.clicked.connect(self.reset_widget)
        self.form.angular.clicked.connect(self.reset_widget)
        self.form.angular.clicked.connect(self.fill_angular_fields)
        self.form.run.clicked.connect(self.accept)

    def load_config(self, d):
        civiltools_config.load(self.etabs, self.form, d)

    def reset_widget(self):
        if self.form.combination.isChecked():
            self.form.angular_specs.setEnabled(False)
            self.form.section_cuts.setEnabled(False)
            self.form.x_dynamic_loadcase_list.setEnabled(True)
            self.form.y_dynamic_loadcase_list.setEnabled(True)
            self.form.y_scalefactor_combobox.setEnabled(True)
        elif self.form.angular.isChecked():
            self.form.angular_specs.setEnabled(True)
            self.form.section_cuts.setEnabled(True)
            self.form.x_dynamic_loadcase_list.setEnabled(False)
            self.form.y_dynamic_loadcase_list.setEnabled(False)
            self.form.y_scalefactor_combobox.setEnabled(False)

    def accept(self):
        ex_name = self.form.ex_combobox.currentText()
        ey_name = self.form.ey_combobox.currentText()
        x_scale_factor = float(self.form.x_scalefactor_combobox.currentText())
        y_scale_factor = float(self.form.y_scalefactor_combobox.currentText())
        num_iteration = self.form.iteration.value()
        tolerance = self.form.tolerance.value()
        reset = self.form.reset.isChecked()
        analyze = self.form.analyze.isChecked()
        consider_min_static_base_shear = self.form.consider_min_static_base_shear.isChecked()
        if self.form.angular.isChecked():
            angular_specs = [item.text() for item in self.form.angular_specs.selectedItems()]
            section_cuts = [item.text() for item in self.form.section_cuts.selectedItems()]
            self.etabs.angles_response_spectrums_analysis(
                ex_name,
                ey_name,
                angular_specs,
                section_cuts,
                x_scale_factor,
                num_iteration,
                tolerance,
                reset,
                analyze,
            )
        else:
            x_specs, y_specs = self.get_load_cases()
            _, _, df = self.etabs.scale_response_spectrums(
                ex_name,
                ey_name,
                x_specs,
                y_specs,
                x_scale_factor,
                y_scale_factor,
                num_iteration,
                tolerance,
                reset,
                analyze,
                consider_min_static_base_shear,
            )
        import table_model
        table_model.show_results(df, table_model.BaseShearModel)
        self.form.close()

    def get_load_cases(self):
        x_loadcases = []
        y_loadcases = []
        lw = self.form.x_dynamic_loadcase_list
        for i in range(lw.count()):
            item = lw.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                x_loadcases.append(item.text())
        lw = self.form.y_dynamic_loadcase_list
        for i in range(lw.count()):
            item = lw.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                y_loadcases.append(item.text())
        return x_loadcases, y_loadcases

    def reject(self):
        import FreeCADGui as Gui
        Gui.Control.closeDialog()

    def select_spect_loadcases(self):
        for lw in (self.form.x_dynamic_loadcase_list, self.form.y_dynamic_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setSelected(True)
    
    def select_angular_list(self):
        for lw in (self.form.angular_specs, self.form.section_cuts):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setSelected(True)

    # def fill_100_30_fields(self):
    #     sx, sxe, sy, sye = self.etabs.load_cases.get_sxye_seismic_load_cases()
    #     self.form.x_dynamic_loadcase_list.addItems(sx.union(sxe))
    #     self.form.y_dynamic_loadcase_list.addItems(sy.union(sye))

    def fill_angular_fields(self):
        section_cuts_angles = self.etabs.database.get_section_cuts_angle()
        angles = list(section_cuts_angles.values())
        section_cuts = list(section_cuts_angles.keys())
        angles_spectral = self.etabs.load_cases.get_spectral_with_angles(angles)
        specs = list(angles_spectral.values())
        self.form.angular_specs.clear()
        self.form.section_cuts.clear()
        self.form.angular_specs.addItems(specs)
        self.form.section_cuts.addItems(section_cuts)
        self.select_angular_list()
