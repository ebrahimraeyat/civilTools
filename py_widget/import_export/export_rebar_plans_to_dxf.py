from pathlib import Path

from PySide.QtGui import QMessageBox

import FreeCADGui as Gui
import os, random, string


civiltools_path = Path(__file__).parent.parent.parent


class Form:

    def __init__(self, etabs_model):
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'import_export' / 'export_rebar_plans_to_dxf.ui'))
        self.etabs = etabs_model
        self.fill_filename()
        self.create_connections()

    def get_filename(self):
        try:
            top_rebars=self.form.top_rebars.text()
            bot_rebars=self.form.bot_rebars.text()
            torsion_rebars=self.form.torsion_rebars.text()
            name = f"{top_rebars}__{bot_rebars}__{torsion_rebars}_____" + ''.join(random.choices(string.ascii_letters + string.digits, k=5)) + '.dxf'
            file_path = self.etabs.get_filepath()
            folder_path = file_path / 'plans'
            if not folder_path.exists():
                os.mkdir(str(folder_path))
            filename = folder_path / name
        except:
            filename = ''
        return filename
    
    def fill_filename(self):
        filename = self.get_filename()
        self.form.filename.setText(str(filename))

    def create_connections(self):
        # TOP Rebars
        self.form.top_number_1.valueChanged.connect(self.set_top_rebars)
        self.form.top_phi_1.currentIndexChanged.connect(self.set_top_rebars)
        self.form.top_number_2.valueChanged.connect(self.set_top_rebars)
        self.form.top_phi_2.currentIndexChanged.connect(self.set_top_rebars)
        self.form.top_rebars.textChanged.connect(self.fill_filename)
        # BOT Rebars
        self.form.bot_number_1.valueChanged.connect(self.set_bot_rebars)
        self.form.bot_phi_1.currentIndexChanged.connect(self.set_bot_rebars)
        self.form.bot_number_2.valueChanged.connect(self.set_bot_rebars)
        self.form.bot_phi_2.currentIndexChanged.connect(self.set_bot_rebars)
        self.form.bot_rebars.textChanged.connect(self.fill_filename)
        # TORSION Rebars
        self.form.torsion_number.valueChanged.connect(self.set_torsion_rebars)
        self.form.torsion_phi.currentIndexChanged.connect(self.set_torsion_rebars)
        self.form.torsion_rebars.textChanged.connect(self.fill_filename)

        self.form.browse.clicked.connect(self.browse)
        self.form.export_button.clicked.connect(self.export)
        self.form.cancel_pushbutton.clicked.connect(self.reject)

    def set_top_rebars(self):
        top_number_1 = self.form.top_number_1.value()
        top_phi_1 = int(self.form.top_phi_1.currentText())
        top_rebars = f"{top_number_1}~{top_phi_1}"
        top_number_2 = self.form.top_number_2.value()
        if top_number_2:
            top_phi_2 = int(self.form.top_phi_2.currentText())
            top_rebars += f"+{top_number_2}~{top_phi_2}"
        self.form.top_rebars.setText(top_rebars)
    
    def set_bot_rebars(self):
        bot_number_1 = self.form.bot_number_1.value()
        bot_phi_1 = int(self.form.bot_phi_1.currentText())
        bot_rebars = f"{bot_number_1}~{bot_phi_1}"
        bot_number_2 = self.form.bot_number_2.value()
        if bot_number_2:
            bot_phi_2 = int(self.form.bot_phi_2.currentText())
            bot_rebars += f"+{bot_number_2}~{bot_phi_2}"
        self.form.bot_rebars.setText(bot_rebars)
    
    def set_torsion_rebars(self):
        torsion_number = self.form.torsion_number.value()
        if torsion_number:
            torsion_phi = int(self.form.torsion_phi.currentText())
            torsion_rebars = f"{torsion_number}~{torsion_phi}"
        else:
            torsion_rebars = ''
        self.form.torsion_rebars.setText(torsion_rebars)



    def browse(self):
        ext = '.dxf'
        from PySide.QtGui import QFileDialog
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
        top_rebars = self.form.top_rebars.text()
        bot_rebars = self.form.bot_rebars.text()
        torsion_rebars = self.form.torsion_rebars.text()
        ignore_area = self.form.ignore_area.value()
        if not torsion_rebars:
            torsion_rebars = '0~16'
        if not filename:
            return
        from etabs_api_export import export_plans_to_dxf as ex
        if self.form.moment_redistribution_groupbox.isChecked():
            moment_redistribution_positive_coefficient = self.form.moment_redistribution_positive_coefficient.value()
            moment_redistribution_negative_coefficient = self.form.moment_redistribution_negative_coefficient.value()
        else:
            moment_redistribution_positive_coefficient = 1
            moment_redistribution_negative_coefficient = 1

        if self.form.selection_checkbox.isChecked():
            names = self.etabs.select_obj.get_selected_obj_type(2)
            if len(names) == 0:
                self.etabs.select_obj.get_previous_selection()
                names = self.etabs.select_obj.get_selected_obj_type(2)
            if len(names) == 0:
                QMessageBox.warning(None, "Concrete Beams Selection", "There is no conctete beams Selected in ETABS Model.")
                return
            
        else:
            names, _ = self.etabs.frame_obj.get_beams_columns()
            if len(names) == 0:
                QMessageBox.warning(None, "Concrete Beams", "There is no conctete beams in ETABS Model.")
                return

        ex.export_to_dxf_beam_rebars(
            frame_names=names,
            etabs=self.etabs,
            Open_file=False,
            top_rebars=top_rebars,
            bot_rebars=bot_rebars,
            torsion_rebar=torsion_rebars,
            filename=filename,
            moment_redistribution_positive_coefficient = moment_redistribution_positive_coefficient,
            moment_redistribution_negative_coefficient = moment_redistribution_negative_coefficient,
            ignore_rebar_area=ignore_area,
                    )
        if self.form.open_checkbox.isChecked():
            from civiltools_python_functions import open_file
            open_file(filename)
        else:
            QMessageBox.information(None, 'Successful', f'Model has been exported to {filename}')

    def getStandardButtons(self):
        return 0
    
    def reject(self):
        self.form.reject()
