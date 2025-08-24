from pathlib import Path

from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


civiltools_path = Path(__file__).parent.parent.parent


class Form:
    
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'import_export' / 'export_dwg_to_pdf.ui'))
        # self.fill_plot_styles()
        self.create_connections()

    # def fill_plot_styles(self):
    #     styles = doc.ActiveLayout.GetPlotStyleTableNames()
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

    def get_selected_layout(self):
        if self.form.left_up_vertical.isChecked():
            checked_button = self.form.left_up_vertical
        if self.form.right_up_vertical.isChecked():
            checked_button = self.form.right_up_vertical
        if self.form.left_down_vertical.isChecked():
            checked_button = self.form.left_down_vertical
        if self.form.right_down_vertical.isChecked():
            checked_button = self.form.right_down_vertical
        if self.form.left_up_horizontal.isChecked():
            checked_button = self.form.left_up_horizontal
        if self.form.right_up_horizontal.isChecked():
            checked_button = self.form.right_up_horizontal
        if self.form.left_down_horizontal.isChecked():
            checked_button = self.form.left_down_horizontal
        if self.form.right_down_horizontal.isChecked():
            checked_button = self.form.right_down_horizontal
        horizontal, vertical, prefer_dir = checked_button.objectName().split("_")
        return horizontal, vertical, prefer_dir

    # def browse(self):
    #     ext = '.dxf'
    #     from PySide.QtGui import QFileDialog
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
        horizontal, vertical, prefer_dir = self.get_selected_layout()
        way = self.form.way_combobox.currentText()
        remove_pdf = self.form.remove_pdf_checkbox.isChecked()
        filename = dwg_to_pdf.export_dwg_to_pdf(
            horizontal,
            vertical,
            prefer_dir=prefer_dir,
            remove_pdfs=remove_pdf,
            way = int(way),
            )
        if filename is None:
            QMessageBox.warning(None, 'Selection', 'Please select some blocks in Autocad File.')
            return

        from civiltools_python_functions import open_file
        open_file(filename)


    def getStandardButtons(self):
        return 0
    
    def reject(self):
        self.form.reject()
