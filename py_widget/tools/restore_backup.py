from pathlib import Path

from PySide import QtGui
import FreeCADGui as Gui

import civiltools_rc


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtGui.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'tools' / 'restore_backup.ui'))
        self.etabs = etabs_model
        self.fill_list()

    def accept(self):
        item = self.form.list.currentItem()
        filename_path = self.file_path / item.text()
        self.etabs.restore_backup(filename_path)

    def fill_list(self):
        self.file_path = self.etabs.get_filepath() / 'backups'
        edbs = self.file_path.glob(f'BACKUP_*')
        edbs = [edb.name for edb in edbs]
        self.form.list.addItems(edbs)
        filename = self.etabs.get_file_name_without_suffix()
        file_path = self.etabs.get_filepath()
        max_num = 0
        for edb in file_path.glob(f'BACKUP_{filename}*.EDB'):
            num = edb.stem[len('BACKUP_') + len(filename) + 1:]
            try:
                num = int(num)
                max_num = max(max_num, num)
            except:
                continue
        name = f'BACKUP_{filename}_{max_num}.EDB'
        if not name.lower().endswith('.edb'):
            name += '.EDB'
        i = -1
        try:
            i = edbs.index(name)
        except ValueError:
            i = len(edbs) - 1
        self.form.list.setCurrentRow(i)

