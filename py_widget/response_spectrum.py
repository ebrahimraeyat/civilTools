from pathlib import Path

from PySide2 import  QtWidgets, QtCore
import FreeCADGui as Gui
from PySide2.QtWidgets import QComboBox, QItemDelegate
from PySide2.QtCore import QAbstractTableModel, Qt, QSize, QModelIndex

civiltools_path = Path(__file__).absolute().parent.parent

from exporter import civiltools_config




class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'response_spectrum.ui'))
        self.etabs = etabs_obj
        self.angular_model = None
        # self.fill_100_30_fields(d)
        # self.select_spect_loadcases()
        self.load_config(d)
        self.create_connections()

    def create_connections(self):
        self.form.combination.clicked.connect(self.reset_widget)
        self.form.angular.clicked.connect(self.reset_widget)
        self.form.angular.clicked.connect(self.fill_angular_fields)
        self.form.run.clicked.connect(self.accept)

    def load_config(self, d):
        civiltools_config.load(self.etabs, self.form, d)

    def reset_widget(self, checked):
        sender = self.sender()
        if sender == self.form.combination:
            self.form.tableView.setEnabled(not checked)
            self.form.angular.setChecked(not checked)
            self.form.x_dynamic_loadcase_list.setEnabled(checked)
            self.form.y_dynamic_loadcase_list.setEnabled(checked)
            self.form.y_scalefactor_combobox.setEnabled(checked)
        elif sender == self.form.angular:
            self.form.combination.setChecked(not checked)
            self.form.tableView.setEnabled(checked)
            self.form.x_dynamic_loadcase_list.setEnabled(not checked)
            self.form.y_dynamic_loadcase_list.setEnabled(not checked)
            self.form.y_scalefactor_combobox.setEnabled(not checked)

    def accept(self):
        ex_name = self.form.ex_combobox.currentText()
        ey_name = self.form.ey_combobox.currentText()
        x_scale_factor = float(self.form.x_scalefactor_combobox.currentText())
        y_scale_factor = float(self.form.y_scalefactor_combobox.currentText())
        num_iteration = self.form.iteration.value()
        tolerance = self.form.tolerance.value()
        reset = self.form.reset.isChecked()
        analyze = self.form.analyze.isChecked()
        consider_min_static_base_shear = self.form.consider_min_static_base_shear.isChecked()
        if self.form.angular.isChecked():
            way = "angular"
            angular_specs = []
            section_cuts = []
            for row in range(self.angular_model.rowCount()):
                index = self.angular_model.index(row, 1)
                spec = self.angular_model.data(index)
                angular_specs.append(spec)
                index = self.angular_model.index(row, 2)
                sec_cut = self.angular_model.data(index)
                section_cuts.append(sec_cut)
            _, df = self.etabs.angles_response_spectrums_analysis(
                ex_name,
                ey_name,
                angular_specs,
                section_cuts,
                x_scale_factor,
                num_iteration,
                tolerance,
                reset,
                analyze,
            )
        else:
            x_specs, y_specs = self.get_load_cases()
            way = "100-30"
            _, _, df = self.etabs.scale_response_spectrums(
                ex_name,
                ey_name,
                x_specs,
                y_specs,
                x_scale_factor,
                y_scale_factor,
                num_iteration,
                tolerance,
                reset,
                analyze,
                consider_min_static_base_shear,
            )
        import table_model
        table_model.show_results(df, table_model.BaseShearModel,
                                 etabs=self.etabs,
                                 json_file_name=f"BaseShear{way.capitalize()}")
        self.form.close()

    def get_load_cases(self):
        x_loadcases = []
        y_loadcases = []
        lw = self.form.x_dynamic_loadcase_list
        for i in range(lw.count()):
            item = lw.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                x_loadcases.append(item.text())
        lw = self.form.y_dynamic_loadcase_list
        for i in range(lw.count()):
            item = lw.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                y_loadcases.append(item.text())
        return x_loadcases, y_loadcases

    def reject(self):
        import FreeCADGui as Gui
        Gui.Control.closeDialog()

    def select_spect_loadcases(self):
        for lw in (self.form.x_dynamic_loadcase_list, self.form.y_dynamic_loadcase_list):
            for i in range(lw.count()):
                item = lw.item(i)
                item.setSelected(True)
    
    def fill_angular_fields(self):
        if self.angular_model is not None:
            return
        all_response_spectrums = self.etabs.load_cases.get_response_spectrum_loadcase_name()
        section_cuts_angles = self.etabs.database.get_section_cuts_angle()
        angles = list(section_cuts_angles.values())
        angles_spectral = self.etabs.load_cases.get_spectral_with_angles(angles)
        section_cuts = []
        specs = []
        angles = []
        for angle, spec in angles_spectral.items():
            for sec_cut, ang in section_cuts_angles.items():
                if int(angle) == int(ang):
                    specs.append(spec)
                    section_cuts.append(sec_cut)
                    angles.append(ang)
                    break
        self.angular_model = AngularTableModel(
            angles=angles,
            specs=specs,
            section_cuts=section_cuts,
            all_response_spectrums=all_response_spectrums,
            )
        self.form.tableView.setModel(self.angular_model)
        self.form.tableView.setItemDelegate(AngularDelegate(self.form))


