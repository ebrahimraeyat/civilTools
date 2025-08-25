from pathlib import Path
from typing import Union

from PySide import QtGui
from PySide.QtCore import Qt
import FreeCADGui as Gui
from PySide.QtGui import QFileDialog

import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtGui.QWidget):
    def __init__(self,
                 etabs_obj,
                 d: dict,
                 ):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'torsion_weaknend.ui'))
        self.etabs = etabs_obj
        self.directory = str(Path(self.etabs.SapModel.GetModelFilename()).parent)
        self.fill_selected_beams()
        self.xy_radio_button_clicked()
        self.fill_xy_loadcase_names(d)
        self.create_connections()

    def fill_xy_loadcase_names(self,
                               d: dict,
                               ):
        '''
        d: Configuration of civiltools
        '''
        ex, exn, exp, ey, eyn, eyp = self.etabs.get_first_system_seismic(d)
        x_names = [ex, exp, exn]
        y_names = [ey, eyp, eyn]
        if d.get('activate_second_system', False):
            ex, exn, exp, ey, eyn, eyp = self.etabs.get_second_system_seismic(d)
            x_names.extend((ex, exp, exn))
            y_names.extend((ey, eyp, eyn))
        self.form.x_loadcase_list.addItems(x_names)
        self.form.y_loadcase_list.addItems(y_names)
        for lw in (self.form.x_loadcase_list, self.form.y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)

    def accept(self):
        asli_file_path = self.etabs.get_filename()
        if self.form.x_radio_button.isChecked():
            dir_ = 'x'
            lw = self.form. x_loadcase_list
        else:
            dir_ = 'y'
            lw = self.form. y_loadcase_list
        items = self.form.beams_list.selectedItems()
        if items:
            name = items[-1].text()
        else:
            QtGui.QMessageBox.warning(None, 'Select Beam', 'Select one beam and press refresh button.')
            return
        self.etabs.add_prefix_suffix_name(suffix=f'_weakness_torsion_{dir_}', open=True)
        self.etabs.lock_and_unlock_model()
        self.etabs.frame_obj.set_end_release_frame(name)
        import table_model
        loadcases = []
        for i in range(lw.count()):
            item = lw.item(i)
            if item.checkState() == Qt.Checked:
                loadcases.append(item.text())
        df = self.etabs.get_diaphragm_max_over_avg_drifts(loadcases=loadcases)
        self.etabs.SapModel.File.OpenFile(str(asli_file_path))
        table_model.show_results(df, table_model.TorsionModel, self.etabs.view.show_point,
                                 etabs=self.etabs,
                                 json_file_name=f"WeaknessTorsionDir{dir_.upper()} {self.etabs.get_file_name_without_suffix()}")
        self.form.close()

    def fill_selected_beams(self):
        self.form.beams_list.clear()
        try:
            selected = self.etabs.SapModel.SelectObj.GetSelected()
        except IndexError:
            return
        types = selected[1]
        names = selected[2]
        beams = []
        for type, name in zip(types, names):
            if type == 2 and self.etabs.SapModel.FrameObj.GetDesignOrientation(name)[0] == 2:
                beams.append(name)
        if len(beams) > 0:
            self.form.beams_list.addItems(beams)
            self.form.beams_list.setCurrentRow(len(beams) - 1)

    def xy_radio_button_clicked(self):
        if self.form.x_radio_button.isChecked():
            self.form.x_loadcase_list.setEnabled(True)
            self.form.y_loadcase_list.setEnabled(False)
        elif self.form.y_radio_button.isChecked():
            self.form.x_loadcase_list.setEnabled(False)
            self.form.y_loadcase_list.setEnabled(True)
        
    def create_connections(self):
        self.form.beams_list.itemClicked.connect(self.beam_changed)
        self.form.refresh_button.clicked.connect(self.fill_selected_beams)
        self.form.x_radio_button.toggled.connect(self.xy_radio_button_clicked)
        self.form.y_radio_button.toggled.connect(self.xy_radio_button_clicked)
        self.form.run.clicked.connect(self.accept)

    def beam_changed(self, item):
        beam_name = item.text()
        self.etabs.view.show_frame(beam_name)
