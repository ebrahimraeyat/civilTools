from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui

import create_f2k


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'load_combinations_to_f2k.ui'))
        self.etabs = etabs_model
        # filename = Path(self.etabs.SapModel.GetModelFilename()).with_suffix('.F2k')
        # self.form.filename.setText(str(filename))
        self.fill_load_combinations()
        self.create_connections()
    
    def add_to_f2k(self):
        load_combinations = []
        for i in range(self.form.load_combinations_list.count()):
            item = self.form.load_combinations_list.item(i)
            if item.isSelected():
                load_combinations.append(item.text())
        if not load_combinations:
            return
        filename = self.form.filename.text()
        if not filename:
            QMessageBox.warning(None, 'Select File', f'Please select input F2k file.')
            return

        if filename and not Path(filename).exists():
            QMessageBox.warning(None, 'Wrong File', f'Safe F2K file {filename} did not exist.')
            return

        f2k = create_f2k.CreateF2kFile(
            input_f2k=filename,
            etabs=self.etabs,
            append=True,
            )
        f2k.add_load_combinations(load_combinations=load_combinations)
        f2k.write()
        QMessageBox.information(None, 'Successfull',f'Successfully written to {filename} file.')

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
        self.form.add_to_f2k_button.clicked.connect(self.add_to_f2k)
        self.form.browse.clicked.connect(self.browse)

    def reject(self):
        Gui.Control.closeDialog()

    def browse(self):
        ext = '.f2k'
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getOpenFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        self.form.filename.setText(filename)
    