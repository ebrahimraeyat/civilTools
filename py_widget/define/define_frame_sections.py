from pathlib import Path
import math

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox

import FreeCAD
import FreeCADGui as Gui
# from pivy.coin import SoInput, SoDB
# from pivy.quarter import QuarterWidget
from qt_models import table_models

import civiltools_rc


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'define_frame_sections.ui'))
        self.etabs = etabs_model
        self.fill_form()
        self.task_dialog = None
        # self.beam_names = self.etabs.frame_obj.concrete_section_names('Beam')
        # self.column_names = self.etabs.frame_obj.concrete_section_names('Column')
        # self.other_names = self.etabs.frame_obj.other_sections(self.beam_names + self.column_names)
        # self.fill_sections()
        self.create_connections()
        # self._firstwidget = None

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
        # self.form.single.clicked.connect(self.change_selection_behavior)
        # self.form.multiple.clicked.connect(self.change_selection_behavior)
        self.form.width_add_button.clicked.connect(self.add_width)
        self.form.height_add_button.clicked.connect(self.add_height)
        self.form.add_name_pattern_button.clicked.connect(self.add_pattern)
        self.form.section_pattern_name.textChanged.connect(self.update_section_name)
        self.form.run.clicked.connect(self.accept)
        self.form.longitudinal_bars_mats.lineEdit().editingFinished.connect(self.create_AIII_rebar)
        self.form.tie_bars_mats.lineEdit().editingFinished.connect(self.create_AII_rebar)
        # self.form.columns_tableview.clicked.connect(self.view_section)
        # self.form.columns_tableview.itemSelectionChanged.connect(self.view_section)
        # self.form.beams.clicked.connect(self.fill_sections)
        # self.form.columns.clicked.connect(self.fill_sections)
        # self.form.filter_line.textChanged.connect(self.filter_sections)
        # selection_model = self.form.columns_tableview.selectionModel()
        # selection_model.selectionChanged.connect(self.on_selectionChanged)

    # @QtCore.pyqtSlot('QItemSelection', 'QItemSelection')
    def on_selectionChanged(self, selected, deselected):
        print("selected: ")
        for ix in selected.indexes():
            print(ix.data())

        print("deselected: ")
        for ix in deselected.indexes():
            print(ix.data())
            print(ix.row())

    def change_design_type(self):
        if self.form.column_type.isChecked():
            self.form.beam_column_stacked.setCurrentIndex(0)
            self.form.section_pattern_name.setText("C$WidthX$Height_($NX$M)T$RebarSize")
            self.form.name_pattern_box.clear()
            self.form.name_pattern_box.addItems(
                (
                    "$Width",
                    "$Height",
                    "$TotalRebars",
                    "$RebarSize",
                    "$N",
                    "$M",
                    "$Fc",
                    "$RebarPercentage",
                    ))
        elif self.form.beam_type.isChecked():
            self.form.beam_column_stacked.setCurrentIndex(1)
            self.form.section_pattern_name.setText("B$WidthX$Height")
            self.form.name_pattern_box.clear()
            self.form.name_pattern_box.addItems(
                (
                    "$Width",
                    "$Height",
                    "$Fc",
                    ))

    # def change_selection_behavior(self):
    #     if self.form.single.isChecked():
    #         mode = QAbstractItemView.SingleSelection
    #     elif self.form.multiple.isChecked():
    #         mode = QAbstractItemView.ExtendedSelection
    #     self.form.width_list.setSelectionMode(mode)
    #     self.form.height_list.setSelectionMode(mode)
    #     self.form.main_rebar_size_list.setSelectionMode(mode)
    #     self.form.x_rebar_list.setSelectionMode(mode)
    #     self.form.y_rebar_list.setSelectionMode(mode)
    #     if self.form.single.isChecked():
    #         self.form.width_list.setCurrentRow(3)
    #         self.form.height_list.setCurrentRow(3)
    #         self.form.main_rebar_size_list.setCurrentRow(3)
    #         self.form.x_rebar_list.setCurrentRow(0)
    #         self.form.y_rebar_list.setCurrentRow(1)

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
                                        '$RebarPercentage', f"{rebar_percentage:.2f}"
                                    )
        self.form.section_name.setText(new_text)



    def filter_sections(self):
        text = self.form.filter_line.text()
        for i in range(self.form.sections.count()):
            item = self.form.sections.item(i)
            item.setHidden(not (item.text().__contains__(text)))

    def create_AIII_rebar(self):
        name = self.form.longitudinal_bars_mats.lineEdit().text()
        if QMessageBox.question(None, 'Create AIII Rebar',
            f'Do you want to create {name} Rebar?') == QMessageBox.No:
            return
        self.etabs.material.add_AIII_rebar(name)
    
    def create_AII_rebar(self):
        name = self.form.tie_bars_mats.lineEdit().text()
        if QMessageBox.question(None, 'Create AII Rebar',
            f'Do you want to create {name} Rebar?') == QMessageBox.No:
            return
        self.etabs.material.add_AII_rebar(name)

    def accept(self):
        is_column = self.form.column_type.isChecked()
        is_beam = self.form.beam_type.isChecked()
        if is_column:
            cover = self.form.column_cover.value()
        elif is_beam:
            cover = self.form.beam_cover.value()
        longitudinal_bars_mats = self.form.longitudinal_bars_mats.currentText()
        # from PySide2.QtWidgets import QMessageBox
        # if not longitudinal_bars_mats:
        #     ret = QMessageBox.question(None, 'Create AIII?',
        #     'ETABS Model did not contain AIII rebars, Do you want to add it?')
        #     if ret == QMessageBox.Yes:
        #         pass
        tie_bars_mats = self.form.tie_bars_mats.currentText()
        # if not tie_bars_mats:
        #     ret = QMessageBox.question(None, 'Create AII?',
        #     'ETABS Model did not contain AII rebars, Do you want to add it?')
        #     if ret == QMessageBox.Yes:
        #         pass
        concrete_mat = self.form.concrete_mats.currentText()
        fc = self.etabs.material.get_fc(concrete_mat)
        widths = [int(item.text()) for item in self.form.width_list.selectedItems()]
        heights = [int(item.text()) for item in self.form.height_list.selectedItems()]
        main_rebar_sizes = [item.text() for item in self.form.main_rebar_size_list.selectedItems()]
        x_rebar_numbers = [int(item.text()) for item in self.form.x_rebar_list.selectedItems()]
        y_rebar_numbers = [int(item.text()) for item in self.form.y_rebar_list.selectedItems()]
        check_rebar_percentage = self.form.rebar_percentage.isChecked()
        min_p = self.form.min_p.value()
        max_p = self.form.max_p.value()
        check_rebar_dist = self.form.rebar_clear_distance.isChecked()
        min_rebar_dist = self.form.min_rebar_dist.value()
        max_rebar_dist = self.form.max_rebar_dist.value()
        if self.form.check.isChecked():
            design_type = 'Check'
        elif self.form.design.isChecked():
            design_type = 'Design'
        tie_bar_size = self.form.tie_bar_size.currentText()
        tie_space = self.form.tie_space.value()
        n = self.form.n_2.value()
        m = self.form.m_2.value()
        pattern_name = self.form.section_pattern_name.text()
        main_diameters = []
        for i in range(self.form.main_rebar_size_list.count()):
            item = self.form.main_rebar_size_list.item(i)
            main_diameters.append(item.text())
        tie_diameters = []
        for i in range(self.form.tie_bar_size.count()):
            tie_diameters.append(self.form.tie_bar_size.itemText(i))
        column_sections = []
        beam_sections = []
        current_column_sections = []
        current_beam_sections = []
        current_columns_name = []
        current_beams_name = []
        if not FreeCAD.ActiveDocument:
            FreeCAD.newDocument("Sections")
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, 'Proxy') and obj.Proxy:
                if obj.Proxy.Type == 'ConcreteColumnSection':
                    current_column_sections.append(obj)
                    current_columns_name.append(obj.Label)
                elif obj.Proxy.Type == 'ConcreteBeamSection':
                    current_beam_sections.append(obj)
                    current_beams_name.append(obj.Label)
        if is_column:
            from freecad_obj import sections
            for diameter in main_rebar_sizes:
                for B in widths:
                    for H in heights:
                        for N in x_rebar_numbers:
                            for M in y_rebar_numbers:
                                if B / H < 0.3 or H / B < 0.3:
                                    continue
                                d = int(diameter.rstrip('d'))
                                rebar_area = math.pi * d ** 2 / 4
                                number = 2 * (N + M) - 4
                                p = rebar_area * number / (B * H)
                                if check_rebar_percentage and not (min_p < p < max_p):
                                    continue
                                tie_diameter = int(tie_bar_size.rstrip('d'))
                                c = cover * 10 + tie_diameter + d / 2
                                dist_x = (B * 10 - 2 * c) / (N - 1) - d
                                dist_y = (H * 10 - 2 * c) / (M - 1) - d
                                dist = min(dist_x, dist_y) / 10
                                if check_rebar_dist and not (min_rebar_dist < dist < max_rebar_dist):
                                    continue
                                new_text = pattern_name.replace(
                                    '$Width', str(B)).replace(
                                        '$Height', str(H)).replace(
                                            '$RebarSize', diameter.rstrip('d')).replace(
                                                '$TotalRebars', str(number)).replace(
                                                    '$N', str(N)).replace(
                                                        '$M', str(M)).replace(
                                                            '$Fc', str(fc)).replace(
                                                                '$RebarPercentage', f"{p:.2f}"
                                                            )
                                if new_text in current_columns_name:
                                    continue
                                sec = sections.make_column_section(
                                    B * 10,
                                    H * 10,
                                    N,
                                    M,
                                    diameter,
                                    tie_bar_size,
                                    cover * 10,
                                    main_diameters=main_diameters,
                                    tie_diameters=tie_diameters,
                                    pattern_name=pattern_name,
                                    longitudinal_bar_name=longitudinal_bars_mats,
                                    tie_bar_name=tie_bars_mats,
                                    tie_bar_space=tie_space,
                                    n=n,
                                    m=m,
                                    concrete_name=concrete_mat,
                                    fc=f'{fc} MPa',
                                    design_type=design_type,
                                )
                                column_sections.append(sec)
        elif is_beam:
            from freecad_obj import concrete_beam_section
            for B in widths:
                for H in heights:
                    if B < H / 4:
                        continue
                    new_text = pattern_name.replace(
                        '$Width', str(B)).replace(
                            '$Height', str(H))
                    if new_text in current_beams_name:
                        continue
                    sec = concrete_beam_section.make_beam_section(
                        B * 10,
                        H * 10,
                        cover * 10,
                        pattern_name=pattern_name,
                        longitudinal_bar_name=longitudinal_bars_mats,
                        tie_bar_name=tie_bars_mats,
                        concrete_name=concrete_mat,
                        fc=f'{fc} MPa',
                    )
                    beam_sections.append(sec)
        
        column_sections.extend(current_column_sections)
        beam_sections.extend(current_beam_sections)
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewTop()
        if not Gui.Control.activeDialog():
            from py_widget.define import view_frame_sections
            self.task_dialog = view_frame_sections.Form(self.etabs)
            column_model = table_models.ConcreteColumnSectionTableModel(sections=column_sections)
            self.task_dialog.form.columns_tableview.setModel(column_model)

            beam_model = table_models.ConcreteBeamSectionTableModel(sections=beam_sections)
            self.task_dialog.form.beams_tableview.setModel(beam_model)
            # from freecad_funcs import add_dock_widget
            # add_dock_widget(self.task_dialog.form, 'civiltools_concrete_sections', 'sections')
            Gui.Control.showDialog(self.task_dialog)
        else:
            self.task_dialog.form.columns_tableview.model().beginResetModel()
            self.task_dialog.form.columns_tableview.model().sections=column_sections
            self.task_dialog.form.columns_tableview.model().endResetModel()
            self.task_dialog.form.beams_tableview.model().beginResetModel()
            self.task_dialog.form.beams_tableview.model().sections=beam_sections
            self.task_dialog.form.beams_tableview.model().endResetModel()
        
        for column in (
            table_models.NAME,
            table_models.WIDTH,
            table_models.HEIGHT,
            table_models.N,
            table_models.M,
            table_models.TOTAL,
            table_models.RHO,
        ):
            self.task_dialog.form.columns_tableview.resizeColumnToContents(column)
        for column in (
            table_models.NAME,
            table_models.WIDTH,
            table_models.HEIGHT,
        ):
            self.task_dialog.form.beams_tableview.resizeColumnToContents(column)

    def reject(self):
        Gui.Control.closeDialog()



 
# class MdiQuarterWidget(QuarterWidget):
#     def __init__(self, parent, sharewidget):
#         QuarterWidget.__init__(self, parent=parent, sharewidget=sharewidget)
 
    # def loadFile(self, filename):
    #     in_ = SoInput()
    #     if (in_.openFile(str(filename.toLatin1()))):
    #         root = SoDB.readAll(in_)
    #     if (root):
    #         self.setSceneGraph(root)
    #         self.currentfile = filename
    #         self.setWindowTitle(filename)
    #         return True
    #     return False
 
    # def currentFile(self):
    #     return self.currentfile
 
    # def minimumSizeHint(self):
    #     return QtCore.QSize(640, 480)