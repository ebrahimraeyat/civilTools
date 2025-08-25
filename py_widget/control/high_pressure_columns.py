from pathlib import Path


from PySide import QtGui
import FreeCADGui as Gui
import FreeCAD

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtGui.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'high_pressure_columns.ui'))
        self.etabs = etabs_model
        self.create_connections()

    def create_connections(self):
        self.form.limit_spinbox.valueChanged.connect(self.set_group_name)

    def set_group_name(self, float):
        self.form.group_name.setText(f'{float:.2f}*Ag*fc')


    def accept(self):
        limit = self.form.limit_spinbox.value()
        data = self.etabs.database.get_axial_pressure_columns(limit)
        import table_model
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        char_len = int(p.GetFloat('table_max_etabs_model_name_length', 200))
        table_model.show_results(
            data,
            model=table_model.HighPressureColumnModel,
            function=self.etabs.view.show_frame,
            etabs=self.etabs,
            json_file_name=f"HighPressureColumn {self.etabs.get_file_name_without_suffix()[:char_len]}"
            )
        def get_high_pressure_names():
            filt = data['Result'] == True
            df = data.loc[filt]
            return  df['UniqueName']

        group_name = self.form.group_name.text() if self.form.group_checkbox.isChecked() else None
        if group_name:
            frame_names = get_high_pressure_names()
            if len(frame_names) == 0:
                return
            self.etabs.group.add(group_name)
            for name in frame_names:
                self.etabs.SapModel.FrameObj.SetGroupAssign(name, group_name)
        if self.form.select_all.isChecked():
            if group_name is None:
                frame_names = get_high_pressure_names()
            if len(frame_names) == 0:
                return
            self.etabs.view.show_frames(frame_names)

    def reject(self):
        Gui.Control.closeDialog()