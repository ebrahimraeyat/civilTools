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
        map_radio_to_type = {
            self.form.concrete : 'concrete',
            self.form.steel : 'steel',
            self.form.shearwall : 'shearwall',
            self.form.slab : 'slab',
        }
        for radio in map_radio_to_type.keys():
            if radio.isChecked():
                type_ = map_radio_to_type[radio]
        load_combinations = self.etabs.database.get_design_load_combinations(type_=type_)
        self.form.load_combinations_list.clear()
        if load_combinations:
            self.form.load_combinations_list.addItems(load_combinations)
            
    def create_connections(self):
        self.form.concrete.clicked.connect(self.fill_load_combinations)
        self.form.steel.clicked.connect(self.fill_load_combinations)
        self.form.shearwall.clicked.connect(self.fill_load_combinations)
        self.form.slab.clicked.connect(self.fill_load_combinations)
        self.form.create_button.clicked.connect(self.create)
    