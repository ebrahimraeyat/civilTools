from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'control_joint_shear.ui'))
        self.etabs = etabs_model
        self.create_connections()
        self.set_main_file_name()

    def set_main_file_name(self):
        main_file_path = Path(self.etabs.SapModel.GetModelFilename())
        self.main_file_path = main_file_path.with_suffix(".EDB")

    def create_connections(self):
        self.form.check.clicked.connect(self.check)
        self.form.cancel_button.clicked.connect(self.accept)
        self.form.open_main_file_button.clicked.connect(self.open_main_file)

    def open_main_file(self):
        self.etabs.SapModel.File.OpenFile(str(self.main_file_path))
        self.accept()

    def check(self):
        filename = self.form.filename.text()
        file_path = Path(filename)
        if file_path.exists():
            filename = file_path
        open_main_file = self.form.open_main_file.isChecked()
        structure_type = self.form.structure_type_combobox.currentText()
        data = self.etabs.create_joint_shear_file(
            filename,
            structure_type,
            open_main_file=open_main_file,
            )
        if data is None:
            return
        headers = list(data.columns)
        import table_model
        table_model.show_results(
            data,
            headers,
            model=table_model.JointShear,
            function=self.etabs.view.show_frame,
            )
        if open_main_file:
            self.accept()
        else:
            self.form.open_main_file_button.setEnabled(True)
            self.form.check.setEnabled(False)

    def accept(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0