from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model, ex, exn, exp, ey, eyn, eyp):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'columns_100_30.ui'))
        self.etabs = etabs_model
        self.ex = ex
        self.exn = exn
        self.exp = exp
        self.ey = ey
        self.eyn = eyn
        self.eyp = eyp
        self.create_connections()
        self.set_code()

    def create_connections(self):
        self.form.browse.clicked.connect(self.get_filename)
        self.form.structure_type.currentIndexChanged.connect(self.set_code)
        self.form.check.clicked.connect(self.check)
        self.form.cancel_button.clicked.connect(self.accept)

    def set_code(self):
        self.type_ = self.form.structure_type.currentText()
        self.code = self.etabs.design.get_code(self.type_)
        self.form.design_code.setText(self.code)

    def get_filename(self):
        directory = str(self.etabs.get_filepath())
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
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
        data = self.etabs.frame_obj.require_100_30(
                self.ex,
                self.exn,
                self.exp,
                self.ey,
                self.eyn,
                self.eyp,
                filename,
                self.type_,
                self.code,
            )
        headers = list(data.columns)
        import table_model
        table_model.show_results(
            data,
            headers,
            model=table_model.Column100_30Model,
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
        Gui.Control.closeDialog()
        if create_load_combinations:
            # Gui.runCommand('civiltools_load_combinations')
            import find_etabs
            from py_widget.define import create_load_combinations
            win = create_load_combinations.Form(self.etabs)
            win.form.separate_direction.setChecked(True)
            find_etabs.show_win(win, in_mdi=False)


    def accept(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0