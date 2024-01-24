from pathlib import Path

import pandas as pd

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import Qt

import FreeCADGui as Gui

from exporter import civiltools_config
from building.build import StructureSystem, Building

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'drift.ui'))
        self.etabs = etabs_obj
        self.dynamic_tab_clicked = False
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
        d = civiltools_config.get_settings_from_etabs(self.etabs)
        tab = self.form.tab_widget.currentIndex()
        create_t_file = self.form.create_t_file_box.isChecked()
        structure_type = 'concrete'
        if self.form.steel_radiobutton.isChecked():
            structure_type = 'steel'
        #     no_of_stories = d['no_of_story_x'] + d['no_of_story_x1']
        no_of_stories = d['no_of_story_x']
        cdx = d['cdx']
        cdy = d['cdy']
        two_system = d.get('activate_second_system', False)
        if create_t_file:
            self.etabs.unlock_model()
            tx, ty, main_file = self.etabs.get_drift_periods(structure_type=structure_type)
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
                ex_name = d.get('ex_combobox')
                ey_name = d.get('ey_combobox')
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
                rux = d.get('Rux', None)
                if rux:
                    ruy = d.get('Ruy', None)
                    rux1 = d.get('Rux1', None)
                    ruy1 = d.get('Ruy1', None)
                    if rux1 >= rux:
                        cdx = d.get('cdx1')
                    if ruy1 >= ruy:
                        cdy = d.get('cdy1')
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
        if create_t_file and structure_type == 'steel':
            print(f"Opening file {main_file}\n")
            self.etabs.SapModel.File.OpenFile(str(main_file))
            data = self.get_data_for_apply_earthquakes(building, d)
            self.etabs.apply_cfactors_to_edb(data, d=d)
        if ret is None:
            QMessageBox.warning(None,
                                'Diphragm',
                                'Please Check that you assigned diaphragm to stories.')
            return
        import table_model
        df = pd.DataFrame(ret[0], columns=ret[1])
        if self.form.show_separate_checkbox.isChecked():
            filt = df['OutputCase'].isin(x_loadcases)
            df1 = df.loc[filt]
            table_model.show_results(df1, table_model.DriftModel)
            filt = df['OutputCase'].isin(y_loadcases)
            df1 = df.loc[filt]
            table_model.show_results(df1, table_model.DriftModel)
        else:
            table_model.show_results(df, table_model.DriftModel)
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
        bot_1, top_1, bot_2, top_2 = self.etabs.get_top_bot_stories(d)
        # get bottom system data
        first_system_seismic = self.etabs.get_first_system_seismic_drift(d)
        cx_1, cy_1 = building.results_drift[1:]
        kx_1, ky_1 = building.kx_drift, building.ky_drift
        data = []
        # Check if second system is active
        if d.get('activate_second_system', False):
            # get top system data
            second_system_seismic = self.etabs.get_second_system_seismic_drift(d)
            cx_2, cy_2 = building.building2.results_drift[1:]
            kx_2, ky_2 = building.building2.kx_drift, building.building2.ky_drift
            # Special case with Ru_bot = Ru_top
            if d.get('special_case', False) and \
            building.x_system.Ru == building.building2.x_system.Ru and \
            building.y_system.Ru == building.building2.y_system.Ru:
                # get bottom system data
                data.append((first_system_seismic[:3], [top_1, bot_1, str(cx_1), str(kx_1)]))
                data.append((first_system_seismic[3:], [top_1, bot_1, str(cy_1), str(ky_1)]))
                # get top system data
                data.append((second_system_seismic[:3], [top_2, bot_2, str(cx_2), str(kx_2)]))
                data.append((second_system_seismic[3:], [top_2, bot_2, str(cy_2), str(ky_2)]))
            # case B, Ru_bot >= Ru_top
            elif building.x_system.Ru >= building.building2.x_system.Ru and \
            building.y_system.Ru >= building.building2.y_system.Ru:
                cx_all, cy_all = building.results_drift_all_top[1:]
                kx_all, ky_all = building.kx_drift_all, building.ky_drift_all
                data.append((first_system_seismic[:3], [top_2, bot_1, str(cx_all), str(kx_all)]))
                data.append((first_system_seismic[3:], [top_2, bot_1, str(cy_all), str(ky_all)]))
            else:
                QMessageBox.warning(None, "Not Implemented", "Can not apply earthquake for your systems")
                return None
        else:
            # get bottom system data
            data.append((first_system_seismic[:3], [top_1, bot_1, str(cx_1), str(kx_1)]))
            data.append((first_system_seismic[3:], [top_1, bot_1, str(cy_1), str(ky_1)]))
        return data