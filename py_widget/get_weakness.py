from pathlib import Path

import pandas as pd

from PySide import QtGui
import FreeCADGui as Gui
import FreeCAD
from PySide.QtGui import QMessageBox, QFileDialog

import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent

from exporter import civiltools_config


class Form(QtGui.QWidget):
    def __init__(self, etabs_obj, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'weakness.ui'))
        self.etabs = etabs_obj
        self.d = d
        self.directory = str(Path(self.etabs.SapModel.GetModelFilename()).parent)
        self.fill_selected_beams()
        self.set_filenames()
        self.create_connections()
        self.load_config(d)

    def load_config(self, d):
        civiltools_config.load(self.etabs, self.form, d)

    def accept(self):
        if not self.etabs.success:
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        dynamic = self.form.dynamic_analysis_groupbox.isChecked()
        use_weakness_file = self.form.file_groupbox.isChecked()
        dir_ = 'x' if self.form.x_radio_button.isChecked() else 'y'
        beam_numbers = self.form.beams_list.count()
        if beam_numbers == 0:
            try:
                name = self.SapModel.SelectObj.GetSelected()[2][0]
            except:
                QMessageBox.warning(None, 'Select Beam', 'Select One Beam in the ETABS Model.')
                return
        else:
            name = self.form.beams_list.currentItem().text()
        if use_weakness_file:
            weakness_filepath = Path(self.form.weakness_file.text())
            if weakness_filepath.exists():
                ret = self.etabs.frame_obj.get_beams_columns_weakness_structure(
                    name=name,
                    weakness_filename=weakness_filepath,
                    dir_=dir_,
                    dynamic=dynamic,
                    d = self.d,
                    )
        else:
            weakness_filename = f'weakness_{dir_}.EDB'
            ret = self.etabs.frame_obj.get_beams_columns_weakness_structure(
                name=name,
                weakness_filename=weakness_filename,
                dir_=dir_,
                dynamic=dynamic,
                d = self.d,
                )
        if not ret:
            err = "Please select one beam in ETABS model!"
            QMessageBox.critical(self, "Error", str(err))
            return None
        df = pd.DataFrame(ret[0], columns=ret[1])
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        char_len = int(p.GetFloat('table_max_etabs_model_name_length', 200))
        import table_model
        table_model.show_results(df, table_model.ColumnsRatioModel,
        function=self.etabs.view.show_frame_with_lable_and_story,
        etabs=self.etabs,
        json_file_name=f"ColumnsRatio{dir_.upper()} {self.etabs.get_file_name_without_suffix()[:char_len]}")
        df = pd.DataFrame(ret[2], columns=ret[3])
        table_model.show_results(df, table_model.BeamsRebarsModel,
        function=self.etabs.view.show_frame_with_lable_and_story,
        etabs=self.etabs,
        json_file_name=f"BeamsRebars{dir_.upper()} {self.etabs.get_file_name_without_suffix()[:char_len]}")
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
        name = self.form.beams_list.currentItem().text()
        dir_ = self.etabs.frame_obj.get_frame_direction(name)
        exec(f"self.form.{dir_}_radio_button.setChecked(True)")

    def set_filenames(self):
        f = Path(self.etabs.SapModel.GetModelFilename())
        if self.form.x_radio_button.isChecked():
            self.form.weakness_file.setText(str(f.with_name('weakness_x.EDB')))
        elif self.form.y_radio_button.isChecked():
            self.form.weakness_file.setText(str(f.with_name('weakness_y.EDB')))
        
    def create_connections(self):
        self.form.weakness_button.clicked.connect(self.get_filename)
        self.form.beams_list.itemClicked.connect(self.beam_changed)
        self.form.refresh_button.clicked.connect(self.fill_selected_beams)
        self.form.x_radio_button.toggled.connect(self.set_filenames)
        self.form.y_radio_button.toggled.connect(self.set_filenames)
        self.form.run.clicked.connect(self.accept)

    def beam_changed(self, item):
        beam_name = item.text()
        self.etabs.view.show_frame(beam_name)


    def get_filename(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'select *.EDB file',
                                                  self.directory, "ETBAS Model(*.EDB)")
        if filename == '':
            return
        self.form.weakness_file.setText(filename)

