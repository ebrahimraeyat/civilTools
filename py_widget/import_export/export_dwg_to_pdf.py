from pathlib import Path

from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui


civiltools_path = Path(__file__).parent.parent.parent


class Form:

    def __init__(self, etabs_model):
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'import_export' / 'export_dwg_to_pdf.ui'))
        self.etabs = etabs_model
        # self.fill_filename()
        self.create_connections()

    # def fill_filename(self):
    #     try:
    #         name = self.etabs.get_filename().with_suffix('.dxf')
    #     except:
    #         name = ''
    #     self.form.filename.setText(str(name))

    def create_connections(self):
        # self.form.browse.clicked.connect(self.browse)
        self.form.select_blocks_button.clicked.connect(self.export)
        self.form.cancel_pushbutton.clicked.connect(self.reject)

    # def browse(self):
    #     ext = '.dxf'
    #     from PySide2.QtWidgets import QFileDialog
    #     filters = f"{ext[1:]} (*{ext})"
    #     filename, _ = QFileDialog.getSaveFileName(None, 'select file',
    #                                             None, filters)
    #     if not filename:
    #         return
    #     if not filename.lower().endswith(ext):
    #         filename += ext
    #     self.form.filename.setText(filename)

    def export(self):
        from functions import dwg_to_pdf
        horizontal_combobox = self.form.horizontal_combobox.currentText()
        vertical_combobox = self.form.vertical_combxbox.currentText()
        if self.form.vertical_radiobutton.isChecked():
            pref = "vertical"
        else:
            pref = "horizontal"
        remove_pdf = self.form.remove_pdf_checkbox.isChecked()
        filename = dwg_to_pdf.export_dwg_to_pdf(
            horizontal_combobox,
            vertical_combobox,
            prefer_dir=pref,
            remove_pdfs=remove_pdf,
            )
        if filename is None:
            QMessageBox.warning(None, 'Selection', f'Please select some blocks in Autocad File.')

        from civiltools_python_functions import open_file
        open_file(filename)
        # else:

    def getStandardButtons(self):
        return 0
    
    def reject(self):
        self.form.reject()
