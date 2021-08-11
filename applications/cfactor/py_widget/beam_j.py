import sys
from pathlib import Path

from PyQt5 import QtCore

from PyQt5 import uic
from PyQt5.QtCore import Qt

cfactor_path = Path(__file__).absolute().parent.parent

beamj_base, beamj_window = uic.loadUiType(cfactor_path / 'widgets' / 'beam_j.ui')

class BeamJForm(beamj_base, beamj_window):
    def __init__(self,
            # etabs_model,
            parent=None):
        super(BeamJForm, self).__init__()
        self.setupUi(self)
        # self.etabs = etabs_model
        # self.fill_load_combinations()
        self.create_connections()

    def fill_load_combinations(self):
        pass

    def create_connections(self):
        self.initial_checkbox.stateChanged.connect(self.set_initial_j)

    def set_initial_j(self):
        if self.initial_checkbox.isChecked():
            self.initial_spinbox.setEnabled(True)
        else:
            self.initial_spinbox.setEnabled(False)

