from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog, QPushButton

cfactor_path = Path(__file__).absolute().parent.parent

weakness_base, weakness_window = uic.loadUiType(cfactor_path / 'widgets' / 'weakness.ui')

class WeaknessForm(weakness_base, weakness_window):
    def __init__(self, etabs_model, parent=None):
        super(WeaknessForm, self).__init__(parent)
        self.setupUi(self)
        self.etabs = etabs_model
        self.directory = str(Path(self.etabs.SapModel.GetModelFilename()).parent)
        self.fill_selected_beams()
        self.set_filenames()
        self.create_connections()

    def fill_selected_beams(self):
        self.beams_list.clear()
        selected = self.etabs.SapModel.SelectObj.GetSelected()
        types = selected[1]
        names = selected[2]
        beams = []
        for type, name in zip(types, names):
            if type == 2 and self.etabs.SapModel.FrameObj.GetDesignOrientation(name)[0] == 2:
                beams.append(name)
        if len(beams) > 0:
            self.beams_list.addItems(beams)
            self.beams_list.setCurrentRow(len(beams) - 1)

    def set_filenames(self):
        f = Path(self.etabs.SapModel.GetModelFilename())
        self.weakness_file.setText(str(f.with_name('weakness.EDB')))
        
    def create_connections(self):
        self.weakness_button.clicked.connect(self.get_filename)
        self.beams_list.itemClicked.connect(self.beam_changed)
        self.refresh_button.clicked.connect(self.fill_selected_beams)

    def beam_changed(self, item):
        # item = self.beams_list.currentItem()
        beam_name = item.text()
        self.etabs.view.show_frame(beam_name)


    def get_filename(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'select *.EDB file',
                                                  self.directory, "ETBAS Model(*.EDB)")
        if filename == '':
            return
        self.weakness_file.setText(filename)

