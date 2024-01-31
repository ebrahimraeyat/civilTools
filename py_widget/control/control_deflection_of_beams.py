from pathlib import Path
import math

import numpy as np
import pandas as pd

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QMessageBox
from PySide2.QtGui import QPolygonF, QBrush
from PySide2.QtCore import QPointF, QModelIndex, QItemSelection

import FreeCADGui as Gui
import FreeCAD

from design import get_deflection_check_result
import table_model


from exporter import civiltools_config

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self,
    etabs_model,
    beam_names,
    d: dict,
    ):
        '''
        d: dictionary of model properties
        '''
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'control_deflection_of_beams.ui'))
        self.etabs = etabs_model
        self.results = None
        self.main_file_path = None
        self.fill_load_cases()
        self.load_config(beam_names=beam_names, d=d)
        self.create_connections()
        self.scene = QtWidgets.QGraphicsScene()
        self.form.graphicsview.setScene(self.scene)
        self.beam_columns = self.etabs.frame_obj.get_beams_columns_on_stories()

    def load_config(self,
            beam_names: list,
            d: dict,
    ):
        if self.etabs is None:
            return
        try:
            self.etabs.get_filename()
        except:
            return
        civiltools_config.load(self.etabs, self.form, d)
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        live_load_percentage = p.GetFloat('civiltools_live_load_percentage_deflection', 0.25)
        continues_short_term = p.GetInt('continues_short_term_combobox', 1)
        continues_long_term = p.GetInt('continues_long_term_combobox', 0)
        console_short_term = p.GetInt('console_short_term_combobox', 0)
        console_long_term = p.GetInt('console_long_term_combobox', 0)
        self.form.live_percentage_spinbox.setValue(live_load_percentage)
        for combobox, index in zip(
            (self.form.continues_short_term_combobox,
             self.form.continues_long_term_combobox,
             self.form.console_short_term_combobox,
             self.form.console_long_term_combobox,
            ),(
                continues_short_term,
                continues_long_term,
                console_short_term,
                console_long_term,
            )):
            combobox.setCurrentIndex(index)
        self.populate_table(beam_names, d)

    def populate_table(self,
            beam_names: list,
            d: dict,
            ):
        '''
        d : A dictionary of etabs file settings
        '''
        d = d.get('beams_properties', {})
        if d and 'Name' in d.keys(): # for df saved format
            df = pd.DataFrame.from_dict(d)
            current_names = df.Name.unique()
        else:
            df = pd.DataFrame()
            current_names = []
        additional_names = list(set(beam_names).difference(current_names))
        n = len(additional_names)
        if n > 0:
            new_rows = pd.DataFrame({
                'Name': additional_names,
                'Console': [False] * n,
                'Label': [''] * n,
                'Story': [''] * n,
                'Minus Length': [50] * n,
                'Torsion Rebar':[True] * n,
                'Add Rebar': [0] * n,
                'Cover': [6] * n,
                'Width': [40] * n,
                'Height': [50] * n,
                'Result': [''] * n,
            })
            df = df.append(new_rows, ignore_index=True)
            
        def fill_props(row):
            beam_name = row['Name']
            section_name = self.etabs.SapModel.FrameObj.GetSection(beam_name)[0]
            try:
                _, _, h, b, *_ = self.etabs.SapModel.PropFrame.GetRectangle(section_name)
            except:
                h, b = (0, 0)
            label, story, *_ = self.etabs.SapModel.FrameObj.GetLabelFromName(beam_name)
            row['Label'] = label
            row['Story'] = story
            row['Height'] = h
            row['Width'] = b
            return row
            
        units = self.etabs.get_current_unit()
        self.etabs.set_current_unit('kgf', 'cm')
        df = df.apply(fill_props, axis=1)
        self.etabs.set_current_unit(*units)
        filt = df['Name'].isin(beam_names)
        df = df.loc[filt]
        self.result_table = table_model.ResultWidget(
            df,
            model=table_model.BeamDeflectionTableModel,
            function=self.result_table_clicked)
        self.form.table_vertical_layout.insertWidget(0, self.result_table)

    def create_connections(self):
        self.form.check_button.clicked.connect(self.check)
        self.form.cancel_button.clicked.connect(self.reject)
        self.form.help.clicked.connect(self.show_help)
        self.form.create_report_button.clicked.connect(self.create_report)
        self.form.continues_short_term_combobox.currentIndexChanged.connect(self.check_result)
        self.form.continues_long_term_combobox.currentIndexChanged.connect(self.check_result)
        self.form.console_short_term_combobox.currentIndexChanged.connect(self.check_result)
        self.form.console_long_term_combobox.currentIndexChanged.connect(self.check_result)
        # self.form.table_view.selectionModel().selectionChanged.connect(self.row_clicked)

    def result_table_clicked(self, beam_name):
        self.etabs.view.show_frame(beam_name)
        self.draw_beams_columns(beam_name)
        self.check_result()
    
    def check_result(self):
        if self.results is None:
            return
        row, _ = self.result_table.get_current_row_col()
        beam_name = str(self.result_table.model.data(self.result_table.model.index(row, 0)))
        self.form.results.setText(self.results[2][row])
        # check results
        is_console = self.result_table.model.df['Console'].iloc[row]
        ln_str = 'Ln / '
        if is_console:
            short_term = int(self.form.console_short_term_combobox.currentText().lstrip(ln_str))
            long_term = int(self.form.console_long_term_combobox.currentText().lstrip(ln_str))
        else:
            short_term = int(self.form.continues_short_term_combobox.currentText().lstrip(ln_str))
            long_term = int(self.form.continues_long_term_combobox.currentText().lstrip(ln_str))
        def1 = self.results[0][row]
        def2 = self.results[1][row]
        minus_length = self.result_table.model.df['Minus Length'].iloc[row]
        ln = self.etabs.frame_obj.get_length_of_frame(beam_name) - minus_length
        text = f"Beam Name = {beam_name}, "
        text += get_deflection_check_result(def1, def2, ln, short_term, long_term)
        self.form.check_results.setText(text)
    
    def create_report(self):
        if self.results is None:
            return
        from freecad_funcs import get_file_name, open_file
        filename = get_file_name(suffix='docx', etabs=self.etabs)
        from report import beam_deflection_report as report
        doc = None
        for row in range(len(self.results[0])):
            beam_name = str(self.result_table.model.data(self.result_table.model.index(row, 0)))
            text1 = self.results[2][row]
            # check results
            is_console = self.result_table.model.df['Console'].iloc[row]
            ln_str = 'Ln / '
            if is_console:
                short_term = int(self.form.console_short_term_combobox.currentText().lstrip(ln_str))
                long_term = int(self.form.console_long_term_combobox.currentText().lstrip(ln_str))
            else:
                short_term = int(self.form.continues_short_term_combobox.currentText().lstrip(ln_str))
                long_term = int(self.form.continues_long_term_combobox.currentText().lstrip(ln_str))
            def1 = self.results[0][row]
            def2 = self.results[1][row]
            minus_length = self.result_table.model.df['Minus Length'].iloc[row]
            ln = self.etabs.frame_obj.get_length_of_frame(beam_name) - minus_length
            text2 = get_deflection_check_result(def1, def2, ln, short_term, long_term)
            doc = report.create_report(self.etabs, text1, text2, beam_name, doc=doc)
            doc.add_page_break()
        doc.save(filename)
        open_file(filename)

    def get_file_name(self):
        return str(self.etabs.get_filename_path_with_suffix(".EDB"))
    
    def check(self):
        df = self.result_table.model.df
        if min(min(df.Width.unique()), min(df.Height.unique())) <= 0:
            QMessageBox.warning(None, "Zero Dimention", 'Check the Beams Widths and Heights, There is Zero Value')
            return
        beams_props = df.to_dict()
        civiltools_config.update_setting(self.etabs, ['beams_properties'], [beams_props])
        self.main_file_path = self.get_file_name()
        # Get beam and point
        live_percentage = self.form.live_percentage_spinbox.value()
        equivalent_loads = self.get_equivalent_loads()
        dead = equivalent_loads.get('Dead', [])
        supper_dead = equivalent_loads.get('SDead', [])
        lives = equivalent_loads.get('L', []) + equivalent_loads.get('L_5', []) + equivalent_loads.get('RoofLive', []) + equivalent_loads.get('Snow', [])
        filename = self.form.filename.text()
        # Get Results
        self.results = self.etabs.design.get_deflection_of_beams(
            dead=dead,
            supper_dead=supper_dead,
            lives=lives,
            beam_names=df,
            lives_percentage=live_percentage,
            filename=filename,
        )
        self.form.check_button.setEnabled(False)
        # self.emit_row_clicked()
        self.open_main_file()
        QMessageBox.information(None, "Complete", "Beam Deflection Check Complete.")

    def emit_row_clicked(self):
        index = QModelIndex()
        selection_model = self.form.table_view.selectionModel()
        old_selection = selection_model.selection()
        new_selection = QItemSelection(index, index)  # Replace 'index' with the desired QModelIndex object
        self.form.table_view.selectionModel().selectionChanged.emit(old_selection, new_selection)

    def fill_load_cases(self):
        load_patterns = self.etabs.load_patterns.get_load_patterns()
        map_number_to_pattern = {
            1 : self.form.dead_combobox,    # 'Dead',
            2 : self.form.sdead_combobox,   # 'Super Dead',
            3 : self.form.live_combobox,    # 'Live',
            4 : self.form.lred_combobox,    # 'Reducible Live',
            7 : self.form.snow_combobox, # 'Snow',
            11 : self.form.lroof_combobox, # 'ROOF Live',
        }
        live_loads = [''] + [lp for lp in load_patterns if self.etabs.SapModel.LoadPatterns.GetLoadType(lp)[0] in (3, 4, 11)]
        live_loads_combobox = (
                self.form.live_combobox,
                self.form.lred_combobox,
                self.form.lroof_combobox,
                self.form.live5_combobox,
                self.form.live_parking_combobox,
                )
        for combobox in live_loads_combobox:
            combobox.addItems(live_loads)
        for lp in load_patterns:
            type_ = self.etabs.SapModel.LoadPatterns.GetLoadType(lp)[0]
            combobox = map_number_to_pattern.get(type_, None)
            i = -1
            if lp in live_loads:
                i = live_loads.index(lp)
            if combobox is not None:
                if combobox in live_loads_combobox:
                    # if i == -1:
                    #     combobox.addItem(lp)
                    # else:
                    combobox.setCurrentIndex(i)
                else:
                    combobox.addItem(lp)
            if type_ == 3 and '5' in lp:
                self.form.live5_combobox.setCurrentIndex(i)

    def resize_columns(self):
        for column in range(self.model.columnCount()):
            self.form.table_view.resizeColumnToContents(column)

    def open_main_file(self):
        self.etabs.SapModel.File.OpenFile(str(self.main_file_path))
    
    def get_equivalent_loads(self):
        load_patterns = self.etabs.load_patterns.get_load_patterns()
        equivalent_loads = {}
        # Deads
        deads = []
        dead = self.form.dead_combobox.currentText()
        if dead:
            deads.append(dead)
        if deads:
            equivalent_loads['Dead'] = deads
        sdeads = []
        sdead = self.form.sdead_combobox.currentText()
        if sdead:
            sdeads.append(sdead)
        partition = self.form.partition_combobox.currentText()
        if partition:
            sdeads.append(partition)
        if sdeads:
            equivalent_loads['SDead'] = sdeads
        # L
        lives = []
        live = self.form.live_combobox.currentText()
        if live:
            lives.append(live)
            if live not in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(live, 3)
        lred = self.form.lred_combobox.currentText()
        if lred:
            lives.append(lred)
            if lred not in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(lred, 4)
        if lives:
            equivalent_loads['L'] = lives
        # L_5
        Ls_5 = []
        live5 = self.form.live5_combobox.currentText()
        if live5:
            Ls_5.append(live5)
            if live5 not in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(live5, 3)
        if Ls_5:
            equivalent_loads['L_5'] = Ls_5
        # RoofLive
        lroof = self.form.lroof_combobox.currentText()
        if lroof:
            equivalent_loads['RoofLive'] = [lroof]
            if lroof not in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(lroof, 11)
        # snow
        snow = self.form.snow_combobox.currentText()
        if snow:
            equivalent_loads['Snow'] = [snow]
            if snow not in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(snow, 7)
        return equivalent_loads
    
    def accept(self):
        self.form.close()

    def closeEvent(self, event):
        print("you just closed the pyqt window!!! you are awesome!!!")
        self.reject()
    
    def reject(self):
        if (
            self.main_file_path is not None and 
            QMessageBox.question(
            None,
            'Open Main File',
            'Do you want to Open Main File?',)
            ) == QMessageBox.Yes:
            self.open_main_file()
        self.form.close()
        
    def draw_beams_columns(self, beam_name:str):
        story = self.etabs.SapModel.FrameObj.GetLabelFromName(beam_name)[1]
        beams, columns = self.beam_columns[story]
        self.scene.clear()
        
        blue_pen = QtGui.QPen(QtGui.QColor("Red"))
        black_pen = QtGui.QPen(QtGui.QColor("Black"))
        blue_pen.setWidth(20)
        black_pen.setWidth(5)
        for name in beams:
            coords = self.etabs.frame_obj.get_xy_of_frame_points(name)
            line = self.scene.addLine(coords[0], -coords[1] , coords[2] , -coords[3] )
            if name == beam_name:
                line.setPen(blue_pen)
            else:
                line.setPen(black_pen)
        # Draw Columns
        # Convert the points and draw the polygon on the scene
        brush = QBrush(QtGui.QColor("Black"))
        for name in columns:
            coords = self.etabs.frame_obj.get_xy_of_frame_points(name)
            polygon = convert5Pointto8Point(coords[0], -coords[1], 50, 50, 0)
            item = self.scene.addPolygon(polygon)
            # Set the brush on the polygon item
            item.setBrush(brush)
        self.form.graphicsview.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def show_help(self):
        from freecad_funcs import show_help
        show_help('beams_deflection.html', 'civilTools')


def convert5Pointto8Point(cx_, cy_, w_, h_, a_):
    theta = math.radians(a_)
    bbox = np.array([[cx_], [cy_]]) + \
        np.matmul([[math.cos(theta), math.sin(theta)],
                   [-math.sin(theta), math.cos(theta)]],
                  [[-w_ / 2, w_/ 2, w_ / 2, -w_ / 2, w_ / 2 + 8],
                   [-h_ / 2, -h_ / 2, h_ / 2, h_ / 2, 0]])

    # Create a QPolygonF object with the points
    polygon = QPolygonF()
    for i in range(4):
        x, y = bbox[0][i], bbox[1][i]
        polygon.append(QPointF(x, y))
    return polygon