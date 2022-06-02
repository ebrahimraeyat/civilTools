from pathlib import Path
import math

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QAbstractItemView
from PySide2.QtCore import QAbstractTableModel

import FreeCADGui as Gui

import civiltools_rc


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'define_frame_sections.ui'))
        self.etabs = etabs_model
        self.fill_form()
        # self.beam_names = self.etabs.frame_obj.concrete_section_names('Beam')
        # self.column_names = self.etabs.frame_obj.concrete_section_names('Column')
        # self.other_names = self.etabs.frame_obj.other_sections(self.beam_names + self.column_names)
        # self.fill_sections()
        self.create_connections()

    def fill_form(self):
        s340, s400 = self.etabs.material.get_S340_S400_rebars()
        if s400:
            self.form.longitudinal_bars_mats.addItems(s400)
        if s340:
            self.form.tie_bars_mats.addItems(s340)
        concretes = self.etabs.material.get_material_of_type(2)
        if concretes:
            self.form.concrete_mats.addItems(concretes)
        tie_rebars, main_rebars = self.etabs.material.get_tie_main_rebars()
        if main_rebars:
            self.form.main_rebar_size_list.addItems(main_rebars)
            self.form.main_rebar_size_list.setCurrentRow(0)
        if tie_rebars:
            self.form.tie_bar_size.addItems(tie_rebars)
        self.update_section_name()

    def fill_sections(self):
        self.form.sections.clear()
        if self.form.all_sections.isChecked():
            self.form.sections.addItems(self.other_names)
        elif self.form.beams.isChecked():
            self.form.sections.addItems(self.beam_names)
        elif self.form.columns.isChecked():
            self.form.sections.addItems(self.column_names)


    def create_connections(self):
        self.form.column_type.clicked.connect(self.change_design_type)
        self.form.beam_type.clicked.connect(self.change_design_type)
        self.form.single.clicked.connect(self.change_selection_behavior)
        self.form.multiple.clicked.connect(self.change_selection_behavior)
        self.form.width_add_button.clicked.connect(self.add_width)
        self.form.height_add_button.clicked.connect(self.add_height)
        self.form.add_name_pattern_button.clicked.connect(self.add_pattern)
        self.form.section_pattern_name.textChanged.connect(self.update_section_name)
        # self.form.beams.clicked.connect(self.fill_sections)
        # self.form.columns.clicked.connect(self.fill_sections)
        # self.form.filter_line.textChanged.connect(self.filter_sections)

    def change_design_type(self):
        if self.form.column_type.isChecked():
            self.form.beam_column_stacked.setCurrentIndex(0)
        elif self.form.beam_type.isChecked():
            self.form.beam_column_stacked.setCurrentIndex(1)

    def change_selection_behavior(self):
        if self.form.single.isChecked():
            mode = QAbstractItemView.SingleSelection
        elif self.form.multiple.isChecked():
            mode = QAbstractItemView.ExtendedSelection
        self.form.width_list.setSelectionMode(mode)
        self.form.height_list.setSelectionMode(mode)
        self.form.main_rebar_size_list.setSelectionMode(mode)
        self.form.x_rebar_list.setSelectionMode(mode)
        self.form.y_rebar_list.setSelectionMode(mode)
        if self.form.single.isChecked():
            self.form.width_list.setCurrentRow(3)
            self.form.height_list.setCurrentRow(3)
            self.form.main_rebar_size_list.setCurrentRow(3)
            self.form.x_rebar_list.setCurrentRow(0)
            self.form.y_rebar_list.setCurrentRow(1)

    def add_width(self):
        width = self.form.dimension.value()
        for i in range(self.form.width_list.count()):
            item = self.form.width_list.item(i)
            if float(item.text()) == width:
                return
        self.form.width_list.addItem(str(width))
    
    def add_height(self):
        width = self.form.dimension.value()
        for i in range(self.form.height_list.count()):
            item = self.form.height_list.item(i)
            if float(item.text()) == width:
                return
        self.form.height_list.addItem(str(width))

    def add_pattern(self):
        pattern = self.form.name_pattern_box.currentText()
        i = self.form.section_pattern_name.cursorPosition()
        text = self.form.section_pattern_name.text()
        if text:
            new_text = text[0: i] + pattern + text[i:]
        else:
            new_text = pattern
        self.form.section_pattern_name.setText(new_text)

    def update_section_name(self, text=None):
        if text is None:
            text = self.form.section_pattern_name.text()
        width = self.form.width_list.currentItem().text()
        height = self.form.height_list.currentItem().text()
        main_rebar = self.form.main_rebar_size_list.currentItem().text().rstrip('d')
        N = self.form.x_rebar_list.currentItem().text()
        M = self.form.y_rebar_list.currentItem().text()
        conc = self.form.concrete_mats.currentText()
        fc = int(self.etabs.material.get_fc(conc))
        total_rebar = 2 * (int(N) + int(M)) - 4
        rebar_area = math.pi * int(main_rebar) ** 2 / 4
        rebar_percentage = rebar_area * total_rebar / (float(width) * float(height)) / 100
        new_text = text.replace(
            '$Width', width).replace(
                '$Height', height).replace(
                    '$RebarSize', main_rebar).replace(
                        '$TotalRebars', str(total_rebar)).replace(
                            '$N', str(N)).replace(
                                '$M', str(M)).replace(
                                    '$Fc', str(fc)).replace(
                                        '$RebarPercentage', f"{rebar_percentage:.1f}"
                                    )
        self.form.section_name.setText(new_text)



    def filter_sections(self):
        text = self.form.filter_line.text()
        for i in range(self.form.sections.count()):
            item = self.form.sections.item(i)
            item.setHidden(not (item.text().__contains__(text)))

    def accept(self):
        stories = [item.text() for item in self.form.stories.selectedItems()]
        sec_name = self.form.sections.currentItem().text()
        sec_type = 'other'
        if self.form.beams.isChecked():
            sec_type = 'beam'
        elif self.form.columns.isChecked():
            sec_type = 'column'
        self.etabs.frame_obj.assign_sections_stories(
            sec_name = sec_name,
            stories = stories,
            frame_names = None,
            sec_type = sec_type,
            )

    def reject(self):
        Gui.Control.closeDialog()


