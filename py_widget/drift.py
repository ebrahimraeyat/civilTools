from pathlib import Path

import pandas as pd

from PySide import QtGui
from PySide.QtGui import QMessageBox
from PySide.QtCore import Qt

import FreeCADGui as Gui
import FreeCAD

from exporter import civiltools_config

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtGui.QWidget):
    def __init__(self, etabs_obj, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / "widgets" / "drift.ui"))
        self.etabs = etabs_obj
        self.dynamic_tab_clicked = False
        self.d = d
        self.create_connections()
        self.load_config(d)

    def create_connections(self):
        self.form.run.clicked.connect(self.accept)
        self.form.create_t_file_box.clicked.connect(self.create_t_file_clicked)

    def create_t_file_clicked(self, check):
        self.form.structuretype_groupbox.setEnabled(check)

    def load_config(self, d):
        civiltools_config.load(self.etabs, self.form, d)

    def fill_angular_fields(self):
        lw = self.form.angular_specs
        if lw.count() > 0:
            return
        angles_spectral = self.etabs.load_cases.get_spectral_with_angles()
        specs = list(angles_spectral.values())
        lw.clear()
        lw.addItems(specs)
        for i in range(lw.count()):
            item = lw.item(i)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)

    def reset_widget(self):
        if self.form.xy.isChecked():
            self.form.angular_specs.setEnabled(False)
            self.form.x_dynamic_drift_loadcase_list.setEnabled(True)
            self.form.y_dynamic_drift_loadcase_list.setEnabled(True)
        elif self.form.angular.isChecked():
            self.form.angular_specs.setEnabled(True)
            self.form.x_dynamic_drift_loadcase_list.setEnabled(False)
            self.form.y_dynamic_drift_loadcase_list.setEnabled(False)

    def accept(self):
        create_t_file = self.form.create_t_file_box.isChecked()
        modal = self.d.get("modal_combobox", None)
        if modal is None:
            modals = self.etabs.load_cases.get_loadcase_withtype(3)
            if create_t_file and len(modals) == 0:
                message = 'You must define a Modal Case in your model.'
                QMessageBox.warning(None,
                                    'Modal LoadCase',
                                    message)
            return False
        d = civiltools_config.get_settings_from_etabs(self.etabs)
        tab = self.form.tab_widget.currentIndex()
        structure_type = "concrete"
        if self.form.steel_radiobutton.isChecked():
            structure_type = "steel"
        #     no_of_stories = d['no_of_story_x'] + d['no_of_story_x1']
        no_of_stories = d["no_of_story_x"]
        cdx = d["cdx"]
        cdy = d["cdy"]
        two_system = d.get("activate_second_system", False)
        if create_t_file:
            self.etabs.unlock_model()
            tx, ty, main_file = self.etabs.get_drift_periods(
                structure_type=structure_type
            )
            civiltools_config.save_analytical_periods(self.etabs, tx, ty)
            building = civiltools_config.current_building_from_etabs(self.etabs)
            if two_system:
                if building.building2.x_system.Ru >= building.x_system.Ru:
                    cdx = building.building2.x_system.cd
                if building.building2.y_system.Ru >= building.y_system.Ru:
                    cdy = building.building2.y_system.cd
            data = self.get_data_for_apply_earthquakes(building, d)
            self.etabs.apply_cfactors_to_edb(data, d=d)
            if tab == 1:
                # execute scale response spectrum
                x_specs, y_specs, _ = self.get_load_cases(tab=1)
                ex_name = d.get("ex_drift_combobox")
                ey_name = d.get("ey_drift_combobox")
                x_scale_factor = float(self.form.x_scalefactor_combobox.currentText())
                y_scale_factor = float(self.form.y_scalefactor_combobox.currentText())
                self.etabs.scale_response_spectrums(
                    ex_name,
                    ey_name,
                    x_specs,
                    y_specs,
                    x_scale_factor,
                    y_scale_factor,
                )
        # For two systems that not ticks the create t file, Temporary
        else:
            if two_system:
                rux = d.get("Rux", None)
                if rux:
                    ruy = d.get("Ruy", None)
                    rux1 = d.get("Rux1", None)
                    ruy1 = d.get("Ruy1", None)
                    if rux1 >= rux:
                        cdx = d.get("cdx1")
                    if ruy1 >= ruy:
                        cdy = d.get("cdy1")
                else:
                    building = civiltools_config.current_building_from_etabs(self.etabs)
                    if building.building2.x_system.Ru >= building.x_system.Ru:
                        cdx = building.building2.x_system.cd
                    if building.building2.y_system.Ru >= building.y_system.Ru:
                        cdy = building.building2.y_system.cd
        # Get Drifts
        x_loadcases, y_loadcases, loadcases = self.get_load_cases(tab)
        if not loadcases:
            loadcases = x_loadcases + y_loadcases
        ret = self.etabs.get_drifts(
            no_of_stories,
            cdx,
            cdy,
            loadcases,
            x_loadcases,
            y_loadcases,
        )
        if create_t_file and structure_type == "steel":
            print(f"Opening file {main_file}\n")
            self.etabs.SapModel.File.OpenFile(str(main_file))
            civiltools_config.save_analytical_periods(self.etabs, tx, ty)
            data = self.get_data_for_apply_earthquakes(building, d)
            self.etabs.apply_cfactors_to_edb(data, d=d)
        if ret is None:
            QMessageBox.warning(
                None, "Diphragm", "Please Check that you assigned diaphragm to stories."
            )
            return
        import table_model
        if tab == 1:
            analysis_type = 'Dynamic'
        else:
            analysis_type = 'Static'
        df = pd.DataFrame(ret[0], columns=ret[1])
        model_name = "Drift"
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        char_len = int(p.GetFloat('table_max_etabs_model_name_length', 200))
        if self.form.show_separate_checkbox.isChecked():
            filt = df["OutputCase"].isin(x_loadcases)
            df1 = df.loc[filt]
            table_model.show_results(df1, table_model.DriftModel, etabs=self.etabs,
                                     json_file_name=f"{analysis_type}{model_name}XDir {self.etabs.get_file_name_without_suffix()[:char_len]}")
            filt = df["OutputCase"].isin(y_loadcases)
            df1 = df.loc[filt]
            table_model.show_results(df1, table_model.DriftModel, etabs=self.etabs,
                                     json_file_name=f"{analysis_type}{model_name}YDir {self.etabs.get_file_name_without_suffix()[:char_len]}")
        else:
            table_model.show_results(df, table_model.DriftModel, etabs=self.etabs,
                                     json_file_name=f"{analysis_type}{model_name} {self.etabs.get_file_name_without_suffix()[:char_len]}")
        self.form.close()

    def get_load_cases(self, tab):
        x_loadcases = []
        y_loadcases = []
        loadcases = []

        if tab == 0:
            lw = self.form.x_drift_loadcase_list
            for i in range(lw.count()):
                item = lw.item(i)
                if item.checkState() == Qt.Checked:
                    x_loadcases.append(item.text())
            lw = self.form.y_drift_loadcase_list
            for i in range(lw.count()):
                item = lw.item(i)
                if item.checkState() == Qt.Checked:
                    y_loadcases.append(item.text())
        elif tab == 1:
            if self.form.xy.isChecked():
                lw = self.form.x_dynamic_drift_loadcase_list
                for i in range(lw.count()):
                    item = lw.item(i)
                    if item.checkState() == Qt.Checked:
                        x_loadcases.append(item.text())
                lw = self.form.y_dynamic_drift_loadcase_list
                for i in range(lw.count()):
                    item = lw.item(i)
                    if item.checkState() == Qt.Checked:
                        y_loadcases.append(item.text())
            elif self.form.angular.isChecked():
                loadcases = []
                lw = self.form.angular_specs
                for i in range(lw.count()):
                    item = lw.item(i)
                    if item.checkState() == Qt.Checked:
                        loadcases.append(item.text())
        return x_loadcases, y_loadcases, loadcases

    def reject(self):
        Gui.Control.closeDialog()

    def get_data_for_apply_earthquakes(self, building, d: dict):
        data = civiltools_config.get_data_for_apply_earthquakes_drift(
            building,
            etabs=self.etabs,
            d=d,
        )
        if data is None:
            QMessageBox.warning(
                None, "Not Implemented", "Can not apply earthquake for your systems"
            )
            return None
        return data
