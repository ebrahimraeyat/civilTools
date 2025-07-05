from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui

import table_model
from qt_models.columns_pmm_model import ColumnsPMMAll, ColumnsPMMDelegate

from exporter import civiltools_config

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'shearwall' / 'create_25percent_file.ui'))
        self.etabs = etabs_model
        self.d = d
        self.create_connections()
        self.load_config(d)

    def create_connections(self):
        self.form.create_file.clicked.connect(self.create)

    def create(self):
        self.etabs.set_current_unit('kgf', 'cm')
        mod = self.form.modifier_spinbox.value()
        dynamic = self.form.dynamic_analysis_groupbox.isChecked()
        main_file, filename = self.etabs.shearwall.create_25percent_file(
            modifiers = 8 * [mod],
            dynamic=dynamic,
            d=self.d,
            open_main_file=False)
        df = self.etabs.design.get_concrete_columns_pmm_table()
        self.etabs.open_model(main_file)
        column_names = self.etabs.frame_obj.concrete_section_names('Column')
        kwargs = {
            'etabs': self.etabs,
            'custom_delegate': ColumnsPMMDelegate,
            'sections': column_names,
            }
        table_model.show_results(
            df,
            model=ColumnsPMMAll,
            function=self.etabs.view.show_frame_with_lable_and_story,
            json_file_name="shearwall_25percent_column_ratio",
            etabs=self.etabs,
            kwargs=kwargs,
            )
        self.reject()

    def load_config(self, d):
        civiltools_config.load(self.etabs, self.form, d)

    def reject(self):
        self.form.close()