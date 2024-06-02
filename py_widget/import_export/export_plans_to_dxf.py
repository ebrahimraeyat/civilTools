from pathlib import Path

from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui


civiltools_path = Path(__file__).parent.parent.parent


class Form:

    def __init__(self, etabs_model):
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'import_export' / 'export_plans_to_dxf.ui'))
        self.etabs = etabs_model
        self.fill_filename()
        self.create_connections()

    def fill_filename(self):
        try:
            name = self.etabs.get_filename().with_suffix('.dxf')
        except:
            name = ''
        self.form.filename.setText(str(name))

    def create_connections(self):
        self.form.browse.clicked.connect(self.browse)
        self.form.export_button.clicked.connect(self.export)
        self.form.cancel_pushbutton.clicked.connect(self.reject)

    def browse(self):
        ext = '.dxf'
        from PySide2.QtWidgets import QFileDialog
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        self.form.filename.setText(filename)

    def export(self):
        filename = self.form.filename.text()
        if not filename:
            return
        from etabs_api_export import export_plans_to_dxf as ex
        ex.export_to_dxf(etabs=self.etabs, filename=filename)
        if self.form.open_checkbox.isChecked():
            from civiltools_python_functions import open_file
            open_file(filename)
        else:
            QMessageBox.information(None, 'Successful', f'Model has been exported to {filename}')

    def getStandardButtons(self):
        return 0
    
    def reject(self):
        self.form.reject()
