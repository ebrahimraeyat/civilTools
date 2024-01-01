from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui
from PySide2.QtWidgets import QMessageBox, QFileDialog

import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'weakness.ui'))
        self.form.setWindowTitle("Torsion in Weakened Structure")
        self.etabs = etabs_obj
        self.directory = str(Path(self.etabs.SapModel.GetModelFilename()).parent)
        self.fill_selected_beams()
        self.set_filenames()
        self.create_connections()

    def accept(self):

        use_weakness_file = self.form.file_groupbox.isChecked()
        dir_ = 'x' if self.form.x_radio_button.isChecked() else 'y'
        if use_weakness_file:
            weakness_filepath = self.etabs.add_prefix_suffix_name(suffix=f'_weakness_torsion_{dir_}')
            if weakness_filepath.exists() and \
                not self.etabs.get_filename() == weakness_filepath:
                self.etabs.SapModel.File.OpenFile(str(weakness_filepath))
            else:
                weakness_filepath = Path(self.form.weakness_file.text())
                if weakness_filepath.exists() and \
                    not self.etabs.get_filename() == weakness_filepath:
                    self.etabs.SapModel.File.OpenFile(str(weakness_filepath))
        else:
            items = self.form.beams_list.selectedItems()
            if items:
                name = items[-1].text()
            else:
                return
            self.etabs.add_prefix_suffix_name(suffix=f'_weakness_torsion_{dir_}', open=True)
            self.etabs.lock_and_unlock_model()
            self.etabs.frame_obj.set_end_release_frame(name)
        self.form.close()
        from PySide2 import QtCore
        QtCore.QTimer.singleShot(1, lambda : Gui.runCommand("civil_show_torsion"))

    # def getStandardButtons(self):
    #     return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

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
        if self.form.x_radio_button.isChecked():
            dir_ = 'x'
        elif self.form.y_radio_button.isChecked():
            dir_ = 'y'
        path = self.etabs.add_prefix_suffix_name(suffix=f'_weakness_torsion_{dir_}')
        self.form.weakness_file.setText(str(path))
        
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

