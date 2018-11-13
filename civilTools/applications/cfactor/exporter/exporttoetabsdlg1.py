from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

export_etabs_window, etabs_base = uic.loadUiType('applications/cfactor/widgets/export_etabs.ui')

class ExportToEtabs(etabs_base, export_etabs_window):
    def __init__(self, building, parent=None):
        super(ExportToEtabs, self).__init__()
        self.setupUi(self)
        self.building = building
        self.input_button.clicked.connect(self.selectFile)
        self.output_button.clicked.connect(self.saveFile)
        self.input_path_line.textChanged.connect(self.set_suffix)

    def accept(self):
        input_e2k = self.input_path_line.text()
        output_e2k = self.output_path_line.text()
        story_e2k_text = self.story_e2k_text()
        apply_story_file = ExportToEtabs.replace_block(input_e2k, replacement=story_e2k_text)
        apply_earthquake_file = self._earthquake_e2k_text(apply_story_file)
        with open(output_e2k, 'w') as output_file:
            output_file.write(apply_earthquake_file)
        etabs_base.accept(self)

    @staticmethod
    def replace_block(_input, start='$ STORIES', end='$ GRIDS', replacement=''):
        outstr = ''
        with open(_input, 'r') as infile:
            copy = True
            for line in infile:
                if line.startswith(start):
                    outstr += line
                    outstr += replacement
                    copy = False
                elif line.startswith(end):
                    outstr += line
                    copy = True
                elif copy:
                    outstr += line
        return outstr

    def _story_data(self):
        story_height = []
        if self.simple_story_radiobutton.isChecked():
            num_story = self.number_of_story_spinox.value()
            typical_height = self.typical_height_spinbox.value()
            buttom_height = self.buttom_height_spinbox.value()
            for story in range(num_story, 1, -1):
                story_height.append((f'Story{story}', typical_height))
            story_height.append(('Story1', buttom_height))

        elif self.custom_story_radiobutton.isChecked():
            # do something
            print("custom")
        self.top_story = story_height[0][0]
        self.bottom_story = 'Base'  #story_height[-1][0]
        return story_height

    def story_e2k_text(self):
        story_data = self._story_data()
        storye2ktext = ''
        for story in story_data:
            storye2ktext += '  STORY "{}"  HEIGHT {}\n'.format(story[0], story[1])
        storye2ktext += '  STORY "Base"  ELEV 0\n\n'
        return storye2ktext

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
                l[top_story_index] = f'"{self.top_story}"'
                l[bot_story_index] = f'"{self.bottom_story}"'
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

    @staticmethod
    def get_len_unit(input_e2k):
        with open(input_e2k, 'r') as infile:
            for line in infile:
                if line.startswith('$ CONTROLS'):
                    break
            for line in infile:
                l = line.split()
                break
            len_unit = l[2]
            len_unit = len_unit.replace('"', ' ')
            return len_unit.lower()

    def set_suffix(self):
        input_e2k = self.input_path_line.text()
        unit = ExportToEtabs.get_len_unit(input_e2k)
        self.typical_height_spinbox.setSuffix(unit)
        self.buttom_height_spinbox.setSuffix(unit)

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
        print(exp_et_w.number_of_story_spinox.value())
    sys.exit(app.exec_())
