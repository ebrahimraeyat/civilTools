from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox
import FreeCADGui as Gui
import FreeCAD

from freecad_funcs import import_etabs_mesh_results

from exporter import civiltools_config

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'control_deflection_of_slab.ui'))
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
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        live_load_percentage = p.GetFloat('civiltools_live_load_percentage_deflection', 0.25)
        self.form.live_percentage_spinbox.setValue(live_load_percentage)

    def create_connections(self):
        self.form.check_button.clicked.connect(self.check)
        self.form.cancel_button.clicked.connect(self.reject)
        self.form.open_main_file_button.clicked.connect(self.open_main_file)

    def get_file_name(self):
        return str(self.etabs.get_filename_path_with_suffix(".EDB"))
    
    def check(self):
        self.main_file_path = self.get_file_name()
        # Get beam and point
        slab_names = self.etabs.select_obj.get_selected_floors()
        if len(slab_names) == 0:
            QMessageBox.warning(None, 'Select one Floor', 'Select One Floor in ETABS Model.')
            return
        if len(slab_names) > 1:
            QMessageBox.warning(None, 'Select one Floor', 'Select Only One Floor in ETABS Model.')
            return
        slab_name = slab_names.pop()
        live_percentage = self.form.live_percentage_spinbox.value()
        s1 = self.form.s1_spinbox.value() * 10
        d = self.form.d_spinbox.value() * 10
        twtop = self.form.twtop_spinbox.value()
        twbot = self.form.twbot_spinbox.value()
        tw = (twtop + twbot) / 2 * 10
        as_top = self.form.astop_spinbox.value() * 100
        as_bot = self.form.asbot_spinbox.value() * 100
        hc = self.form.hc_spinbox.value() * 10
        equivalent_loads = self.get_equivalent_loads()
        dead = equivalent_loads.get('Dead', [])
        supper_dead = equivalent_loads.get('SDead', [])
        lives = equivalent_loads.get('L', []) + equivalent_loads.get('L_5', []) + equivalent_loads.get('RoofLive', []) + equivalent_loads.get('Snow', [])
        ret = self.etabs.area.get_deflection_of_slab(
            dead=dead,
            supper_dead=supper_dead,
            lives=lives,
            slab_name=slab_name,
            s=s1,
            d=d,
            tw=tw,
            hc=hc,
            as_top=as_top,
            as_bot=as_bot,
            two_way=True,
            lives_percentage=live_percentage,
            filename='',
        )
        print(ret)
        # m = self.etabs.area.get_mesh_results([slab_name])
        # import_etabs_mesh_results(m)
        m = self.etabs.area.get_mesh_results([slab_name], case_name='deflection2')
        import_etabs_mesh_results(m)
        self.open_main_file()
        # self.form.open_main_file_button.setEnabled(True)
        # self.form.check_button.setEnabled(False)

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