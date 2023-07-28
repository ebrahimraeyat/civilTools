from pathlib import Path

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
        self.fill_xy_loadcase_names()
        self.fill_dynamic_xy_loadcase_names()
        self.create_connections()
    
    def create_connections(self):
        self.form.xy.clicked.connect(self.reset_widget)
        self.form.run.clicked.connect(self.accept)
        # self.form.angular.clicked.connect(self.reset_widget)
        # self.form.angular.clicked.connect(self.fill_angular_fields)

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
        no_of_stories = d['no_of_story_x']
        cdx = d['cdx']
        cdy = d['cdy']
        bot_story = d["bot_x_combo"]
        top_story = d["top_x_combo"]
        x_loadcases = []
        y_loadcases = []

        tab = self.form.tabWidget.currentIndex()
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
        create_t_file = self.form.create_t_file_box.isChecked()
        if create_t_file:
            structure_type = self.etabs.get_type_of_structure()
            if structure_type == 'steel':
                tx, ty, main_file = self.etabs.get_drift_periods(open_main_file=False)
            else:
                tx, ty, _ = self.etabs.get_drift_periods(open_main_file=True)
            civiltools_config.save_analytical_periods(self.etabs, tx, ty)
            building = self.current_building(tx, ty)
            self.etabs.apply_cfactor_to_edb(building, bot_story, top_story)
            # execute scale response spectrum
            if tab == 1:
                import find_etabs
                from py_widget import response_spectrum
                win = response_spectrum.Form(self.etabs, show_message=False)
                find_etabs.show_win(win, in_mdi=False)
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
        drifts, headers = ret
        import table_model
        table_model.show_results(drifts, headers, table_model.DriftModel)
        self.form.close()
    
    def reject(self):
        Gui.Control.closeDialog()

    def current_building(self, tx, ty):
        d = civiltools_config.load(self.etabs)
        risk_level = d['risk_level']
        height_x = d['height_x']
        importance_factor = float(d['importance_factor'])
        soil = d['soil_type']
        city = d['city']
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