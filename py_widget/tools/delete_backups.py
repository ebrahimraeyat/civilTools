from pathlib import Path

from PySide2 import  QtWidgets

import FreeCADGui as Gui

import civiltools_rc


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'tools' / 'delete_backups.ui'))
        self.etabs = etabs_model
        self.fill_list()
        self.create_connections()

    def create_connections(self):
        self.form.select_all.clicked.connect(self.select_all)
        self.form.deselect_all.clicked.connect(self.deselect_all)
        self.form.delete_button.clicked.connect(self.delete)

    def delete(self):
        items = self.form.list.selectedItems()
        for item in items:
            filename_path = self.file_path / item.text()
            filename_path.unlink()
            self.form.list.removeItemWidget(item)
        self.form.list.clear()
        self.fill_list()
        self.deselect_all()

    def fill_list(self):
        self.file_path = self.etabs.get_filepath() / 'backups'
        edbs = self.file_path.glob(f'BACKUP_*')
        edbs = [edb.name for edb in edbs]
        self.form.list.addItems(edbs)
        self.select_all()
        
    def select_all(self):
        for i in range(self.form.list.count()):
            item = self.form.list.item(i)
            item.setSelected(True)

    def deselect_all(self):
        for i in range(self.form.list.count()):
            item = self.form.list.item(i)
            item.setSelected(False)

    def accept(self):
        Gui.Control.closeDialog()
