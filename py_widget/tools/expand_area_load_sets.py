from pathlib import Path

from PySide import QtGui

import table_model

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtGui.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.etabs = etabs_model
        self.df = self.get_expanded_shell_uniform_load_sets()
        self.show_expand_result()

    def create_connections(self):
        self.form.cancel_pushbutton.clicked.connect(self.reject)
        self.form.apply_pushbutton.clicked.connect(self.expand_load_sets)

    def show_expand_result(self):
        if self.df.empty:
            QtGui.QMessageBox.warning(None, 'Empty Load Sets', 'There is no load sets in this model.')
            return
        df = self.df.copy()
        del df['Direction']
        model=table_model.ExpandLoadSets
        self.win = table_model.ExpandedLoadSetsResults(df, model, None)
        self.win.cancel_pushbutton.clicked.connect(self.reject)
        self.win.apply_pushbutton.clicked.connect(self.expand_load_sets)
        self.win.setMinimumSize(600, 600)
        self.win.resize(600, 600)
        self.win.exec_()

    def get_expanded_shell_uniform_load_sets(self):
        return self.etabs.area.get_expanded_shell_uniform_load_sets()

    def reject(self):
        self.win.close()

    def expand_load_sets(self):
        ret = self.etabs.area.expand_uniform_load_sets_and_apply_to_model(self.df)
        if ret:
            QtGui.QMessageBox.information(None, 'Successful', 'All load sets expanded successfully.')
        else:
            QtGui.QMessageBox.warning(None, 'Failed', "Load sets did not expanded!")
        self.reject()

