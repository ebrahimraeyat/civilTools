from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic, QtWidgets

export_etabs_window, etabs_base = uic.loadUiType('widgets/export_etabs.ui')

class ExportToEtabs(etabs_base, export_etabs_window):
    def __init__(self, building=None, parent=None):
        super(ExportToEtabs, self).__init__()
        self.setupUi(self)
        self.building = building
        self.input_button.clicked.connect(self.selectFile)
        self.output_button.clicked.connect(self.saveFile)

    def accept(self):
        input_e2k = self.input_path_line.text()
        output_e2k = self.output_path_line.text()
        with open(input_e2k, encoding="ISO-8859-1") as f:
            input_str = f.read()
        apply_earthquake_file = self._earthquake_e2k_text(input_str)
        with open(output_e2k, 'w') as output_file:
            output_file.write(apply_earthquake_file)
        etabs_base.accept(self)

    def _earthquake_e2k_text(self, string):
        results = self.building.results
        ex, ey = results[1], results[2]
        kx, ky = self.building.kx, self.building.ky
        ex_drift, kx_drift = self.building.results_drift[1], self.building.kx_drift
        ey_drift, ky_drift = self.building.results_drift[2], self.building.ky_drift
        siesmic_drift = []
        e2k_text = ''
        for line in string.splitlines():
            if "Seismic (Drift)" in line:
                load_case_name = line.split()[1]
                siesmic_drift.append(load_case_name)
            if all(seismic in line for seismic in [" SEISMIC", 'DIR "']):
                l = line.split()
                top_story_index = l.index("TOPSTORY") + 1
                bot_story_index = l.index("BOTTOMSTORY") + 1
                SHEARCOEFF_index = l.index("SHEARCOEFF") + 1
                HEIGHTEXPONENT_index = l.index("HEIGHTEXPONENT") + 1
                if any(drift in line for drift in siesmic_drift):
                    if 'DIR "X' in line:
                        l[SHEARCOEFF_index] = f'{ex_drift}'
                        l[HEIGHTEXPONENT_index] = f'{kx_drift}'
                    elif 'DIR "Y' in line:
                        l[SHEARCOEFF_index] = f'{ey_drift}'
                        l[HEIGHTEXPONENT_index] = f'{ky_drift}'
                elif 'DIR "X' in line:
                    l[SHEARCOEFF_index] = f'{ex}'
                    l[HEIGHTEXPONENT_index] = f'{kx}'
                elif 'DIR "Y' in line:
                    l[SHEARCOEFF_index] = f'{ey}'
                    l[HEIGHTEXPONENT_index] = f'{ky}'
                new_line = ' '.join(l)
                e2k_text += new_line+'\n'
            else:
                e2k_text += line+'\n'
        return e2k_text

    def selectFile(self):
        self.input_path_line.setText(QFileDialog.getOpenFileName(filter="e2k(*.e2k)")[0])

    def saveFile(self):
        output_e2k = QFileDialog.getSaveFileName(filter="e2k(*.e2k)")[0]
        if not output_e2k.endswith('.e2k'):
            output_e2k += '.e2k'
        self.output_path_line.setText(output_e2k)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    exp_et_w = ExportToEtabs()
    if exp_et_w.exec_():
        print('export')
    sys.exit(app.exec_())
