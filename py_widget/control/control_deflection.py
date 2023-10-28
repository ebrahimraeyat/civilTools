from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox
import FreeCADGui as Gui

from design import get_deflection_check_result

from exporter import civiltools_config

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'control_deflection.ui'))
        self.etabs = etabs_model
        self.fill_load_cases()
        self.create_connections()
        self.load_config()
        self.main_file_path = None

    def load_config(self):
        if self.etabs is None:
            return
        try:
            etabs_filename = self.etabs.get_filename()
        except:
            return
        civiltools_config.load(self.etabs, self.form)

    def create_connections(self):
        self.form.check_button.clicked.connect(self.check)
        self.form.cancel_button.clicked.connect(self.reject)
        self.form.open_main_file_button.clicked.connect(self.open_main_file)

    def get_file_name(self):
        return str(self.etabs.get_filename_path_with_suffix(".EDB"))
    
    def check(self):
        self.main_file_path = self.get_file_name()
        # Get beam and point
        selected = self.etabs.select_obj.get_selected_objects()
        beam_names = selected.get(2, [])
        if len(beam_names) == 0:
            QMessageBox.warning(None, 'Select one Beam', 'Select One Beam in ETABS Model.')
            return
        if len(beam_names) > 1:
            QMessageBox.warning(None, 'Select one Beam', 'Select Only One Beam in ETABS Model.')
            return
        beam_name = beam_names[0]
        # point name
        point_names = selected.get(1, [])
        if len(point_names) > 1:
            QMessageBox.warning(None, 'Select Point', 'Select Only Zero/One Point in ETABS Model.')
            return
        point_for_get_deflection=None
        if len(point_names) == 1:
            point_for_get_deflection = point_names[0]
        torsion_area = self.form.torsion_rebar_checkbox.isChecked()
        if torsion_area:
            torsion_area = None
        else:
            torsion_area = 0
        is_console = self.form.is_console.isChecked()
        if is_console:
            location = 'bot'
            distance_for_calculate_rho = 'start'
        else:
            location = 'top'
            distance_for_calculate_rho = 'middle'
        cover = self.form.cover_spinbox.value()
        beam_dimension = self.form.beam_dimension_groupbox.isChecked()
        if beam_dimension:
            b = self.form.beam_width_spinbox.value()
            h = self.form.beam_height_spinbox.value()
            d = h - cover
            frame_area = b * d
        else:
            frame_area = None
        live_percentage = self.form.live_percentage_spinbox.value()
        additional_rebars = self.form.additional_rebars.value()
        minus_length = self.form.minus_length.value()
        equivalent_loads = self.get_equivalent_loads()
        dead = equivalent_loads.get('Dead', [])
        supper_dead = equivalent_loads.get('SDead', [])
        lives = equivalent_loads.get('L', []) + equivalent_loads.get('L_5', []) + equivalent_loads.get('RoofLive', []) + equivalent_loads.get('Snow', [])
        ret = self.etabs.design.get_deflection_of_beam(
            dead=dead,
            supper_dead=supper_dead,
            lives=lives,
            beam_name=beam_name,
            distance_for_calculate_rho=distance_for_calculate_rho,
            location=location,
            torsion_area=torsion_area,
            frame_area=frame_area,
            cover=cover,
            lives_percentage=live_percentage,
            filename='',
            point_for_get_deflection=point_for_get_deflection,
            is_console=is_console,
            additional_rebars=additional_rebars,
        )
        text = ret[2]
        self.form.results.setText(text)
        self.form.open_main_file_button.setEnabled(True)
        self.form.check_button.setEnabled(False)
        # check results
        ln = self.etabs.frame_obj.get_length_of_frame(beam_name) - minus_length
        def1 = ret[0]
        def2 = ret[1]
        text2 = get_deflection_check_result(def1, def2, ln)
        self.form.check_results.setText(text2)

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
            i = j = -1
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
            if not live in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(live, 3)
        lred = self.form.lred_combobox.currentText()
        if lred:
            lives.append(lred)
            if not lred in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(lred, 4)
        if lives:
            equivalent_loads['L'] = lives
        # L_5
        Ls_5 = []
        live5 = self.form.live5_combobox.currentText()
        if live5:
            Ls_5.append(live5)
            if not live5 in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(live5, 3)
        if Ls_5:
            equivalent_loads['L_5'] = Ls_5
        # RoofLive
        lroof = self.form.lroof_combobox.currentText()
        if lroof:
            equivalent_loads['RoofLive'] = [lroof]
            if not lroof in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(lroof, 11)
        # snow
        snow = self.form.snow_combobox.currentText()
        if snow:
            equivalent_loads['Snow'] = [snow]
            if not snow in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(snow, 7)
        return equivalent_loads
    
    def accept(self):
        self.form.close()
    
    def reject(self):
        if (
            self.main_file_path is not None and 
            QMessageBox.question(
            None,
            'Open Main File',
            'Do you want to Open Main File?',)
            ) == QMessageBox.Yes:
            self.open_main_file()
        self.accept()
        
    def getStandardButtons(self):
        return 0