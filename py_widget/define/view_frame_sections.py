from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox

import FreeCAD
import FreeCADGui as Gui

from qt_models import table_models
import civiltools_rc


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'view_frame_sections.ui'))
        self.etabs = etabs
        self.fill_form()
        self.create_connections()

    def create_connections(self):
        self.form.columns_tableview.clicked.connect(self.view_column_section)
        self.form.beams_tableview.clicked.connect(self.view_beam_section)
        self.form.export_to_etabs.clicked.connect(self.export_to_etabs)
        self.form.concrete_checkbox.clicked.connect(self.concrete_clicked)

    def concrete_clicked(self):
        if self.form.concrete_checkbox.isChecked():
            self.form.concrete_mats.setEnabled(True)
        else:
            self.form.concrete_mats.setEnabled(False)

    def fill_form(self):
        concretes = self.etabs.material.get_material_of_type(2)
        if concretes:
            self.form.concrete_mats.addItems(concretes)

    def view_column_section(self):
        row = self.form.columns_tableview.currentIndex().row()
        section = self.form.columns_tableview.model().sections[row]
        for obj in FreeCAD.ActiveDocument.Objects:
            if (
                hasattr(obj, 'Proxy') and
                hasattr(obj.Proxy, 'Type') and
                obj.Proxy.Type == "ConcreteColumnSection" and
                obj.Section_Name == section.Section_Name
                ):
                obj.ViewObject.show()
            else:
                obj.ViewObject.hide()
    
    def view_beam_section(self):
        row = self.form.beams_tableview.currentIndex().row()
        section = self.form.beams_tableview.model().sections[row]
        for obj in FreeCAD.ActiveDocument.Objects:
            if (
                hasattr(obj, 'Proxy') and
                hasattr(obj.Proxy, 'Type') and
                obj.Proxy.Type == "ConcreteBeamSection" and
                obj.Section_Name == section.Section_Name
                ):
                obj.ViewObject.show()
            else:
                obj.ViewObject.hide()

    def resize_columns(self, view):
        for column in (
            table_models.NAME,
            table_models.WIDTH,
            table_models.HEIGHT,
            table_models.N,
            table_models.M,
            table_models.TOTAL,
            table_models.RHO,
        ):
            view.resizeColumnToContents(column)

    def export_to_etabs(self):
        i = self.form.tabWidget.currentIndex()
        use_concrete_mat = self.form.concrete_checkbox.isChecked()
        concrete_mat = self.form.concrete_mats.currentText()
        selected_rows = set()
        sections = []
        if i == 0: # columns
            indexes = self.form.columns_tableview.selectedIndexes()
            if indexes:
                for index in indexes:
                    row = index.row()
                    selected_rows.add(row)
                for row in selected_rows:
                    sections.append(self.form.columns_tableview.model().sections[row])
            else:
                sections = self.form.columns_tableview.model().sections
            for section in sections:
                if not use_concrete_mat:
                    concrete_mat = section.Concrete_Name
                self.etabs.prop_frame.create_concrete_column(
                    name = section.Label,
                    concrete = concrete_mat,
                    height = section.H.Value,
                    width = section.B.Value,
                    rebar_mat = section.Longitudinal_Rebar_Name,
                    tie_mat = section.Tie_Bars_Name,
                    cover = section.cover,
                    number_3dir_main_bars = section.N,
                    number_2dir_main_bars = section.M,
                    main_rebar_size = section.rebar_diameters_names[section.Diameter],
                    tie_rebar_size = section.rebar_diameters_names[section.Tie_Bars_d],
                    tie_space = section.Tie_Bars_Space,
                    number_2dir_tie_bars = section.m,
                    number_3dir_tie_bars = section.n,
                    design = True if section.Design_type == 'Design' else False,
                )
        elif i == 1:
            indexes = self.form.beams_tableview.selectedIndexes()
            if indexes:
                for index in indexes:
                    row = index.row()
                    selected_rows.add(row)
                for row in selected_rows:
                    sections.append(self.form.beams_tableview.model().sections[row])
            else:
                sections = self.form.beams_tableview.model().sections
            for section in sections:
                if not use_concrete_mat:
                    concrete_mat = section.Concrete_Name
                self.etabs.prop_frame.create_concrete_beam(
                    name = section.Label,
                    concrete = concrete_mat,
                    height = section.H.Value,
                    width = section.B.Value,
                    rebar_mat = section.Longitudinal_Rebar_Name,
                    tie_mat = section.Tie_Bars_Name,
                    cover = section.cover,
                )
        QMessageBox.information(None, '', f'{len(selected_rows)} Sections Imported into {self.etabs.get_filename()} ETABS Model.')
        
    def reject(self):
        Gui.Control.closeDialog()