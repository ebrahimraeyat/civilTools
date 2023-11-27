from pathlib import Path
import math

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QMessageBox
import numpy as np
from PySide2.QtGui import QPolygonF, QBrush
from PySide2.QtCore import QPointF
import FreeCADGui as Gui
import FreeCAD

from design import get_deflection_check_result
from qt_models import beam_deflection_model

from exporter import civiltools_config

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self,
    etabs_model,
    beam_names,
    d: dict={},
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
        if len(d) == 0:
            d = civiltools_config.load(self.etabs, self.form)
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        live_load_percentage = p.GetFloat('civiltools_live_load_percentage_deflection', 0.25)
        self.form.live_percentage_spinbox.setValue(live_load_percentage)
        self.populate_table(beam_names, d)

    def populate_table(self,
            beam_names: list,
            d: dict,
            ):
        '''
        d : A dictionary of etabs file settings
        '''
        d = d.get('beams_properties', {})
        beam_props = {}
        self.etabs.set_current_unit('kgf', 'cm')
        for beam_name in beam_names:
            beam_prop = d.get(beam_name, None)
            if beam_prop is None:
                section_name = self.etabs.SapModel.FrameObj.GetSection(beam_name)[0]
                try:
                    _, _, h, b, *_ = self.etabs.SapModel.PropFrame.GetRectangle(section_name)
                except:
                    h, b = 0
                label, story, *_ = self.etabs.SapModel.FrameObj.GetLabelFromName(beam_name)
                beam_prop = {
                    'Story': story,
                    'Label': label,
                    'is_console': 0,
                    'minus_length': 50,
                    'add_torsion_rebar': 2,
                    'add_rebar': 0,
                    'cover': 4,
                    'width': b,
                    'height': h,
                    'result': '',
                    }
            beam_props[beam_name] = beam_prop
        self.model = beam_deflection_model.BeamDeflectionTableModel(beam_props)
        self.form.table_view.setModel(self.model)
        self.resize_columns()

    def create_connections(self):
        self.form.check_button.clicked.connect(self.check)
        self.form.cancel_button.clicked.connect(self.reject)
        self.form.open_main_file_button.clicked.connect(self.open_main_file)
        self.form.short_term_combobox.currentIndexChanged.connect(self.result_changed)
        self.form.long_term_combobox.currentIndexChanged.connect(self.result_changed)
        self.form.table_view.selectionModel().selectionChanged.connect(self.row_clicked)

    def row_clicked(self, selection):
        if len(selection) == 0:
            return
        index = selection.indexes()[0]
        row = index.row()
        col = beam_deflection_model.NAME
        beam_name = str(self.model.data(self.model.index(row, col)))
        self.etabs.view.show_frame(beam_name)
        self.check_result(row, beam_name)
        self.draw_beams_columns(beam_name)
    
    def result_changed(self, index):
        if self.results is None:
            return
        row = self.form.table_view.currentIndex().row()
        col = beam_deflection_model.NAME
        beam_name = str(self.model.data(self.model.index(row, col)))
        self.check_result(row, beam_name)

    def check_result(self,
        beam_index: int,
        beam_name: str,
        ):
        if self.results is None:
            return
        self.form.results.setText(self.results[2][beam_index])
        # check results
        short_term = int(self.form.short_term_combobox.currentText().lstrip('Ln / '))
        long_term = int(self.form.long_term_combobox.currentText().lstrip('Ln / '))
        def1 = self.results[0][beam_index]
        def2 = self.results[1][beam_index]
        beam_prop = self.model.beam_data[beam_name]
        minus_length = beam_prop['minus_length']
        ln = self.etabs.frame_obj.get_length_of_frame(beam_name) - minus_length
        text = f"Beam Name = {beam_name}, "
        text += get_deflection_check_result(def1, def2, ln, short_term, long_term)
        self.form.check_results.setText(text)

    def get_file_name(self):
        return str(self.etabs.get_filename_path_with_suffix(".EDB"))
    
    def check(self):
        beams_props = self.model.beam_data
        civiltools_config.update_setting(self.etabs, ['beams_properties'], [beams_props])
        self.main_file_path = self.get_file_name()
        # Get beam and point
        points_for_get_deflection=None
        beam_names = []
        torsion_areas = []
        is_consoles = []
        locations = []
        distances_for_calculate_rho = []
        covers = []
        frame_areas = []
        additionals_rebars = []
        for beam_name, beam_prop in beams_props.items():
            torsion_area = beam_prop['add_torsion_rebar']
            if torsion_area:
                torsion_area = None
            else:
                torsion_area = 0
            is_console = beam_prop['is_console']
            if is_console:
                location = 'bot'
                distance_for_calculate_rho = 'start'
            else:
                location = 'top'
                distance_for_calculate_rho = 'middle'
            cover = beam_prop['cover']
            b = beam_prop['width']
            h = beam_prop['height']
            d = h - cover
            frame_area = b * d
            additional_rebars = beam_prop['add_rebar']
            # prepare inputs for calculate deflections
            beam_names.append(beam_name)
            torsion_areas.append(torsion_area)
            is_consoles.append(is_console)
            locations.append(location)
            distances_for_calculate_rho.append(distance_for_calculate_rho)
            covers.append(cover)
            frame_areas.append(frame_area)
            additionals_rebars.append(additional_rebars)
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
            beam_names=beam_names,
            distances_for_calculate_rho=distances_for_calculate_rho,
            locations=locations,
            torsion_areas=torsion_areas,
            frame_areas=frame_areas,
            covers=covers,
            lives_percentage=live_percentage,
            filename=filename,
            points_for_get_deflection=points_for_get_deflection,
            is_consoles=is_consoles,
            additionals_rebars=additionals_rebars,
        )
        self.form.open_main_file_button.setEnabled(True)
        self.form.check_button.setEnabled(False)

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
        self.accept()
    
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
        print('accept')
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