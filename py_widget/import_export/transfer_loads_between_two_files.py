import math
from pathlib import Path
import copy

from PySide2.QtWidgets import (
    QMessageBox,
    QFileDialog,
    QComboBox,
    QItemDelegate
)
from PySide2.QtCore import (
    QAbstractTableModel,
    Qt,
    QModelIndex,
    QSize,
)

import FreeCADGui as Gui

import etabs_obj

        
civiltools_path = Path(__file__).parent.parent.parent


class Form:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'import_export' / 'transfer_loads_between_two_files.ui'))
        self.model1 = None
        self.model2 = None
        self.create_connections()

    def create_connections(self):
        self.form.open_model1.clicked.connect(self.open_model1)
        self.form.open_model2.clicked.connect(self.open_model2)
        self.form.transfer.clicked.connect(self.transfer)

    def open_model1(self):
        name, software = self.browse()
        self.form.model1_name.setText(name)
        if self.model1 is not None and hasattr(self.model1, "close_etabs"):
            self.model1.close_etabs()
        self.model1 = software
        self.populate_loadcase_table()
    
    def open_model2(self):
        name, software = self.browse()
        self.form.model2_name.setText(name)
        if self.model2 is not None and hasattr(self.model2, "close_etabs"):
            self.model2.close_etabs()
        self.model2 = software
        self.populate_loadcase_table()

    def browse(self):
        filters = "ETABS (*.EDB);;Sap 2000 (*.sdb)"
        filename, _ = QFileDialog.getOpenFileName(None, 'Select File',
                                                None, filters)
        if not filename:
            return
        name = str(Path(filename).name)
        ext = Path(name).suffix
        software_name = "ETABS"
        if ext.lower() == '.edb':
            software_name = "ETABS"
        elif ext.lower() == '.sdb':
            software_name = "SAP2000"
        software = etabs_obj.EtabsModel(
            attach_to_instance=False,
            backup=False,
            software=software_name,
            model_path=filename,
            )
        return name, software

    def populate_loadcase_table(self):
        if self.model1 and self.model2:
            left_loadcases = self.model1.load_cases.get_loadcase_withtype(1) # static loadcase
            right_loadcases = self.model2.load_cases.get_loadcase_withtype(1) # static loadcase
            left_loadcases.append('None')
            right_loadcases.append('None')
            model = TransferLoadsTableModel(
                left_loadcases, right_loadcases)
            self.form.loadcases_tableview.setModel(model)
            self.form.loadcases_tableview.setItemDelegate(TransferLoadsDelegate())


    def transfer(self):
        import points_functions
        level1 = float(self.form.model1_level_combobox.currentText())
        level2 = float(self.form.model2_level_combobox.currentText())
        map_dict = self.get_map_loadcase()
        replace = self.form.replace_checkbox.isChecked()
        ret = points_functions.transfer_loads_between_two_models(
            self.model1,
            self.model2,
            level1,
            level2,
            map_dict,
            replace,
            )
        if len(ret) == 0:
            name1 = self.model1.get_file_name_without_suffix()
            name2 = self.model2.get_file_name_without_suffix()
            QMessageBox.information(
                None,
                'Successful',
                f'All Load Cases transfered from {name1} Model to {name2} Model')

    def get_map_loadcase(self):
        lc_model = self.form.loadcases_tableview.model()
        map_dict = {}
        for row in range(lc_model.rowCount()):
            if lc_model.check_state[row]:
                index = lc_model.index(row, 0)
                lc1 = lc_model.data(index)
                if lc1 in lc_model.all_left_loadcases:
                    index = lc_model.index(row, 1)
                    lc2 = lc_model.data(index)
                    if lc2 in lc_model.all_right_loadcases:
                        map_dict[lc1] = lc2
        return map_dict

    def getStandardButtons(self):
        return 0
    
    def reject(self):
        self.form.reject()



class TransferLoadsTableModel(QAbstractTableModel):

    def __init__(self,
                 left_loadcases: list,
                 right_loadcases: list,
                 ):
        super().__init__()
        self.left_loadcases = left_loadcases[:-1]
        self.right_loadcases = right_loadcases[:-1]
        self.all_left_loadcases = copy.deepcopy(left_loadcases)
        self.all_right_loadcases = copy.deepcopy(right_loadcases)
        self.columns = {
            0: "left_lc",
            1: "right_lc",
        }
        self.check_state = [True] * len(left_loadcases)

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
        # col = index.column()
        # if col == 0:
        #     return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return self.left_loadcases[row]
            elif col == 1:
                return self.right_loadcases[row]
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
            if col == 0:
                self.left_loadcases[row] = str(value)
                self.dataChanged.emit(index, index)
                return True
            elif col == 1:
                self.right_loadcases[row] = str(value)
                self.dataChanged.emit(index, index)
                return True
        return False

    def rowCount(self, index=QModelIndex()):
        return min(len(self.left_loadcases), len(self.right_loadcases))

    def columnCount(self, index=QModelIndex()):
        return 2


class TransferLoadsDelegate(QItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = parent

    def createEditor(self, parent, option, index):
        col = index.column()
        load_case = index.model().data(index)
        combobox = QComboBox(parent)
        if col in (0, 1):
            if col == 0:
                all_loadcases = index.model().all_left_loadcases
            elif col == 1:
                all_loadcases = index.model().all_right_loadcases
            combobox.addItems(all_loadcases)
            loadcase_index = combobox.findText(load_case)
            combobox.setCurrentIndex(loadcase_index)
            # combobox.setEditable(True)
            return combobox
        else:
            return QItemDelegate.createEditor(self, parent, option, index)

    # def setEditorData (self, editor, index):
    #     row = index.row()
    #     col = index.column()
    #     # value = index.model().items[row][column]
    #         editor.setCurrentIndex(index.row())

    def setModelData(self, editor, model, index):
        col = index.column()
        if col in (0, 1):
            model.setData(index, editor.currentText())

    def sizeHint(self, option, index):
        fm = option.fontMetrics
        return QSize(fm.width("2IPE14FPL200X10WP"), fm.height())