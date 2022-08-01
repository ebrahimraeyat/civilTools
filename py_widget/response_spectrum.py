from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui
from PySide2.QtWidgets import QMessageBox

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj, show_message=True):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'response_spectrum.ui'))
        # self.setupUi(self)
        # self.form = self
        self.etabs = etabs_obj
        self.show_message = show_message
        self.fill_100_30_fields()
        self.select_spect_loadcases()
        self.create_connections()

    def create_connections(self):
        self.form.combination.clicked.connect(self.reset_widget)
        self.form.angular.clicked.connect(self.reset_widget)
        self.form.angular.clicked.connect(self.fill_angular_fields)
        self.form.run.clicked.connect(self.accept)

    def reset_widget(self):
        if self.form.combination.isChecked():
            self.form.angular_specs.setEnabled(False)
            self.form.section_cuts.setEnabled(False)
            self.form.x_loadcase_list.setEnabled(True)
            self.form.y_loadcase_list.setEnabled(True)
            self.form.y_scalefactor.setEnabled(True)
        elif self.form.angular.isChecked():
            self.form.angular_specs.setEnabled(True)
            self.form.section_cuts.setEnabled(True)
            self.form.x_loadcase_list.setEnabled(False)
            self.form.y_loadcase_list.setEnabled(False)
            self.form.y_scalefactor.setEnabled(False)

    def accept(self):
        ex_name = self.form.static_x.currentText()
        ey_name = self.form.static_y.currentText()
        x_specs = [item.text() for item in self.form.x_loadcase_list.selectedItems()]
        y_specs = [item.text() for item in self.form.y_loadcase_list.selectedItems()]
        angular_specs = [item.text() for item in self.form.angular_specs.selectedItems()]
        section_cuts = [item.text() for item in self.form.section_cuts.selectedItems()]
        x_scale_factor = self.form.x_scalefactor.value()
        y_scale_factor = self.form.y_scalefactor.value()
        num_iteration = self.form.iteration.value()
        tolerance = self.form.tolerance.value()
        reset = self.form.reset.isChecked()
        analyze = self.form.analyze.isChecked()
        if self.form.angular.isChecked():
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
            self.etabs.scale_response_spectrums(
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
            )
        if self.show_message:
            msg = "Done Response Spectrum Analysis."
            QMessageBox.information(None, 'Successful', str(msg))

    def reject(self):
        import FreeCADGui as Gui
        Gui.Control.closeDialog()

    def select_spect_loadcases(self):
        for lw in (self.form.x_loadcase_list, self.form.y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setSelected(True)
    
    def select_angular_list(self):
        for lw in (self.form.angular_specs, self.form.section_cuts):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setSelected(True)

    def fill_100_30_fields(self):
        ex_name, ey_name = self.etabs.load_patterns.get_EX_EY_load_pattern()
        x_names, y_names = self.etabs.load_cases.get_xy_seismic_load_cases()
        self.form.static_x.addItems(x_names)
        self.form.static_y.addItems(y_names)
        if ex_name is not None:
            self.form.static_x.setCurrentText(ex_name)
        if ey_name is not None:
            self.form.static_y.setCurrentText(ey_name)
        x_specs, y_specs = self.etabs.load_cases.get_response_spectrum_xy_loadcases_names()
        self.form.x_loadcase_list.addItems(x_specs)
        self.form.y_loadcase_list.addItems(y_specs)

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
