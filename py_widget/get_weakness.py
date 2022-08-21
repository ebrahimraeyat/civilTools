from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui
from PySide2.QtWidgets import QMessageBox, QFileDialog

import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'weakness.ui'))
        # self.setupUi(self)
        # self.form = self
        self.etabs = etabs_obj
        self.directory = str(Path(self.etabs.SapModel.GetModelFilename()).parent)
        self.fill_selected_beams()
        self.set_filenames()
        self.create_connections()

    def accept(self):
        import table_model
        if not self.etabs.success:
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
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
                ret = self.etabs.frame_obj.get_beams_columns_weakness_structure(name=name, weakness_filename=weakness_filepath, dir_=dir_)
        else:
            weakness_filename = f'weakness_{dir_}.EDB'
            ret = self.etabs.frame_obj.get_beams_columns_weakness_structure(name=name, weakness_filename=weakness_filename, dir_=dir_)
        if not ret:
            err = "Please select one beam in ETABS model!"
            QMessageBox.critical(self, "Error", str(err))
            return None
        data, headers, data2, headers2 = ret
        table_model.show_results(data, headers, table_model.ColumnsRatioModel)
        table_model.show_results(data2, headers2, table_model.BeamsRebarsModel)
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

