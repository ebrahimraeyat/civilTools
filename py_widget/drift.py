from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import Qt

import FreeCADGui as Gui

from exporter import config
from building.build import StructureSystem, Building

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj, json_file):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'drift.ui'))
        self.etabs = etabs_obj
        self.json_file = json_file
        self.fill_xy_loadcase_names()

    def accept(self):
        d = config.load(self.json_file)
        no_of_stories = d['no_of_story_x']
        cdx = d['cdx']
        cdy = d['cdy']
        bot_story = d["bot_x_combo"]
        top_story = d["top_x_combo"]
        create_t_file = self.form.create_t_file_box.isChecked()
        loadcases = []
        for lw in (self.form.x_loadcase_list, self.form.y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                if item.checkState() == Qt.Checked:
                    loadcases.append(item.text())
        if create_t_file:
            tx, ty, _ = self.etabs.get_drift_periods()
            config.save_analytical_periods(self.json_file, tx, ty)
            building = self.current_building(tx, ty)
            self.etabs.apply_cfactor_to_edb(building, bot_story, top_story)
        drifts, headers = self.etabs.get_drifts(no_of_stories, cdx, cdy, loadcases)
        import table_model
        table_model.show_results(drifts, headers, table_model.DriftModel)
    
    def reject(self):
        Gui.Control.closeDialog()

    def current_building(self, tx, ty):
        d = config.load(self.json_file)
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