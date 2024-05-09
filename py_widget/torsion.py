from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui
from PySide2.QtCore import Qt


civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'torsion.ui'))
        self.etabs = etabs_obj
        self.form.run.clicked.connect(self.accept)
        self.load_config(d)

    def load_config(self, d):
        self.fill_xy_loadcase_names(d)

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
        import table_model
        loadcases = []
        for lw in (self.form.x_loadcase_list, self.form.y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                if item.checkState() == Qt.Checked:
                    loadcases.append(item.text())
        df = self.etabs.get_diaphragm_max_over_avg_drifts(loadcases=loadcases)
        table_model.show_results(df, table_model.TorsionModel, self.etabs.view.show_point,
                                 self.etabs)
        self.form.close()

    
