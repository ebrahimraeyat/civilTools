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
        index = self.form.tabwidget.currentIndex()
        tab_text = self.form.tabwidget.tabText(index)
        self.etabs.unlock_model()
        if tab_text in ('Beams', 'Columns'):
            if tab_text == 'Beams':
                if len(beams) == 0:
                    QMessageBox.warning(None, "Not Beams", 'Can not find any Beams in this model!')
                    return
                modifiers = self.get_beam_modifiers()
                if selected_obj_only:
                    names = set(selections).intersection(beams)
                else:
                    names = beams
            
            elif tab_text == 'Columns':
                if len(columns) == 0:
                    QMessageBox.warning(None, "Not Columns", 'Can not find any Columns in this model!')
                    return
                if selected_obj_only:
                    names = set(selections).intersection(columns)
                else:
                    names = columns
                modifiers = self.get_column_modifiers()
            self.etabs.frame_obj.assign_frame_modifiers(
                names,
                *modifiers,
            )
        elif tab_text == 'Slabs':
            reset_section_modifiers = self.form.reset_section_modifiers.isChecked()
            if selected_obj_only:
                names = self.etabs.select_obj.get_selected_floors()
            else:
                names = self.etabs.area.get_slab_names()
            modifiers = self.get_slab_modifiers()
            self.etabs.area.assign_slab_modifiers(
                names,
                *modifiers,
                reset=reset_section_modifiers,
            )
        QMessageBox.information(
            None,
            'Successfull',
            f'Successfully Applied {len(names)} Modifiers to {self.etabs.get_filename()} Model.',
        )
    
    def apply_to_etabs_all(self):
        selected_obj_only = self.form.selected_obj.isChecked()
        beams, columns = self.etabs.frame_obj.get_beams_columns()
        selections = self.etabs.select_obj.get_selected_obj_type(n=2)
        # Beams
        if selected_obj_only:
            names = set(selections).intersection(beams)
        else:
            names = beams
        self.etabs.unlock_model()
        if names:
            modifiers = self.get_beam_modifiers()
            self.etabs.frame_obj.assign_frame_modifiers(
                names,
                *modifiers,
            )
        # Columns
        if selected_obj_only:
            names = set(selections).intersection(columns)
        else:
            names = columns
        if names:
            modifiers = self.get_column_modifiers()
            self.etabs.frame_obj.assign_frame_modifiers(
                names,
                *modifiers,
            )
        # Slabs
        reset_section_modifiers = self.form.reset_section_modifiers.isChecked()
        if selected_obj_only:
            names = self.etabs.select_obj.get_selected_floors()
        else:
            names = self.etabs.area.get_slab_names()
        modifiers = self.get_slab_modifiers()
        self.etabs.area.assign_slab_modifiers(
            names,
            *modifiers,
            reset=reset_section_modifiers,
        )
        QMessageBox.information(
            None,
            'Successfull',
            f'Successfully Applied All Modifiers to {self.etabs.get_filename()} Model.',
        )
        
    def get_beam_modifiers(self):
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
        return modifiers
    
    def get_column_modifiers(self):
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
        return modifiers
    
    def get_slab_modifiers(self):
        modifiers = [
            self.form.slabs_f11_spinbox.value() if self.form.slabs_f11_checkbox.isChecked() else None,
            self.form.slabs_f22_spinbox.value() if self.form.slabs_f22_checkbox.isChecked() else None,
            self.form.slabs_f12_spinbox.value() if self.form.slabs_f12_checkbox.isChecked() else None,
            self.form.slabs_m11_spinbox.value() if self.form.slabs_m11_checkbox.isChecked() else None,
            self.form.slabs_m22_spinbox.value() if self.form.slabs_m22_checkbox.isChecked() else None,
            self.form.slabs_m12_spinbox.value() if self.form.slabs_m12_checkbox.isChecked() else None,
            self.form.slabs_v13_spinbox.value() if self.form.slabs_v13_checkbox.isChecked() else None,
            self.form.slabs_v23_spinbox.value() if self.form.slabs_v23_checkbox.isChecked() else None,
            self.form.slabs_mass_spinbox.value() if self.form.slabs_mass_checkbox.isChecked() else None,
            self.form.slabs_weight_spinbox.value() if self.form.slabs_weight_checkbox.isChecked() else None,
        ]
        return modifiers
    
    def create_connections(self):
        self.form.apply_to_etabs_button.clicked.connect(self.apply_to_etabs)
        self.form.apply_to_etabs_button_all.clicked.connect(self.apply_to_etabs_all)
        self.form.tabwidget.currentChanged.connect(self.tab_changed)
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
        # Slabs
        self.form.slabs_f11_checkbox.stateChanged.connect(self.slabs_f11_checkbox_clicked)
        self.form.slabs_f22_checkbox.stateChanged.connect(self.slabs_f22_checkbox_clicked)
        self.form.slabs_f12_checkbox.stateChanged.connect(self.slabs_f12_checkbox_clicked)
        self.form.slabs_m11_checkbox.stateChanged.connect(self.slabs_m11_checkbox_clicked)
        self.form.slabs_m22_checkbox.stateChanged.connect(self.slabs_m22_checkbox_clicked)
        self.form.slabs_m12_checkbox.stateChanged.connect(self.slabs_m12_checkbox_clicked)
        self.form.slabs_v13_checkbox.stateChanged.connect(self.slabs_v13_checkbox_clicked)
        self.form.slabs_v23_checkbox.stateChanged.connect(self.slabs_v23_checkbox_clicked)
        self.form.slabs_mass_checkbox.stateChanged.connect(self.slabs_mass_checkbox_clicked)
        self.form.slabs_weight_checkbox.stateChanged.connect(self.slabs_weight_checkbox_clicked)
        # mass & weight value check if above 1 or not
        self.form.beam_mass_spinbox.valueChanged.connect(self.set_beam_mass_spinbox_changed)
        self.form.beam_weight_spinbox.valueChanged.connect(self.set_beam_weight_spinbox_changed)

    def set_beam_weight_spinbox_changed(self):
        if self.form.beam_weight_spinbox.value() > 1:
            self.form.beam_weight_spinbox.setSuffix(" Cm")
        else:
            self.form.beam_weight_spinbox.setSuffix("")
            
    def set_beam_mass_spinbox_changed(self):
        if self.form.beam_mass_spinbox.value() > 1:
            self.form.beam_mass_spinbox.setSuffix(" Cm")
        else:
            self.form.beam_mass_spinbox.setSuffix("")

    def tab_changed(self, index: int):
        tab_text = self.form.tabwidget.tabText(index)
        self.form.apply_to_etabs_button.setText(tab_text)

    
    # Slabs
    def slabs_weight_checkbox_clicked(self):
        self.form.slabs_weight_spinbox.setEnabled(self.form.slabs_weight_checkbox.isChecked())
    
    def slabs_mass_checkbox_clicked(self):
        self.form.slabs_mass_spinbox.setEnabled(self.form.slabs_mass_checkbox.isChecked())
    
    def slabs_f11_checkbox_clicked(self):
        self.form.slabs_f11_spinbox.setEnabled(self.form.slabs_f11_checkbox.isChecked())
    
    def slabs_f22_checkbox_clicked(self):
        self.form.slabs_f22_spinbox.setEnabled(self.form.slabs_f22_checkbox.isChecked())
    
    def slabs_f12_checkbox_clicked(self):
        self.form.slabs_f12_spinbox.setEnabled(self.form.slabs_f12_checkbox.isChecked())
    
    def slabs_m11_checkbox_clicked(self):
        self.form.slabs_m11_spinbox.setEnabled(self.form.slabs_m11_checkbox.isChecked())
    
    def slabs_m22_checkbox_clicked(self):
        self.form.slabs_m22_spinbox.setEnabled(self.form.slabs_m22_checkbox.isChecked())
    
    def slabs_m12_checkbox_clicked(self):
        self.form.slabs_m12_spinbox.setEnabled(self.form.slabs_m12_checkbox.isChecked())
    
    def slabs_v13_checkbox_clicked(self):
        self.form.slabs_v13_spinbox.setEnabled(self.form.slabs_v13_checkbox.isChecked())
    
    def slabs_v23_checkbox_clicked(self):
        self.form.slabs_v23_spinbox.setEnabled(self.form.slabs_v23_checkbox.isChecked())

    # columns
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

    # Beams
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

    