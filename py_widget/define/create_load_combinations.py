from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Signal, Qt

import FreeCADGui as Gui
import FreeCAD
import freecad_funcs



civiltools_path = Path(__file__).absolute().parent.parent.parent
from load_combinations import generate_concrete_load_combinations
from qt_models import treeview

class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'create_load_combinations.ui'))
        self.form.load_combinations_view.index_activated = Signal(list)
        self.etabs = etabs_model
        self.fill_load_cases()
        self.create_connections()
        self.data = None
    
    def create(self):
        equivalent_loads = self.get_equivalent_loads()
        rho_x = float(self.form.rhox_combobox.currentText())
        rho_y = float(self.form.rhoy_combobox.currentText())
        prefix = self.form.prefix.text()
        suffix = self.form.suffix.text()
        if self.form.lrfd.isChecked():
            design_type = "LRFD"
        elif self.form.asd.isChecked():
            design_type = "ASD"
        self.data = generate_concrete_load_combinations(
            equivalent_loads=equivalent_loads,
            prefix = prefix,
            suffix = suffix,
            rho_x=rho_x,
            rho_y=rho_y,
            design_type=design_type,
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
        for lp in load_patterns:
            type_ = self.etabs.SapModel.LoadPatterns.GetLoadType(lp)[0]
            combobox = map_number_to_pattern.get(type_, None)
            if combobox is not None:
                combobox.addItem(lp)
            if type_ == 3 and '5' in lp:
                    self.form.live5_combobox.addItem(lp)
            elif type_ == 4 and '5' in lp:
                    self.form.lred5_combobox.addItem(lp)
            elif type_ == 5: # seismic
                pass
            elif type_ == 8:
                if 'mass' in lp.lower() or 'wall' in lp.lower():
                    self.form.mass_combobox.addItem(lp)
                elif 'ev' in lp.lower() or 'ez' in lp.lower():
                    self.form.ev_combobox.addItem(lp)
        names = self.etabs.load_patterns.get_special_load_pattern_names(5)
        extra_names = set(names).difference(('EX', 'EPX', 'ENX', 'EY', 'EPY', 'ENY'))
        for combobox in (
                self.form.ex_combobox,
                self.form.epx_combobox,
                self.form.enx_combobox,
                self.form.ey_combobox,
                self.form.epy_combobox,
                self.form.eny_combobox,
                ):
            combobox.addItems(extra_names)
            
    def create_connections(self):
        self.form.create_button.clicked.connect(self.create)
        self.form.export_to_etabs_button.clicked.connect(self.export_to_etabs)
        self.form.partition_dead_checkbox.stateChanged.connect(self.partition_dead_clicked)
        self.form.partition_live_checkbox.stateChanged.connect(self.partition_live_clicked)
        self.form.load_combinations_view.activated.connect(self.indexActivated)
        self.form.load_combinations_view.expanded.connect(self.treeExpanded)

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
        ## EPX
        epx = self.form.epx_combobox.currentText()
        if epx:
            equivalent_loads['EPX'] = [epx]
            if not epx in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(epx, 5)
        ## ENX
        enx = self.form.enx_combobox.currentText()
        if enx:
            equivalent_loads['ENX'] = [enx]
            if not enx in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(enx, 5)
        # EY
        ey = self.form.ey_combobox.currentText()
        if ey:
            equivalent_loads['EY'] = [ey]
            if not ey in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(ey, 5)
        ## EPX
        epy = self.form.epy_combobox.currentText()
        if epy:
            equivalent_loads['EPY'] = [epy]
            if not epy in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(epy, 5)
        ## ENX
        eny = self.form.eny_combobox.currentText()
        if eny:
            equivalent_loads['ENY'] = [eny]
            if not eny in load_patterns:
                self.etabs.SapModel.LoadPatterns.Add(eny, 5)
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

        return equivalent_loads