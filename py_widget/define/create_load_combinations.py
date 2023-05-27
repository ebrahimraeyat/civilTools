from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Signal, Qt

import FreeCADGui as Gui
import FreeCAD
import freecad_funcs

from exporter import civiltools_config
from db import ostanha

civiltools_path = Path(__file__).absolute().parent.parent.parent
# from load_combinations import generate_concrete_load_combinations
from qt_models import treeview

class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'create_load_combinations.ui'))
        self.form.load_combinations_view.index_activated = Signal(list)
        self.etabs = etabs_model
        self.fill_load_cases()
        self.fill_cities()
        self.create_connections()
        self.load_config()
        self.setA()
        self.data = None
    
    def load_config(self):
        if self.etabs is None:
            return
        try:
            etabs_filename = self.etabs.get_filename()
        except:
            return
        civiltools_config.load(self.etabs, self.form)

    def create(self):
        self.etabs.unlock_model()
        equivalent_loads = self.get_equivalent_loads()
        rho_x = float(self.form.rhox_combobox.currentText())
        rho_y = float(self.form.rhoy_combobox.currentText())
        prefix = self.form.prefix.text()
        suffix = self.form.suffix.text()
        ev_negative = self.form.ev_negative.isChecked()
        add_notional = self.form.add_notional.isChecked()
        A = self.get_acc(self.form.risk_level.currentText())
        I = float(self.form.importance_factor.currentText())
        sequence_numbering = self.form.sequence_numbering.isChecked()
        if self.form.lrfd.isChecked():
            design_type = "LRFD"
        elif self.form.asd.isChecked():
            design_type = "ASD"
        separate_direction = self.form.separate_direction.isChecked()
        retaining_wall = self.form.retaining_wall_groupbox.isChecked()
        omega_x = 0
        omega_y = 0
        if self.form.omega_groupbox.isChecked():
            omega_x = float(self.form.omega_x.currentText())
            omega_y = float(self.form.omega_y.currentText())
        self.data = self.etabs.load_combinations.generate_concrete_load_combinations(
            equivalent_loads=equivalent_loads,
            prefix = prefix,
            suffix = suffix,
            rho_x=rho_x,
            rho_y=rho_y,
            design_type=design_type,
            separate_direction=separate_direction,
            ev_negative=ev_negative,
            A=A,
            I=I,
            sequence_numbering=sequence_numbering,
            add_notional_loads=add_notional,
            retaining_wall=retaining_wall,
            omega_x=omega_x,
            omega_y=omega_y,
        )
        items=  {}
        for i in range(0, len(self.data), 4):
            comb = self.data[i: i+4]
            name = comb[0]
            root = items.get(name, None)
            if root is None:
                root = treeview.CustomNode(name)
                items[name] = root
            root.addChild(treeview.CustomNode(comb[2:]))
        model = treeview.CustomModel(list(items.values()), headers=('Combo/Case', 'SF'))
        self.form.load_combinations_view.setModel(model)
        freecad_funcs.show_status_message(f'Created {len(items)} Load Combinations')


    def export_to_etabs(self):
        selected_combos = set()
        for ix in self.form.load_combinations_view.selectedIndexes():
            text = ix.data(Qt.DisplayRole)
            selected_combos.add(text)
        
        progressbar = FreeCAD.Base.ProgressIndicator()
        n = int(len(self.data) / 4)
        progressbar.start(
            "Creating Load Combinations...",
            n,
            )
        numbers = set()
        for i in range(0, len(self.data), 4):
            progressbar.next(True)
            comb = self.data[i: i+4]
            name = comb[0]
            if name in selected_combos:
                self.etabs.SapModel.RespCombo.add(name, 0)
                self.etabs.SapModel.RespCombo.SetCaseList(
                    name,
                    0, # loadcase=0, loadcombo=1
                    comb[2],    # cname
                    comb[3],    # sf
                    )
                numbers.add(name)
        progressbar.stop()
        QMessageBox.information(
            None,
            'Successfull',
            f'Successfully written {len(numbers)} Load Combinations to {self.etabs.get_filename()} Model.',
        )

    def fill_load_cases(self):
        load_patterns = self.etabs.load_patterns.get_load_patterns()
        map_number_to_pattern = {
            1 : self.form.dead_combobox,    # 'Dead',
            2 : self.form.sdead_combobox,   # 'Super Dead',
            3 : self.form.live_combobox,    # 'Live',
            4 : self.form.lred_combobox,    # 'Reducible Live',
            # 5 : self.form.dead_combobox # 'Seismic',
            # 6 : self.form.dead_combobox # 'Wind',
            7 : self.form.snow_combobox, # 'Snow',
            # 8 : self.form.mass_combobox, # 'Other',
            11 : self.form.lroof_combobox, # 'ROOF Live',
            # 12 : self.form.dead_combobox # 'Notional',
        }
        live_loads = [''] + [lp for lp in load_patterns if self.etabs.SapModel.LoadPatterns.GetLoadType(lp)[0] in (3, 4, 11)]
        other_loads = [''] + [lp for lp in load_patterns if self.etabs.SapModel.LoadPatterns.GetLoadType(lp)[0] == 8]
        live_loads_combobox = (
                self.form.live_combobox,
                self.form.lred_combobox,
                self.form.lroof_combobox,
                self.form.live5_combobox,
                self.form.lred5_combobox,
                )
        other_combobox = (
            self.form.mass_combobox,
            self.form.ev_combobox,
            self.form.hxp_combobox,
            self.form.hxn_combobox,
            self.form.hyp_combobox,
            self.form.hyn_combobox,
            )
        for combobox in live_loads_combobox:
            combobox.addItems(live_loads)
        for combobox in other_combobox:
            combobox.addItems(other_loads)
        for lp in load_patterns:
            type_ = self.etabs.SapModel.LoadPatterns.GetLoadType(lp)[0]
            combobox = map_number_to_pattern.get(type_, None)
            i = j = -1
            if lp in live_loads:
                i = live_loads.index(lp)
            if lp in other_loads:
                j = other_loads.index(lp)
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
            elif type_ == 4 and '5' in lp:
                self.form.lred5_combobox.setCurrentIndex(i)
            elif type_ == 5: # seismic
                pass
            elif type_ == 8:
                if 'mass' in lp.lower() or 'wall' in lp.lower():
                    self.form.mass_combobox.setCurrentIndex(j)
                elif any((
                    'ev' in lp.lower(),
                    'ez' in lp.lower(),
                    'qv' in lp.lower(),
                    'qz' in lp.lower(),
                    )):
                    self.form.ev_combobox.setCurrentIndex(j)
        xdir, xdir_minus, xdir_plus, ydir, ydir_minus, ydir_plus = self.etabs.load_patterns.get_seismic_load_patterns()
        for combobox, name, dir_ in zip(
                (self.form.ex_combobox,
                self.form.exn_combobox,
                self.form.exp_combobox,
                self.form.ey_combobox,
                self.form.eyn_combobox,
                self.form.eyp_combobox,
                ), 
                ('EX', 'EXN', 'EXP', 'EY', 'EYN', 'EYP'),
                (xdir, xdir_minus, xdir_plus, ydir, ydir_minus, ydir_plus),
            ):
            dir_.add(name)
            combobox.addItems(dir_)

    def setA(self):
        sotoh = ['خیلی زیاد', 'زیاد', 'متوسط', 'کم']
        ostan = self.get_current_ostan()
        city = self.get_current_city()
        try:
            A = int(ostanha.ostans[ostan][city][0])
            i = self.form.risk_level.findText(sotoh[A - 1])
            self.form.risk_level.setCurrentIndex(i)
        except KeyError:
            pass
    
    def get_acc(self, sath):
        sotoh = {'خیلی زیاد' : 0.35,
                'زیاد' : 0.30,
                'متوسط' : 0.25,
                'کم' : 0.20,
                }
        return sotoh[sath]
    
    def get_current_ostan(self):
        return self.form.ostan.currentText()

    def get_current_city(self):
        return self.form.city.currentText()

    def get_citys_of_current_ostan(self, ostan):
        '''return citys of ostan'''
        return ostanha.ostans[ostan].keys()

    def set_citys_of_current_ostan(self):
        self.form.city.clear()
        ostan = self.get_current_ostan()
        citys = self.get_citys_of_current_ostan(ostan)
        # citys.sort()
        self.form.city.addItems(citys)
    
    def fill_cities(self):
        ostans = ostanha.ostans.keys()
        self.form.ostan.addItems(ostans)
        self.set_citys_of_current_ostan()

    def create_connections(self):
        self.form.create_button.clicked.connect(self.create)
        self.form.export_to_etabs_button.clicked.connect(self.export_to_etabs)
        self.form.partition_dead_checkbox.stateChanged.connect(self.partition_dead_clicked)
        self.form.partition_live_checkbox.stateChanged.connect(self.partition_live_clicked)
        self.form.load_combinations_view.activated.connect(self.indexActivated)
        self.form.load_combinations_view.expanded.connect(self.treeExpanded)
        self.form.ostan.currentIndexChanged.connect(self.set_citys_of_current_ostan)
        self.form.city.currentIndexChanged.connect(self.setA)
        self.form.lrfd.clicked.connect(self.consider_ev)
        self.form.asd.clicked.connect(self.consider_ev)
    
    def consider_ev(self):
        if self.form.lrfd.isChecked():
            self.form.ev_negative.setChecked(True)
        else:
            self.form.ev_negative.setChecked(False)
        if self.form.asd.isChecked():
            self.form.ev_negative.setChecked(False)
        else:
            self.form.ev_negative.setChecked(True)

    def partition_dead_clicked(self):
        if self.form.partition_dead_checkbox.isChecked():
            self.form.partition_live_checkbox.setChecked(False)
        else:
            self.form.partition_live_checkbox.setChecked(True)
    
    def partition_live_clicked(self):
        if self.form.partition_live_checkbox.isChecked():
            self.form.partition_dead_checkbox.setChecked(False)
        else:
            self.form.partition_dead_checkbox.setChecked(True)
    
    def indexActivated(self, index):
        # self.form.load_combinations_view.index_activated.emit(self.form.load_combinations_view.model().asRecord(index))
        for ix in self.form.load_combinations_view.selectedIndexes():
            text = ix.data(Qt.DisplayRole) # or ix.data()
            print(text)


    def treeExpanded(self):
        for column in range(self.form.load_combinations_view.model().columnCount(
                            QModelIndex())):
            self.form.load_combinations_view.resizeColumnToContents(column)


        # self.form.prefix_name.editingFinished.connect(self.check_prefix)

    # def check_prefix(self):
    #     if len(self.form.prefix_name.text()) < 1:
    #         self.form.prefix_name.setText('SEC')

    
    def get_equivalent_loads(self):
        load_patterns = self.etabs.load_patterns.get_load_patterns()
        equivalent_loads = {}
        # Deads
        deads = []
        dead = self.form.dead_combobox.currentText()
        if dead:
            deads.append(dead)
            if not dead in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(dead, 1)
                self.etabs.SapModel.LoadPatterns.SetSelfWTMultiplier(dead, 1)
        sdead = self.form.sdead_combobox.currentText()
        if sdead:
            deads.append(sdead)
            if not sdead in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(sdead, 2)
        partition_dead = self.form.partition_dead_combobox.currentText()
        if partition_dead:
            deads.append(partition_dead)
            if not partition_dead in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(partition_dead, 1)
        if deads:
            equivalent_loads['Dead'] = deads
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
        partition_live = self.form.partition_live_combobox.currentText()
        if partition_live:
            lives.append(partition_live)
            if not partition_live in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(partition_live, 3)
        if lives:
            equivalent_loads['L'] = lives
        # L_5
        Ls_5 = []
        live5 = self.form.live5_combobox.currentText()
        if live5:
            Ls_5.append(live5)
            if not live5 in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(live5, 3)
        lred5 = self.form.lred5_combobox.currentText()
        if lred5:
            Ls_5.append(lred5)
            if not lred5 in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(lred5, 4)
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
        # seismic
        ## EX
        ex = self.form.ex_combobox.currentText()
        if ex:
            equivalent_loads['EX'] = [ex]
            if not ex in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(ex, 5)
        ## EXP
        exp = self.form.exp_combobox.currentText()
        if exp:
            equivalent_loads['EXP'] = [exp]
            if not exp in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(exp, 5)
        ## EXN
        exn = self.form.exn_combobox.currentText()
        if exn:
            equivalent_loads['EXN'] = [exn]
            if not exn in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(exn, 5)
        # EY
        ey = self.form.ey_combobox.currentText()
        if ey:
            equivalent_loads['EY'] = [ey]
            if not ey in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(ey, 5)
        ## EYP
        eyp = self.form.eyp_combobox.currentText()
        if eyp:
            equivalent_loads['EYP'] = [eyp]
            if not eyp in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(eyp, 5)
        ## EYN
        eyn = self.form.eyn_combobox.currentText()
        if eyn:
            equivalent_loads['EYN'] = [eyn]
            if not eyn in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(eyn, 5)
        # # mass
        # masses = None
        # mass = self.form.mass_combobox.currentText()
        # if mass:
        #     masses = [mass]

        # EV
        ev = self.form.ev_combobox.currentText()
        if ev:
            equivalent_loads['EV'] = [ev]
            if not ev in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(ev, 8)
        # Retaining Wall
        # HXP
        hxp = self.form.hxp_combobox.currentText()
        if hxp:
            equivalent_loads['HXP'] = [hxp]
            if hxp not in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(hxp, 8)
        # HXN
        hxn = self.form.hxn_combobox.currentText()
        if hxn:
            equivalent_loads['HXN'] = [hxn]
            if hxn not in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(hxn, 8)
        # HyP
        hyp = self.form.hyp_combobox.currentText()
        if hyp:
            equivalent_loads['HYP'] = [hyp]
            if hyp not in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(hyp, 8)
        # HXN
        hyn = self.form.hyn_combobox.currentText()
        if hyn:
            equivalent_loads['HYN'] = [hyn]
            if hyn not in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(hyn, 8)

        return equivalent_loads