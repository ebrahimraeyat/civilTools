from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui


civiltools_path = Path(__file__).absolute().parent.parent.parent

class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'assign' / 'assign_modifiers.ui'))
        self.etabs = etabs_model
        self.create_connections()

    def apply_to_etabs(self):
        selected_obj_only = self.form.selected_obj.isChecked()
        beams, columns = self.etabs.frame_obj.get_beams_columns()
        selections = self.etabs.select_obj.get_selected_obj_type(n=2)
        if self.form.tabwidget.currentIndex() == 0: # beams
            if len(beams) == 0:
                QMessageBox.warning(None, "Not Beams", 'Can not find any Beams in this model!')
                return
            if selected_obj_only:
                names = set(selections).intersection(beams)
            else:
                names = beams
            modifiers = [
                self.form.beam_area_spinbox.value() if self.form.beam_area_checkbox.isChecked() else None,
                self.form.beam_as2_spinbox.value() if self.form.beam_as2_checkbox.isChecked() else None,
                self.form.beam_as3_spinbox.value() if self.form.beam_as3_checkbox.isChecked() else None,
                self.form.beam_torsion_spinbox.value() if self.form.beam_torsion_checkbox.isChecked() else None,
                self.form.beam_i22_spinbox.value() if self.form.beam_i22_checkbox.isChecked() else None,
                self.form.beam_i33_spinbox.value() if self.form.beam_i33_checkbox.isChecked() else None,
                self.form.beam_mass_spinbox.value() if self.form.beam_mass_checkbox.isChecked() else None,
                self.form.beam_weight_spinbox.value() if self.form.beam_weight_checkbox.isChecked() else None,
            ]
        
        elif self.form.tabwidget.currentIndex() == 1: # columns
            if len(columns) == 0:
                QMessageBox.warning(None, "Not Columns", 'Can not find any Columns in this model!')
                return
            if selected_obj_only:
                names = set(selections).intersection(columns)
            else:
                names = columns
            modifiers = [
                self.form.column_area_spinbox.value() if self.form.column_area_checkbox.isChecked() else None,
                self.form.column_as2_spinbox.value() if self.form.column_as2_checkbox.isChecked() else None,
                self.form.column_as3_spinbox.value() if self.form.column_as3_checkbox.isChecked() else None,
                self.form.column_torsion_spinbox.value() if self.form.column_torsion_checkbox.isChecked() else None,
                self.form.column_i22_spinbox.value() if self.form.column_i22_checkbox.isChecked() else None,
                self.form.column_i33_spinbox.value() if self.form.column_i33_checkbox.isChecked() else None,
                self.form.column_mass_spinbox.value() if self.form.column_mass_checkbox.isChecked() else None,
                self.form.column_weight_spinbox.value() if self.form.column_weight_checkbox.isChecked() else None,
            ]
        # frames = self.etabs.select_obj.get_selected_obj_type(2)
        self.etabs.unlock_model()
        self.etabs.frame_obj.assign_frame_modifires(
            names,
            *modifiers,
        )
        QMessageBox.information(
            None,
            'Successfull',
            f'Successfully Apply {len(names)} Modifiers to {self.etabs.get_filename()} Model.',
        )
        # self.reject()
            
    def create_connections(self):
        self.form.apply_to_etabs_button.clicked.connect(self.apply_to_etabs)
        self.form.cancel_button.clicked.connect(self.reject)
        # Beams
        self.form.beam_area_checkbox.stateChanged.connect(self.beam_area_checkbox_clicked)
        self.form.beam_as2_checkbox.stateChanged.connect(self.beam_as2_checkbox_clicked)
        self.form.beam_as3_checkbox.stateChanged.connect(self.beam_as3_checkbox_clicked)
        self.form.beam_torsion_checkbox.stateChanged.connect(self.beam_torsion_checkbox_clicked)
        self.form.beam_i22_checkbox.stateChanged.connect(self.beam_i22_checkbox_clicked)
        self.form.beam_i33_checkbox.stateChanged.connect(self.beam_i33_checkbox_clicked)
        self.form.beam_mass_checkbox.stateChanged.connect(self.beam_mass_checkbox_clicked)
        self.form.beam_weight_checkbox.stateChanged.connect(self.beam_weight_checkbox_clicked)
        # Columns
        self.form.column_area_checkbox.stateChanged.connect(self.column_area_checkbox_clicked)
        self.form.column_as2_checkbox.stateChanged.connect(self.column_as2_checkbox_clicked)
        self.form.column_as3_checkbox.stateChanged.connect(self.column_as3_checkbox_clicked)
        self.form.column_torsion_checkbox.stateChanged.connect(self.column_torsion_checkbox_clicked)
        self.form.column_i22_checkbox.stateChanged.connect(self.column_i22_checkbox_clicked)
        self.form.column_i33_checkbox.stateChanged.connect(self.column_i33_checkbox_clicked)
        self.form.column_mass_checkbox.stateChanged.connect(self.column_mass_checkbox_clicked)
        self.form.column_weight_checkbox.stateChanged.connect(self.column_weight_checkbox_clicked)

    def column_weight_checkbox_clicked(self):
        self.form.column_weight_spinbox.setEnabled(self.form.column_weight_checkbox.isChecked())
    
    def column_mass_checkbox_clicked(self):
        self.form.column_mass_spinbox.setEnabled(self.form.column_mass_checkbox.isChecked())
    
    def column_i33_checkbox_clicked(self):
        self.form.column_i33_spinbox.setEnabled(self.form.column_i33_checkbox.isChecked())
    
    def column_i22_checkbox_clicked(self):
        self.form.column_i22_spinbox.setEnabled(self.form.column_i22_checkbox.isChecked())

    def column_torsion_checkbox_clicked(self):
        self.form.column_torsion_spinbox.setEnabled(self.form.column_torsion_checkbox.isChecked())

    def column_as3_checkbox_clicked(self):
        self.form.column_as3_spinbox.setEnabled(self.form.column_as3_checkbox.isChecked())
    
    def column_as2_checkbox_clicked(self):
        self.form.column_as2_spinbox.setEnabled(self.form.column_as2_checkbox.isChecked())

    def column_area_checkbox_clicked(self):
        self.form.column_area_spinbox.setEnabled(self.form.column_area_checkbox.isChecked())

    def beam_weight_checkbox_clicked(self):
        self.form.beam_weight_spinbox.setEnabled(self.form.beam_weight_checkbox.isChecked())
    
    def beam_mass_checkbox_clicked(self):
        self.form.beam_mass_spinbox.setEnabled(self.form.beam_mass_checkbox.isChecked())
    
    def beam_i33_checkbox_clicked(self):
        self.form.beam_i33_spinbox.setEnabled(self.form.beam_i33_checkbox.isChecked())
    
    def beam_i22_checkbox_clicked(self):
        self.form.beam_i22_spinbox.setEnabled(self.form.beam_i22_checkbox.isChecked())

    def beam_torsion_checkbox_clicked(self):
        self.form.beam_torsion_spinbox.setEnabled(self.form.beam_torsion_checkbox.isChecked())

    def beam_as3_checkbox_clicked(self):
        self.form.beam_as3_spinbox.setEnabled(self.form.beam_as3_checkbox.isChecked())
    
    def beam_as2_checkbox_clicked(self):
        self.form.beam_as2_spinbox.setEnabled(self.form.beam_as2_checkbox.isChecked())

    def beam_area_checkbox_clicked(self):
        self.form.beam_area_spinbox.setEnabled(self.form.beam_area_checkbox.isChecked())

    def reject(self):
        self.form.close()    

    def getStandardButtons(self):
        return 0

    