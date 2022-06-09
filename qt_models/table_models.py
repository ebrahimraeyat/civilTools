from pathlib import Path
from PySide2.QtCore import QAbstractTableModel, Qt 
from PySide2.QtGui import QColor #, QIcon
from PySide2.QtCore import QModelIndex #, QIcon

from qt_models import table_models


civiltools_path = Path(__file__).absolute().parent

low = 'cyan'
intermediate = 'yellow'
high = 'red'



column_column_count = 7
beam_column_count = 3
NAME, WIDTH, HEIGHT, N, M, TOTAL, RHO = range(column_column_count)


class ConcreteColumnSectionTableModel(QAbstractTableModel):

    def __init__(
        self,
        sections: list,
        filename='',
        # type_='BEAM',
        ):
        super(ConcreteColumnSectionTableModel, self).__init__()
        self.filename = filename
        self.dirty = False
        self.sections = sections
        self.names = set()
        # self.type_ = type_

    def sort(self, col, order):
        """Sort table by given column number."""
        self.layoutAboutToBeChanged.emit()
        if col == table_models.WIDTH:
            self.sections.sort(key=lambda x: x.B.Value, reverse= order == Qt.AscendingOrder)
        elif col == table_models.HEIGHT:
            self.sections.sort(key=lambda x: x.H.Value, reverse= order == Qt.AscendingOrder)
        elif col == table_models.N:
            self.sections.sort(key=lambda x: x.N, reverse= order == Qt.AscendingOrder)
        elif col == table_models.M:
            self.sections.sort(key=lambda x: x.M, reverse= order == Qt.AscendingOrder)
        elif col == table_models.TOTAL:
            self.sections.sort(key=lambda x: x.Number, reverse= order == Qt.AscendingOrder)
        elif col == table_models.RHO:
            self.sections.sort(key=lambda x: x.Rebar_Percentage, reverse= order == Qt.AscendingOrder)
        elif col == table_models.NAME:
            self.sections.sort(key=lambda x: x.Section_Name, reverse= order == Qt.AscendingOrder)
        self.layoutChanged.emit()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) |
            Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or
                not (0 <= index.row() < len(self.sections))):
            return
        section = self.sections[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == NAME:
                return section.Section_Name
            elif column == WIDTH:
                return str(int(section.B.getValueAs('cm')))
            elif column == HEIGHT:
                return str(int(section.H.getValueAs('cm')))
            elif column == N:
                return str(section.N)
            elif column == M:
                return str(section.M)
            elif column == TOTAL:
                return str(section.Number)
            elif column == RHO:
                return f'{section.Rebar_Percentage:.2f}'

        elif role == Qt.TextAlignmentRole:
            if column == NAME:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            return int(Qt.AlignCenter | Qt.AlignVCenter)
        elif role == Qt.BackgroundColorRole:
            # if column == SLENDER:
            #     if section.slender == u'لاغر':
            #         return QColor(250, 40, 0)
            #     else:
            #         return QColor(100, 250, 0)
            if '14' in section.Diameter:
                return QColor(150, 200, 150)
            elif '16' in section.Diameter:
                return QColor(150, 200, 250)
            elif '18' in section.Diameter:
                return QColor(250, 200, 250)
            elif '20' in section.Diameter:
                return QColor(250, 250, 130)
            elif '22' in section.Diameter:
                return QColor(10, 250, 250)
            elif '25' in section.Diameter:
                return QColor(210, 230, 230)
            elif '28' in section.Diameter:
                return QColor(110, 230, 230)
            elif '30' in section.Diameter:
                return QColor(210, 130, 230)
            else:
                return QColor(150, 150, 250)
        # elif role == Qt.TextColorRole:
            # if column == SLENDER:
            # return Qt.red)

        return

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            return int(Qt.AlignRight | Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            if section == NAME:
                return "Name"
            elif section == WIDTH:
                return 'B (Cm)'
            elif section == HEIGHT:
                return 'H (Cm)'
            elif section == N:
                return 'N'
            elif section == M:
                return 'M'
            elif section == TOTAL:
                return 'Number'
            elif section == RHO:
                return 'Rho'

        return int(section + 1)

    def rowCount(self, index=QModelIndex()):
        return len(self.sections)

    def columnCount(self, index=QModelIndex()):
        return column_column_count


class ConcreteBeamSectionTableModel(QAbstractTableModel):

    def __init__(
        self,
        sections: list,
        ):
        super(ConcreteBeamSectionTableModel, self).__init__()
        self.sections = sections
        self.names = set()

    def sort(self, col, order):
        """Sort table by given column number."""
        self.layoutAboutToBeChanged.emit()
        if col == table_models.WIDTH:
            self.sections.sort(key=lambda x: x.B.Value, reverse= order == Qt.AscendingOrder)
        elif col == table_models.HEIGHT:
            self.sections.sort(key=lambda x: x.H.Value, reverse= order == Qt.AscendingOrder)
        elif col == table_models.NAME:
            self.sections.sort(key=lambda x: x.Section_Name, reverse= order == Qt.AscendingOrder)
        self.layoutChanged.emit()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) |
            Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or
                not (0 <= index.row() < len(self.sections))):
            return
        section = self.sections[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == NAME:
                return section.Section_Name
            elif column == WIDTH:
                return str(int(section.B.getValueAs('cm')))
            elif column == HEIGHT:
                return str(int(section.H.getValueAs('cm')))

        elif role == Qt.TextAlignmentRole:
            if column == NAME:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            return int(Qt.AlignCenter | Qt.AlignVCenter)
        elif role == Qt.BackgroundColorRole:
            if section.B.Value == 350:
                return QColor(150, 200, 150)
            elif section.B.Value == 400:
                return QColor(150, 200, 250)
            elif section.B.Value == 450:
                return QColor(250, 200, 250)
            elif section.B.Value == 500:
                return QColor(250, 250, 130)
            elif section.B.Value == 550:
                return QColor(10, 250, 250)
            elif section.B.Value == 600:
                return QColor(210, 230, 230)
            elif section.B.Value == 650:
                return QColor(110, 230, 230)
            elif section.B.Value == 700:
                return QColor(210, 130, 230)
            else:
                return QColor(150, 150, 250)
        # elif role == Qt.TextColorRole:
            # if column == SLENDER:
            # return Qt.red)

        return

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            return int(Qt.AlignRight | Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            if section == NAME:
                return "Name"
            elif section == WIDTH:
                return 'B (Cm)'
            elif section == HEIGHT:
                return 'H (Cm)'

        return int(section + 1)

    def rowCount(self, index=QModelIndex()):
        return len(self.sections)

    def columnCount(self, index=QModelIndex()):
        return beam_column_count

    # def setData(self, index, value, role=Qt.EditRole):
    #     if index.isValid() and 0 <= index.row() < len(self.sections):
    #         section = self.sections[index.row()]
    #         column = index.column()
    #         if column == NAME:
    #             if all([value != '', value not in self.names]):
    #                 section.name = value
    #                 self.names.add(value)
    #         try:
    #             value = float(value)
    #             if value > 0:
    #                 if column == AREA:
    #                     section.area = value * 100
    #                 elif column == ASX:
    #                     section.ASx = value * 100
    #                 elif column == ASY:
    #                     section.ASy = value * 100
    #                 elif column == IX:
    #                     section.Ix = value * 10000
    #                 elif column == IY:
    #                     section.Iy = value * 10000
    #                 elif column == ZX:
    #                     section.Zx = value * 1000
    #                 elif column == ZY:
    #                     section.Zy = value * 1000
    #                 elif column == BF:
    #                     section.bf_equivalentI = value * 10
    #                 elif column == TF:
    #                     section.tf_equivalentI = value * 10
    #                 elif column == D:
    #                     section.d_equivalentI = value * 10
    #                 elif column == TW:
    #                     section.tw_equivalentI = value * 10
    #                 elif column == CW:
    #                     section.cw = value * 1e6
    #                 elif column == J:
    #                     section.J = value * 10000
    #                 # elif column == XM:
    #                 #     section.xm = value
    #                 # elif column == YM:
    #                 #     section.ym = value

    #                 section.Rx = sqrt(section.Ix / section.area)
    #                 section.Ry = sqrt(section.Iy / section.area)
    #                 section.Sx = section.Ix / section.ym
    #                 section.Sy = section.Iy / (section.xmax - section.xm)
    #         except ValueError:
    #             pass
    #         section.xml = section.__str__()
    #         self.dirty = True
    #         self.dataChanged.emit(index, index)
    #         return True
    #     return False

    # def insertRows(self, position, rows=1, index=QModelIndex()):
    #     self.beginInsertRows(QModelIndex(), position, position + rows - 1)
    #     for row in range(rows):
    #         self.sections.insert(position + row,
    #                              Ipe("IPE18", 2390, 91, 180, 13170000, 1010000, 166000, 34600, 8.0, 5.3, 9))
    #     self.endInsertRows()
    #     self.dirty = True
    #     return True

    # def removeRows(self, position, rows=1, index=QModelIndex()):
    #     self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
    #     self.sections = (self.sections[:position] +
    #                      self.sections[position + rows:])
    #     self.endRemoveRows()
    #     self.dirty = True
    #     return True

    # def moveRows(self, parent, source_first, source_last, parent2, dest):
    #     self.beginMoveRows(parent, source_first, source_last, parent2, dest)

    #     sections = self.sections
    #     if source_first <= dest:
    #         new_order = sections[:source_first] + sections[source_last + 1:dest + 1] + sections[source_first:source_last + 1] + sections[dest + 1:]
    #     else:  # TODO what if source_first < dest < source_last
    #         new_order = sections[:dest] + sections[source_first:source_last + 1] + sections[dest:source_first] + sections[source_last + 1:]
    #     # self.alignment.set_sequences(new_order, notify=True)
    #     self.sections = new_order
    #     print("BEFORE endMoveRows in edit_sequence_list.Model, %s" % self)
    #     self.endMoveRows()


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
