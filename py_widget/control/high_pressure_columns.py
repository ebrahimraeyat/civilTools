from pathlib import Path


from PySide2 import  QtWidgets
import FreeCADGui as Gui

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'high_pressure_columns.ui'))
        self.etabs = etabs_model


    def accept(self):
        data, headers = self.etabs.database.get_hight_pressure_columns()
        import table_model
        table_model.show_results(
            data,
            headers,
            model=table_model.HighPressureColumnModel,
            function=self.etabs.view.show_frame,
            )
        def get_high_pressure_names():
            filt = data['high pressure'] == True
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