from pathlib import Path

from PySide import QtGui
import FreeCADGui as Gui

civiltools_path = Path(__file__).absolute().parent.parent.parent

from exporter import civiltools_config 

class Form(QtGui.QWidget):
    def __init__(self, etabs_model, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'columns_100_30.ui'))
        self.etabs = etabs_model
        self.load_config(d)
        self.create_connections()
        self.set_code()

    def load_config(self, d):
        civiltools_config.load(self.etabs, self.form, d)
        self.form.dynamic_groupbox.setChecked(False)

    def create_connections(self):
        self.form.browse.clicked.connect(self.get_filename)
        self.form.concrete_radiobutton.clicked.connect(self.set_code)
        self.form.steel_radiobutton.clicked.connect(self.set_code)
        self.form.check.clicked.connect(self.check)
        self.form.cancel_button.clicked.connect(self.reject)
        self.form.static_groupbox.clicked.connect(self.groupbox_clicked)
        self.form.dynamic_groupbox.clicked.connect(self.groupbox_clicked)

    def groupbox_clicked(self, checked):
        sender = self.sender()
        if sender.objectName().startswith('static'):
            self.form.static_group_x.setEnabled(checked)
            self.form.static_group_y.setEnabled(checked)
            self.form.dynamic_group_x.setEnabled(not checked)
            self.form.dynamic_group_y.setEnabled(not checked)
            self.form.dynamic_groupbox.setChecked(not checked)
        elif sender.objectName().startswith('dynamic'):
            self.form.static_group_x.setEnabled(not checked)
            self.form.static_group_y.setEnabled(not checked)
            self.form.dynamic_group_x.setEnabled(checked)
            self.form.dynamic_group_y.setEnabled(checked)
            self.form.static_groupbox.setChecked(not checked)

    def set_code(self):
        if self.form.concrete_radiobutton.isChecked():
            type_ = 'Concrete'
        elif self.form.steel_radiobutton.isChecked():
            type_ = 'Steel'
        self.code = self.etabs.design.get_code(type_)
        self.form.design_code.setText(self.code)

    def get_filename(self):
        directory = str(self.etabs.get_filepath())
        filename, _ = QtGui.QFileDialog.getSaveFileName(
                    None,
                    'ETABS 100-30 file name',
                    directory,
                    "ETABS(*.EDB)",
                    )
        self.form.filename.setText(filename)

    def check(self):
        filename = self.form.filename.text()
        file_path = Path(filename)
        if file_path.exists():
            filename = file_path
        d = civiltools_config.get_prop_from_widget(self.etabs, self.form)
        if self.form.concrete_radiobutton.isChecked():
            type_ = 'Concrete'
        elif self.form.steel_radiobutton.isChecked():
            type_ = 'Steel'
        if self.form.static_groupbox.isChecked():
            load_names = self.etabs.get_first_system_seismic(d)
        elif self.form.dynamic_groupbox.isChecked():
            load_names = self.etabs.get_dynamic_loadcases(d)
        data = self.etabs.frame_obj.require_100_30(
            load_names,
            filename,
            type_,
            self.code,
        )
        import table_model
        table_model.show_results(
            data,
            model=table_model.Column100_30Model,
            function=self.etabs.view.show_frame,
            etabs=self.etabs,
            json_file_name=f"Column100_30 {self.etabs.get_file_name_without_suffix()}",
            )
        def get_100_30_names(ignore_100_30: bool=True):
            filt = data['Result'] == ignore_100_30
            df = data.loc[filt]
            return  df['UniqueName']

        group_name = "100_30_NotRequired"
        ignore_frame_names = get_100_30_names(True)
        if group_name and len(ignore_frame_names) > 0:
            self.etabs.group.add(group_name, remove=True)
            for name in ignore_frame_names:
                self.etabs.SapModel.FrameObj.SetGroupAssign(name, group_name)
        other_frames = get_100_30_names(False)
        if len(other_frames) > 0:
            group_name = "100_30_Required"
            self.etabs.group.add(group_name, remove=True)
            for name in other_frames:
                self.etabs.SapModel.FrameObj.SetGroupAssign(name, group_name)
        
        self.etabs.view.show_frames(ignore_frame_names)
        create_load_combinations = self.form.create_100_30.isChecked()
        self.reject()
        if create_load_combinations:
            # Gui.runCommand('civiltools_load_combinations')
            import find_etabs
            from py_widget.define import create_load_combinations
            win = create_load_combinations.Form(self.etabs)
            win.form.separate_direction.setChecked(True)
            find_etabs.show_win(win, in_mdi=False)

    def reject(self):
        self.form.close()

    def getStandardButtons(self):
        return 0