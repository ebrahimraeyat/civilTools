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
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'drift.ui'))
        self.etabs = etabs_obj
        self.dynamic_tab_clicked = False
        self.fill_xy_loadcase_names()
        self.create_connections()
        self.load_config()
    
    def create_connections(self):
        self.form.run.clicked.connect(self.accept)
        self.form.tab_widget.currentChanged.connect(self.tab_changed)
        self.form.create_t_file_box.clicked.connect(self.create_t_file_clicked)

    def create_t_file_clicked(self, check):
        self.form.structuretype_groupbox.setEnabled(check)

    def load_config(self):
        civiltools_config.load(self.etabs, self.form)

    def tab_changed(self, index: int):
        if index == 1 and not self.dynamic_tab_clicked:
            self.fill_dynamic_xy_loadcase_names()
            self.dynamic_tab_clicked = True

    def fill_dynamic_xy_loadcase_names(self):
        x_specs, y_specs = self.etabs.load_cases.get_response_spectrum_xy_loadcases_names()
        self.form.dynamic_x_loadcase_list.addItems(x_specs)
        self.form.dynamic_y_loadcase_list.addItems(y_specs)
        for lw in (self.form.dynamic_x_loadcase_list, self.form.dynamic_y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)

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
            self.form.dynamic_x_loadcase_list.setEnabled(True)
            self.form.dynamic_y_loadcase_list.setEnabled(True)
        elif self.form.angular.isChecked():
            self.form.angular_specs.setEnabled(True)
            self.form.dynamic_x_loadcase_list.setEnabled(False)
            self.form.dynamic_y_loadcase_list.setEnabled(False)

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
        if create_t_file:
            if structure_type == 'steel':
                tx, ty, main_file = self.etabs.get_drift_periods(open_main_file=False)
            else:
                tx, ty, _ = self.etabs.get_drift_periods(open_main_file=True)
            civiltools_config.save_analytical_periods(self.etabs, tx, ty)
            building = self.current_building(tx, ty)
            bot_story = d["bot_x_combo"]
            top_story = d["top_x_combo"]
            two_system = d['activate_second_system']
            if two_system:
                top_story = d["top_x1_combo"]
                if building.x_system2.Ru >= building.x_system.Ru:
                    cdx = building.x_system2.cd
                if building.y_system2.Ru >= building.y_system.Ru:
                    cdy = building.y_system2.cd
            self.etabs.apply_cfactor_to_edb(building, bot_story, top_story)
            if tab == 1:
                # execute scale response spectrum
                import find_etabs
                from py_widget import response_spectrum
                win = response_spectrum.Form(self.etabs, show_message=False)
                find_etabs.show_win(win, in_mdi=False)
        # For two systems that not ticks the create t file, Temporary
        else:
            two_system = d['activate_second_system']
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
                    building = self.current_building(4, 4)
                    if building.x_system2.Ru >= building.x_system.Ru:
                        cdx = building.x_system2.cd
                    if building.y_system2.Ru >= building.y_system.Ru:
                        cdy = building.y_system2.cd
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
        if ret is None:
            QMessageBox.warning(None,
                                'Diphragm',
                                'Please Check that you assigned diaphragm to stories.')
            return
        import table_model
        df = pd.DataFrame(ret[0], columns=ret[1])
        table_model.show_results(df, table_model.DriftModel)
        self.form.close()

    def get_load_cases(self, tab):
        x_loadcases = []
        y_loadcases = []
        loadcases = []

        if tab == 0:
            lw = self.form.x_loadcase_list
            for i in range(lw.count()):
                item = lw.item(i)
                if item.checkState() == Qt.Checked:
                    x_loadcases.append(item.text())
            lw = self.form.y_loadcase_list
            for i in range(lw.count()):
                item = lw.item(i)
                if item.checkState() == Qt.Checked:
                    y_loadcases.append(item.text())
        elif tab == 1:
            if self.form.xy.isChecked():
                lw = self.form.dynamic_x_loadcase_list
                for i in range(lw.count()):
                    item = lw.item(i)
                    if item.checkState() == Qt.Checked:
                        x_loadcases.append(item.text())
                lw = self.form.dynamic_y_loadcase_list
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

    def current_building(self, tx, ty):
        d = civiltools_config.load(self.etabs)
        risk_level = d['risk_level']
        importance_factor = float(d['importance_factor'])
        soil = d['soil_type']
        city = d['city']
        two_system = d['activate_second_system']
        if two_system:
            height_x1 = d['height_x1']
            noStory1 = d['no_of_story_x1']
            xSystemType1 = d['x_system_name_1']
            xLateralType1 = d['x_lateral_name_1']
            ySystemType1 = d['y_system_name_1']
            yLateralType1 = d['y_lateral_name_1']
            is_infill1= d['infill_1']
            xSystem1 = StructureSystem(xSystemType1, xLateralType1, "X")
            ySystem1 = StructureSystem(ySystemType1, yLateralType1, "Y")
        else:
            xSystem1 = None
            ySystem1 = None
            height_x1 = 0
            is_infill1 = False
        #     if 
        #     no_of_stories = d['no_of_story_x'] + d['no_of_story_x1']
        height_x = d['height_x']
        noStory = d['no_of_story_x']
        xSystemType = d['x_system_name']
        xLateralType = d['x_lateral_name']
        ySystemType = d['y_system_name']
        yLateralType = d['y_lateral_name']
        is_infill = d['infill']
        xSystem = StructureSystem(xSystemType, xLateralType, "X")
        ySystem = StructureSystem(ySystemType, yLateralType, "Y")
        build = Building(
                    risk_level,
                    importance_factor,
                    soil,
                    noStory,
                    height_x,
                    is_infill,
                    xSystem,
                    ySystem,
                    city,
                    tx,
                    ty,
                    xSystem1,
                    ySystem1,
                    height_x1,
                    is_infill1,
                    )
        return build


    def fill_xy_loadcase_names(self):
        x_names, y_names = self.etabs.load_cases.get_xy_seismic_load_cases()
        drift_load_cases = self.etabs.load_cases.get_seismic_drift_load_cases()
        self.form.x_loadcase_list.addItems(x_names)
        self.form.y_loadcase_list.addItems(y_names)
        for lw in (self.form.x_loadcase_list, self.form.y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
        for name in drift_load_cases:
            matching_items = []
            if name in x_names:
                matching_items = self.form.x_loadcase_list.findItems(name, Qt.MatchExactly)
            elif name in y_names:
                matching_items = self.form.y_loadcase_list.findItems(name, Qt.MatchExactly)
            for item in matching_items:
                item.setCheckState(Qt.Checked)