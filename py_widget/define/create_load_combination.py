from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'create_load_combination.ui'))
        self.etabs = etabs_model
        self.fill_load_combinations()
        self.create_connections()
    
    def create(self):
        load_combinations = []
        for i in range(self.form.load_combinations_list.count()):
            item = self.form.load_combinations_list.item(i)
            if item.isSelected():
                load_combinations.append(item.text())
        if not load_combinations:
            return
        scale_factor = self.form.scale_factor.value()
        name = self.form.combo_name.text()
        self.etabs.load_combinations.add_load_combination(
            combo_name=name,
            load_case_names=load_combinations,
            scale_factor=scale_factor,
            type_=1,
            )
        QMessageBox.information(None, 'Successfull','Successfully written to etabs file.')

    def fill_load_combinations(self):
        map_radio_to_load_type = {
            self.form.all_load_type : 'ALL',
            self.form.seismic_load_type : 'SEISMIC',
            self.form.gravity_load_type : 'GRAVITY',
        }
        for radio in map_radio_to_load_type.keys():
            if radio.isChecked():
                load_type = map_radio_to_load_type[radio]
        load_combinations = self.etabs.load_combinations.get_load_combinations_of_type(load_type)
        if self.form.design_type_group.isChecked():
            map_radio_to_design_type = {
                self.form.concrete_design_type : 'concrete',
                self.form.steel_design_type : 'steel',
                self.form.shearwall_design_type : 'shearwall',
                self.form.slab_design_type : 'slab',
            }
            for radio in map_radio_to_design_type.keys():
                if radio.isChecked():
                    type_ = map_radio_to_design_type[radio]
            load_combinations_from_design_type = self.etabs.database.get_design_load_combinations(type_=type_)
            if load_combinations_from_design_type is None:
                load_combinations_from_design_type = []
            load_combinations = set(load_combinations).intersection(load_combinations_from_design_type)
        self.form.load_combinations_list.clear()
        if load_combinations:
            self.form.load_combinations_list.addItems(load_combinations)
            
    def create_connections(self):
        self.form.concrete_design_type.clicked.connect(self.fill_load_combinations)
        self.form.steel_design_type.clicked.connect(self.fill_load_combinations)
        self.form.shearwall_design_type.clicked.connect(self.fill_load_combinations)
        self.form.slab_design_type.clicked.connect(self.fill_load_combinations)
        self.form.design_type_group.clicked.connect(self.fill_load_combinations)

        self.form.all_load_type.clicked.connect(self.fill_load_combinations)
        self.form.seismic_load_type.clicked.connect(self.fill_load_combinations)
        self.form.gravity_load_type.clicked.connect(self.fill_load_combinations)
        self.form.seismic_load_type.clicked.connect(self.set_load_combo)
        self.form.gravity_load_type.clicked.connect(self.set_load_combo)
        self.form.create_button.clicked.connect(self.create)

    def set_load_combo(self):
        if self.form.seismic_load_type.isChecked():
            self.form.combo_name.setText("PUSH_SEISMIC")
        elif self.form.gravity_load_type.isChecked():
            self.form.combo_name.setText("PUSH_GRAV")
    