class AngularTableModel(QAbstractTableModel):

    def __init__(self,
                 angles: list,
                 specs: list,
                 section_cuts: list,
                 all_response_spectrums: list,
                 ):
        super().__init__()
        self.angles = angles
        self.specs = specs
        self.section_cuts = section_cuts
        self.all_response_spectrums = all_response_spectrums
        self.columns = {
            0: "Angle",
            1: "Spec",
            2: "Section Cut"
        }
        self.check_state = [True] * len(angles)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignHCenter | Qt.AlignVCenter)
            return int(Qt.AlignRight | Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return

        if orientation == Qt.Horizontal:
            return self.columns[section]
        # if orientation == Qt.Vertical:
        #     return ""

    def checkState(self, row):
        if self.check_state[row]:
            return Qt.Checked
        else:
            return Qt.Unchecked

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        col = index.column()
        if col == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return self.angles[row]
            elif col == 1:
                return self.specs[row]
            elif col == 2:
                return self.section_cuts[row]
        if role == Qt.CheckStateRole and col == 0:
            return self.checkState(row)
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        col = index.column()
        row = index.row()
        if role == Qt.CheckStateRole and col == 0:
            self.check_state[row] = value
            self.dataChanged.emit(index, index)
            return True
        if role == Qt.EditRole:
            if col == 1:
                self.specs[row] = str(value)
                self.dataChanged.emit(index, index)
                return True
            elif col == 2:
                self.section_cuts[row] = str(value)
                self.dataChanged.emit(index, index)
                return True
        return False

    def rowCount(self, index=QModelIndex()):
        return len(self.angles)

    def columnCount(self, index=QModelIndex()):
        return 3



class AngularDelegate(QItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = parent

    def createEditor(self, parent, option, index):
        col = index.column()
        if col == 1:
            spec = index.model().data(index)
            combobox = QComboBox(parent)
            all_response_spectrums = index.model().all_response_spectrums
            combobox.addItems(all_response_spectrums)
            spec_index = combobox.findText(spec)
            combobox.setCurrentIndex(spec_index)
            # combobox.setEditable(True)
            return combobox
        if col == 2:
            sec_cut = index.model().data(index)
            combobox = QComboBox(parent)
            section_cuts = index.model().section_cuts
            combobox.addItems(section_cuts)
            # combobox.setEditable(True)
            sec_cut_index = combobox.findText(sec_cut)
            combobox.setCurrentIndex(sec_cut_index)
            return combobox
        else:
            return QItemDelegate.createEditor(self, parent, option, index)

    # def setEditorData(self, editor, index):
    #     row = index.row()
    #     col = index.column()
    #     # value = index.model().items[row][column]
    #         editor.setCurrentIndex(index.row())

    def setModelData(self, editor, model, index):
        col = index.column()
        if col in (1, 2):
            model.setData(index, editor.currentText())

    def sizeHint(self, option, index):
        fm = option.fontMetrics
        return QSize(fm.width("2IPE14FPL200X10WP"), fm.height())

