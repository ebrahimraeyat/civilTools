from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui

import table_model
from qt_models.columns_control_models import ColumnsControlDelegate, ControlColumns

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'columns_control.ui'))
        self.etabs = etabs_model
        self.create_connections()
        self.main_file_path = None

    def create_connections(self):
        self.form.check.clicked.connect(self.check)
        # self.form.cancel_button.clicked.connect(self.reject)
        # self.form.open_main_file_button.clicked.connect(self.open_main_file)
        # self.form.structure_type_combobox.currentIndexChanged.connect(self.set_open_main_file)

    def check(self):
        self.etabs.set_current_unit('kgf', 'cm')
        columns_type_sections_df, columns_type_names_df = self.etabs.frame_obj.get_columns_type_sections(dataframe=True)
        column_names = self.etabs.frame_obj.concrete_section_names('Column')
        section_areas = self.etabs.frame_obj.get_section_area(column_names)
        table_model.show_results(
            columns_type_sections_df,
            model=ControlColumns,
            function=self.etabs.view.show_frame_with_lable_and_story,
            kwargs = {
                "section_areas": section_areas,
                "custom_delegate": ColumnsControlDelegate,
                "columns_type_names_df": columns_type_names_df,
                'etabs': self.etabs,
                },
            etabs= self.etabs,
            json_file_name="Column-Sections",
            result_widget = table_model.ControlColumnResultWidget,
            )
        self.reject()

    def reject(self):
        self.form.close()