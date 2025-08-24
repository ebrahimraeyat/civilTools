from pathlib import Path

import pandas as pd

from PySide import QtGui
from PySide.QtCore import Qt

import FreeCADGui as Gui


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtGui.QWidget):
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'shear_story.ui'))
        self.etabs = etabs_obj
        self.fill_xy_loadcase_names()

    def accept(self):

        loadcases = []
        for lw in (self.form.x_loadcase_list, self.form.y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                if item.checkState() == Qt.Checked:
                    loadcases.append(item.text())
        data, headers = self.etabs.get_story_forces_with_percentages(
                loadcases=loadcases)
        df = pd.DataFrame(data, columns=headers)
        import table_model
        table_model.show_results(df, table_model.StoryForcesModel,
                                 etabs=self.etabs,
                                 json_file_name="StoryForces",
                                 )
    
    def reject(self):
        Gui.Control.closeDialog()

    def fill_xy_loadcase_names(self):
        x_names, y_names = self.etabs.load_patterns.get_load_patterns_in_XYdirection()
        drift_load_patterns = self.etabs.load_patterns.get_drift_load_pattern_names()
        all_load_case = self.etabs.SapModel.Analyze.GetCaseStatus()[1]
        x_names = set(x_names).intersection(all_load_case)
        y_names = set(y_names).intersection(all_load_case)
        x_names = set(x_names).difference(drift_load_patterns)
        y_names = set(y_names).difference(drift_load_patterns)
        self.form.x_loadcase_list.addItems(x_names)
        self.form.y_loadcase_list.addItems(y_names)
        for lw in (self.form.x_loadcase_list, self.form.y_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
        # for name in drift_load_patterns:
        #     if name in x_names:
        #         matching_items = self.form.x_loadcase_list.findItems(name, Qt.MatchExactly)
        #     elif name in y_names:
        #         matching_items = self.form.y_loadcase_list.findItems(name, Qt.MatchExactly)
        #     for item in matching_items:
        #         item.setCheckState(Qt.Checked)