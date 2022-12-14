from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model, ex, ey):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'columns_100_30.ui'))
        self.etabs = etabs_model
        self.ex = ex
        self.ey = ey
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
                self.ey,
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
        def get_100_30_names():
                filt = data['Result'] == True
                df = data.loc[filt]
                return  df['UniqueName']

        group_name = self.form.group_name.text() # if self.form.group_checkbox.isChecked() else None
        frame_names = get_100_30_names()
        if group_name:
            if len(frame_names) != 0:
                self.etabs.group.add(group_name)
                for name in frame_names:
                    self.etabs.SapModel.FrameObj.SetGroupAssign(name, group_name)
        # if self.form.select_all.isChecked():
            # if group_name is None:
            #     frame_names = get_100_30_names()
        # if len(frame_names) != 0:
        #     return
        self.etabs.view.show_frames(frame_names)   

    def accept(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0