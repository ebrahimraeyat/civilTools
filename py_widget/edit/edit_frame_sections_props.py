from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui
import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'edit' / 'edit_frame_sections_props.ui'))
        self.etabs = etabs_model
        self.fill_stories()
        self.fill_concretes()
        self.create_connections()

    def fill_stories(self):
        stories = self.etabs.SapModel.Story.GetNameList()[1]
        self.form.stories.addItems(stories)
        item = self.form.stories.item(0)
        item.setSelected(True)

    def fill_concretes(self):
        concretes = self.etabs.material.get_material_of_type(2)
        if concretes:
            self.form.concrete_mats.addItems(concretes)
            self.concrete_changed()

    def concrete_changed(self):
        conc_name = self.form.concrete_mats.currentText()
        suffix = f"_{conc_name}"
        self.form.suffix.setText(suffix)

    def create_connections(self):
        self.form.assign_pushbutton.clicked.connect(self.assign)
        # self.form.cancel_button.clicked.connect(self.reject)
        self.form.concrete_mats.currentIndexChanged.connect(self.concrete_changed)
        self.form.selection_checkbox.clicked.connect(self.selection_clicked)

    def selection_clicked(self, checked):
        if checked:
            self.form.columns.setChecked(True)
            self.form.beams.setChecked(True)
        self.form.stories.setEnabled(not checked)

    def assign(self):
        self.etabs.unlock_model()
        if self.form.selection_checkbox.isChecked():
            names = self.etabs.select_obj.get_selected_obj_type(2) # get all selected frames
        else:
            stories = [item.text() for item in self.form.stories.selectedItems()]
            beams, names = self.etabs.frame_obj.get_beams_columns(type_=2, stories=stories)
            names.extend(beams)
        frame_types = []
        if self.form.columns.isChecked():
            frame_types.append('column')
        if self.form.beams.isChecked():
            frame_types.append('beam')
        if len(frame_types) == 0:
            QtWidgets.QMessageBox.warning(None, 'Selection ', 'Please Select type of frames.')
            return
        conc_name = self.form.concrete_mats.currentText()
        suffix = self.form.suffix.text()
        prefix = self.form.prefix.text()
        clean_names = self.form.clean_names_checkbox.isChecked()
        etabs_main_version = self.etabs.etabs_main_version
        ret, convert_names, section_that_corner_bars_is_different = self.etabs.prop_frame.change_beams_columns_section_fc(
            names,
            conc_name,
            suffix,
            clean_names,
            frame_types,
            prefix,
            apply_with_tables_if_needed=True if etabs_main_version > 19 else False,
            )
        if ret:
            self.etabs.view.refresh_view()
            msg = f"{len(convert_names)} Sections replaced:\n"
            for key, value in convert_names.items():
                msg += f"{key}\t\t ==> {value}\n"
                title = 'Done'
        else:
            msg = "Some Error Occured, Please try againg."
            title = 'Failed'
        QtWidgets.QMessageBox.information(None, title, str(msg))
        if len(section_that_corner_bars_is_different) > 0 and etabs_main_version < 20:
            print(f"{section_that_corner_bars_is_different=}")
            msg = f"{len(section_that_corner_bars_is_different)} Sections have different Corner Bar Size, Edit those in Etabs Model Manually:\n"
            for i, sec in enumerate(section_that_corner_bars_is_different):
                msg += f"{i + 1} ==> \t\t{sec}\n"
                title = 'Change Corner Bar Size'
            QtWidgets.QMessageBox.information(None, title, str(msg))

        # lens = [len(name) for name in convert_names.values()]
        # if max(lens) > 12:
        #     msg = "Some Sections have more than 12 Charachter, maybe error occured in drawing with SAZE 90"
        #     QtWidgets.QMessageBox.information(None, "Max Section Name", str(msg))

    def getStandardButtons(self):
        return 0
