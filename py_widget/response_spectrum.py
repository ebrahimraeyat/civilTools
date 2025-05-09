from pathlib import Path

from PySide2 import  QtWidgets, QtCore
import FreeCADGui as Gui


civiltools_path = Path(__file__).absolute().parent.parent

from exporter import civiltools_config




class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'response_spectrum.ui'))
        self.etabs = etabs_obj
        self.d = d
        self.angular_model = None
        self.load_config(d)
        self.create_connections()

    def create_connections(self):
        self.form.combination_response_spectrum_checkbox.clicked.connect(self.reset_widget)
        self.form.angular_response_spectrum_checkbox.clicked.connect(self.reset_widget)
        self.form.run.clicked.connect(self.accept)

    def load_config(self, d):
        civiltools_config.load(self.etabs, self.form, d)
        if not d.get('activate_second_system', False):
            self.form.ex1_combobox.setEnabled(False)
            self.form.ey1_combobox.setEnabled(False)
            self.form.ex1_drift_combobox.setEnabled(False)
            self.form.ey1_drift_combobox.setEnabled(False)

    def reset_widget(self, checked):
        sender = self.sender()
        if sender == self.form.combination_response_spectrum_checkbox:
            self.form.angular_tableview.setEnabled(not checked)
            self.form.angular_response_spectrum_checkbox.setChecked(not checked)
            self.form.x_dynamic_loadcase_list.setEnabled(checked)
            self.form.y_dynamic_loadcase_list.setEnabled(checked)
            self.form.y_scalefactor_combobox.setEnabled(checked)
            self.form.x_label.setEnabled(checked)
            self.form.y_label.setEnabled(checked)
        elif sender == self.form.angular_response_spectrum_checkbox:
            self.form.combination_response_spectrum_checkbox.setChecked(not checked)
            self.form.angular_tableview.setEnabled(checked)
            self.form.x_dynamic_loadcase_list.setEnabled(not checked)
            self.form.y_dynamic_loadcase_list.setEnabled(not checked)
            self.form.y_scalefactor_combobox.setEnabled(not checked)
            self.form.tabwidget.setCurrentIndex(0)
            self.form.x_label.setEnabled(not checked)
            self.form.y_label.setEnabled(not checked)

    def accept(self):
        index = self.form.tabwidget.currentIndex()
        if index == 0 or self.form.angular_response_spectrum_checkbox.isChecked():
            ex_name = self.form.ex_combobox.currentText()
            ey_name = self.form.ey_combobox.currentText()
            if self.d.get('activate_second_system', False):
                ex1_name = self.form.ex1_combobox.currentText()
                ey1_name = self.form.ey1_combobox.currentText()
                ex_name = [ex_name, ex1_name]
                ey_name = [ey_name, ey1_name]
            lws = [self.form.x_dynamic_loadcase_list, self.form.y_dynamic_loadcase_list]
        elif index == 1:
            ex_name = self.form.ex_drift_combobox.currentText()
            ey_name = self.form.ey_drift_combobox.currentText()
            if self.d.get('activate_second_system', False):
                ex1_name = self.form.ex1_drift_combobox.currentText()
                ey1_name = self.form.ey1_drift_combobox.currentText()
                ex_name = [ex_name, ex1_name]
                ey_name = [ey_name, ey1_name]
            lws = [self.form.x_dynamic_drift_loadcase_list, self.form.y_dynamic_drift_loadcase_list]
        x_scale_factor = float(self.form.x_scalefactor_combobox.currentText())
        y_scale_factor = float(self.form.y_scalefactor_combobox.currentText())
        num_iteration = self.form.iteration.value()
        tolerance = self.form.tolerance.value()
        reset = self.form.reset.isChecked()
        analyze = self.form.analyze.isChecked()
        consider_min_static_base_shear = self.form.consider_min_static_base_shear.isChecked()
        if self.form.angular_response_spectrum_checkbox.isChecked():
            way = "angular"
            angular_specs = []
            section_cuts = []
            angular_model = self.form.angular_tableview.model()
            for row in range(angular_model.rowCount()):
                index = angular_model.index(row, 1)
                spec = angular_model.data(index)
                angular_specs.append(spec)
                index = angular_model.index(row, 2)
                sec_cut = angular_model.data(index)
                section_cuts.append(sec_cut)
            _, df = self.etabs.angles_response_spectrums_analysis(
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
            x_specs, y_specs = self.get_load_cases(*lws)
            way = "100-30"
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
        table_model.show_results(df, table_model.BaseShearModel,
                                 etabs=self.etabs,
                                 json_file_name=f"BaseShear{way.capitalize()}")
        self.form.close()

    def get_load_cases(self, lwx, lwy):
        x_loadcases = []
        y_loadcases = []
        for i in range(lwx.count()):
            item = lwx.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                x_loadcases.append(item.text())
        for i in range(lwy.count()):
            item = lwy.item(i)
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

