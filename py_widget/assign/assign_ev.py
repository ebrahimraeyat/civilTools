from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui
import FreeCAD

from exporter import config

civiltools_path = Path(__file__).absolute().parent.parent.parent

class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model, json_file):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'assign' / 'assign_ev.ui'))
        self.etabs = etabs_model
        self.json_file = json_file
        self.fill_load_patterns()
        self.fill_acc_importance_factor()
        self.create_connections()

    def export_to_etabs(self):
        frames = self.etabs.select_obj.get_selected_obj_type(2)
        load_patterns = []
        dead = self.form.dead_combobox.currentText()
        load_patterns.append(dead)
        ev = self.form.ev_combobox.currentText()
        if not ev:
            QMessageBox.warning(None, "EV Error", "Please Type the name of the Vertical seismic load pattern!")
            return
        all_load_patterns = self.etabs.load_patterns.get_load_patterns()
        if ev not in all_load_patterns:
            QMessageBox.warning(None, "EV Error", f"Vertical Load Pattern {ev} don't exist in Load patterns!")
            return
        acc = float(self.form.acc.currentText())
        importance_factor = float(self.form.importance_factor.currentText())
        replace = self.form.replace.isChecked()
        self_weight = self.form.self_weight.isChecked()
        self.etabs.frame_obj.assign_ev(
            frames=frames,
            load_patterns=load_patterns,
            acc=acc,
            ev=ev,
            importance_factor=importance_factor,
            replace=replace,
            self_weight=self_weight,
        )
        QMessageBox.information(
            None,
            'Successfull',
            f'Successfully Apply EV to {self.etabs.get_filename()} Model.',
        )
        # self.reject()

    def fill_load_patterns(self):
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
            # if type_ == 3 and '5' in lp:
            #         self.form.live5_combobox.addItem(lp)
            # elif type_ == 4 and '5' in lp:
            #         self.form.lred5_combobox.addItem(lp)
            # elif type_ == 5: # seismic
            #     pass
            if type_ == 8:
                if 'ev' in lp.lower() or 'ez' in lp.lower() or 'qz' in lp.lower():
                    self.form.ev_combobox.addItem(lp)
            
    def create_connections(self):
        self.form.export_to_etabs_button.clicked.connect(self.export_to_etabs)
        # self.form.self_weight.stateChanged.connect(self.show_self_weight_warnings)
        self.form.partition_dead_checkbox.stateChanged.connect(self.partition_clicked)
        self.form.partition_live_checkbox.stateChanged.connect(self.partition_clicked)
        self.form.cancel_button.clicked.connect(self.reject)

    def show_self_weight_warnings(self):
        if self.form.self_weight.isChecked():
            ev = self.form.ev_combobox.currentText()
            msg = f"This option changes the self weight value of the vertical load pattern, {ev}, \
            and this considers the self weight of all Beams and Floors."
            QMessageBox.warning(None, "Self Weight", msg)

    def partition_clicked(self):
        if self.form.partition_dead_checkbox.isChecked():
            self.form.partition_live_checkbox.setChecked(False)
        else:
            self.form.partition_dead_checkbox.setChecked(False)

    def fill_acc_importance_factor(self):
        d = config.load(self.json_file)
        accs = [
            'کم',
            'متوسط',
            'زیاد',
            'خیلی زیاد',
            ]
        importance_factors = []
        for i in range(self.form.importance_factor.count()):
            importance_factors.append(self.form.importance_factor.itemText(i))
        risk_level = d['risk_level']
        importance_factor = d['importance_factor']
        i = accs.index(risk_level)
        j = importance_factors.index(importance_factor)

        self.form.acc.setCurrentIndex(i)
        self.form.importance_factor.setCurrentIndex(j)

    def reject(self):
        self.form.close()    

    def getStandardButtons(self):
        return 0

    