from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox

cfactor_path = Path(__file__).absolute().parent.parent

base, window = uic.loadUiType(cfactor_path / 'widgets' / 'explode_seismic_load_patterns.ui')


class Form(base, window):
    def __init__(self, etabs_model, parent=None):
        super(Form, self).__init__()
        self.setupUi(self)
        self.etabs = etabs_model
        
    def accept(self):
        ex = self.ex.text()
        epx = self.epx.text()
        enx = self.enx.text()
        ey = self.ey.text()
        epy = self.epy.text()
        eny = self.eny.text()
        equal_names = {
            'XDir' : ex,
            'XDirPlusE' : epx,
            'XDirMinusE' : enx,
            'YDir' : ey,
            'YDirPlusE' : epy,
            'YDirMinusE' : eny,
            }
        replace_ex = self.replace_ex.isChecked()
        replace_ey = self.replace_ey.isChecked()
        drift_prefix = self.drift_prefix.text()
        drift_suffix = self.drift_suffix.text()
        self.etabs.database.expand_loads(
            equal_names=equal_names,
            replace_ex = replace_ex,
            replace_ey = replace_ey,
            drift_prefix = drift_prefix,
            drift_suffix = drift_suffix,
            )
        window.accept(self)
        msg = "Exploding Load Patterns Done."
        QMessageBox.information(None, 'Successful', str(msg))

