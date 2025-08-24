from pathlib import Path

from PySide import QtGui
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


from exporter import civiltools_config

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtGui.QWidget):
    def __init__(self,
    etabs_model,
    d: dict,
    ):
        '''
        d: dictionary of model properties
        '''
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'create_load_combinations_for_nonlinear_deflection.ui'))
        self.etabs = etabs_model
        self.fill_load_cases()
        self.load_config(d=d)
        self.create_connections()

    def load_config(self,d: dict,):
        civiltools_config.load(self.etabs, self.form, d)
            
    def create_connections(self):
        self.form.create_button.clicked.connect(self.create)

    def create(self):
        live_percentage = self.form.live_percentage_spinbox.value()
        landa = self.form.landa.value()
        equivalent_loads = self.get_equivalent_loads()
        dead = equivalent_loads.get('Dead', [])
        supper_dead = equivalent_loads.get('SDead', [])
        lives = equivalent_loads.get('L', []) + equivalent_loads.get('L_5', []) + equivalent_loads.get('RoofLive', []) + equivalent_loads.get('Snow', [])
        self.create_load_combinations(dead, supper_dead, lives, live_percentage, landa)
        QMessageBox.information(None, "Complete", "Created Load Combinations For Nonlinear Deflection.")
        self.accept()
    
    def create_load_combinations(self, dead, supper_dead, lives, live_percentage, landa):
        print("Create nonlinear load cases ...")
        lc1, lc2, lc3 = self.etabs.database.create_nonlinear_loadcases(
            dead=dead,
            supper_dead=supper_dead,
            lives=lives,
            lives_percentage=live_percentage,
            )
        print("Create deflection load combinations ...")
        self.etabs.SapModel.RespCombo.Add('deflection1', 0)
        self.etabs.SapModel.RespCombo.SetCaseList('deflection1', 0, lc2, 1)
        self.etabs.SapModel.RespCombo.SetCaseList('deflection1', 0, lc1, -1)
        # if supper_dead:
        #     self.etabs.analyze.set_load_cases_to_analyze((lc1, lc2, lc3))
        # else:
        #     self.etabs.analyze.set_load_cases_to_analyze((lc1, lc2))

        self.etabs.SapModel.RespCombo.Add('deflection2', 0)
        self.etabs.SapModel.RespCombo.SetCaseList('deflection2', 0, lc2, 1)
        self.etabs.SapModel.RespCombo.SetCaseList('deflection2', 0, lc1, landa - 1)
        if supper_dead:
            # scale factor set to 0.5 due to xi for 3 month equal to 1.0
            self.etabs.SapModel.RespCombo.SetCaseList('deflection2', 0, lc3, -0.5)

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
     
    