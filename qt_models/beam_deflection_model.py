from pathlib import Path
from PySide2.QtCore import QAbstractTableModel, Qt 
from PySide2.QtGui import QColor #, QIcon
from PySide2 import QtWidgets
from PySide2.QtCore import QModelIndex #, QIcon

# from qt_models import table_models


civiltools_path = Path(__file__).absolute().parent

low = 'cyan'
intermediate = 'yellow'
high = 'red'



column_count = 10
NAME, STORY, IS_CONSOLE, ADD_TORSION_REBAR, ADD_REBAR, MINUS_LENGTH, COVER, WIDTH, HEIGHT, RESULT = range(column_count)


class BeamDeflectionTableModel(QAbstractTableModel):

    def __init__(self, beam_data, parent=None):
        '''
        beam_data : dict with keys = beam_name and value is dict of properties
        '''
        super().__init__()
        self.beam_data = beam_data
        self.beam_names = list(self.beam_data.keys())
        self.set_initial_data()

    def set_initial_data(self):
        self.is_consoles = []
        self.add_torsions_rebar = []
        for beam_name in self.beam_names:
            self.is_consoles.append(self.beam_data[beam_name]['is_console'])
            self.add_torsions_rebar.append(self.beam_data[beam_name]['add_torsion_rebar'])
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignHCenter | Qt.AlignVCenter)
            return int(Qt.AlignRight | Qt.AlignVCenter)
        elif role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            if section == NAME:
                return "Name"
            if section == STORY:
                return "Story"
            if section == IS_CONSOLE:
                return "Console"
            if section == ADD_TORSION_REBAR:
                return "Torsion Rebar"
            if section == ADD_REBAR:
                return "Add Rebar"
            if section == MINUS_LENGTH:
                return "Minus Length"
            if section == COVER:
                return "Cover"
            if section == WIDTH:
                return "Width"
            if section == HEIGHT:
                return "Height"
            if section == RESULT:
                return "Result"
        if orientation == Qt.Vertical:
            return str(section + 1)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        col = index.column()
        if col in (IS_CONSOLE, ADD_TORSION_REBAR):
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        if col in (NAME, STORY, RESULT):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        beam_name = self.beam_names[row]
        beam_prop = self.beam_data[beam_name]
        # Complete data access and population logic from beam_data
        if role == Qt.DisplayRole:
            if col == NAME:
                return beam_name
            if col == STORY:
                return beam_prop['Story']
            elif col == ADD_REBAR:
                return beam_prop["add_rebar"]
            elif col == MINUS_LENGTH:
                return beam_prop["minus_length"]
            elif col == COVER:
                return beam_prop["cover"]
            elif col == WIDTH:
                return beam_prop["width"]
            elif col == HEIGHT:
                return beam_prop["height"]
            elif col == RESULT:
                return beam_prop["result"]
        if role == Qt.CheckStateRole:
            if col == IS_CONSOLE:
                return beam_prop["is_console"]
            if col == ADD_TORSION_REBAR:
                return beam_prop["add_torsion_rebar"]

        # if role == Qt.DecorationRole:
        #     value = self._data[index.row()][index.column()]
        #     if isinstance(value, float):
        #         return QtGui.QIcon('calendar.png')
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        col = index.column()
        row = index.row()
        beam_name = self.beam_names[row]
        if role == Qt.CheckStateRole and col in (IS_CONSOLE, ADD_TORSION_REBAR):
            if col == IS_CONSOLE:
                self.beam_data[beam_name]['is_console'] = value
            elif col == ADD_TORSION_REBAR:
                self.beam_data[beam_name]['add_torsion_rebar'] = value
        elif role == Qt.EditRole:
            if col == RESULT:
                self.beam_data[beam_name]['result'] = str(value)
            elif col == ADD_REBAR:
                self.beam_data[beam_name]['add_rebar'] = float(value)
            elif col == MINUS_LENGTH:
                self.beam_data[beam_name]['minus_length'] = float(value)
            elif col == COVER:
                self.beam_data[beam_name]['cover'] = float(value)
            elif col == WIDTH:
                self.beam_data[beam_name]['width'] = float(value)
            elif col == HEIGHT:
                self.beam_data[beam_name]['height'] = float(value)
        return False

    def rowCount(self, index=QModelIndex()):
        return len(self.beam_names)

    def columnCount(self, index=QModelIndex()):
        return column_count

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.table = QtWidgets.QTableView()
        data = {'1':
        {'is_console': 2,
        'Story': 'STORY1',
        'minus_length': 30,
        'add_torsion_rebar': 0,
        'add_rebar': 5,
        'cover': 4,
        'width': 40,
        'height': 50,
        'result': ''}}
        self.model = BeamDeflectionTableModel(data)
        self.table.setModel(self.model)
        self.setCentralWidget(self.table)


    

if __name__ == "__main__":
    import sys
    app=QtWidgets.QApplication(sys.argv)
    window=MainWindow()
    window.show()
    app.exec_()


# class ColumnDelegate(QItemDelegate):

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.ui = parent

#     def createEditor(self, parent, option, index):
#         col = index.column()
#         if col == 1:
#             combobox = QComboBox(parent)
#             size = self.ui.ipe_size.currentText()
#             sections = index.model().level_obj.sections_name
#             sections_with_current_size = [section for section in sections if f"IPE{size}" in section]
#             if not sections_with_current_size:
#                 sections_with_current_size = [f"2IPE{size}"]
#             combobox.addItems(sections_with_current_size)
#             # combobox.setEditable(True)
#             return combobox
#         else:
#             return QItemDelegate.createEditor(self, parent, option, index)

#     # def setEditorData(self, editor, index):
#     #     row = index.row()
#     #     col = index.column()
#     #     # value = index.model().items[row][column]
#     #         editor.setCurrentIndex(index.row())

#     def setModelData(self, editor, model, index):
#         col = index.column()
#         if col == 1:
#             model.setData(index, editor.currentText())

#     def sizeHint(self, option, index):
#         fm = option.fontMetrics
#         return QSize(fm.width("2IPE14FPL200X10WPL200X10"), fm.height())



# class SectionDelegate(QItemDelegate):
#     def __init__(self, parent=None):
#         super(SectionDelegate, self).__init__(parent)

#     def createEditor(self, parent, option, index):
#         if index.column() == NAME:
#             editor = QLineEdit(parent)
#             editor.returnPressed.connect(self.commitAndCloseEditor)
#             return editor
#         else:
#             # spinbox = QDoubleSpinBox(parent)
#             # return spinbox
#             return QItemDelegate.createEditor(self, parent, option,
#                                               index)

#     def setEditorData(self, editor, index):
#         text = index.model().data(index, Qt.DisplayRole)
#         if index.column() == NAME:
#             editor.setText(text)

#         else:
#             # editor.setValue(float(text))
#             QItemDelegate.setEditorData(self, editor, index)

#     def commitAndCloseEditor(self):
#         editor = self.sender()
#         if isinstance(editor, (QTextEdit, QLineEdit)):
#             self.commitData.emit(editor)
#             self.closeEditor.emit(editor)
