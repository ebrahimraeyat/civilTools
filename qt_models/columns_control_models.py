from pathlib import Path
import enum

from PySide2.QtCore import (
    QAbstractTableModel,
    Qt,
    QSize,
)
from PySide2.QtGui import QColor #, QIcon
from PySide2.QtWidgets import QComboBox, QItemDelegate

from table_model import PandasModel

from prop_frame import CompareTwoColumnsEnum


civiltools_path = Path(__file__).absolute().parent


@enum.unique
class CompareTwoColumnsColorEnum(enum.Enum):
    red = CompareTwoColumnsEnum.section_area.value
    seagreen = CompareTwoColumnsEnum.corner_rebar_size.value
    greenyellow = CompareTwoColumnsEnum.longitudinal_rebar_size.value
    green = CompareTwoColumnsEnum.total_rebar_area.value
    magenta = CompareTwoColumnsEnum.local_axes.value
    firebrick = CompareTwoColumnsEnum.section_dimension.value
    springgreen = CompareTwoColumnsEnum.rebar_number.value
    yellow = CompareTwoColumnsEnum.rebar_slop.value
    lightskyblue = CompareTwoColumnsEnum.OK.value
    white = CompareTwoColumnsEnum.not_checked.value
    

class ControlColumns(PandasModel):
    def __init__(self, data, kwargs=None):
        super(ControlColumns, self).__init__(data, kwargs)
        self.section_areas = self.kwargs['section_areas']
        self.columns_type_names_df = self.kwargs["columns_type_names_df"]
        self.etabs = self.kwargs['etabs']

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()
        if index.isValid():
            # value = self.df.iloc[row][col]
            above_col = self.columns_type_names_df.iloc[row, col]
            value = self.etabs.SapModel.FrameObj.GetSection(above_col)[0]
            if role == Qt.DisplayRole:
                # colors = QColor.colorNames()
                # return colors[col * self.rowCount() + row]
                return str(value)
            elif role == Qt.BackgroundColorRole:
                # colors = QColor.colorNames()
                # return QColor(colors[col * self.rowCount() + row])
                if row != (self.rowCount() - 1) and value is not None:
                    below_col = self.columns_type_names_df.iloc[row + 1, col]
                    below_sec = self.etabs.SapModel.FrameObj.GetSection(below_col)[0]
                    #  = self.df.iloc[row + 1][col]
                    if below_sec is not None:
                        ret = self.etabs.prop_frame.compare_two_columns(below_col, above_col, self.section_areas)
                        return QColor(CompareTwoColumnsColorEnum(ret.value).name)
                else:
                    return QColor(CompareTwoColumnsColorEnum.lightskyblue.name)
                # return QColor(*low)
            elif role == Qt.TextAlignmentRole:
                return int(Qt.AlignCenter | Qt.AlignVCenter)
            
    def headerData(self, col, orientation, role):
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return self.columns_type_names_df.columns[col]
        return self.columns_type_names_df.index[col]
            
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)


class ColumnsControlDelegate(QItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        row = index.row()
        col = index.column()
        if row == index.model().rowCount() - 1:
            return
        section_name = index.model().data(index)
        below_index = index.model().index(row + 1, col)
        below_section_name = index.model().data(below_index)
        print(f'{below_section_name=}')
        if below_section_name == 'None' or section_name == 'None':
            return
        section_areas = index.model().sourceModel().section_areas
        section_area = section_areas.get(below_section_name, None)
        if section_area is None:
            return
        etabs = index.model().sourceModel().etabs
        desired_sections = []
        columns_type_names_df = index.model().sourceModel().columns_type_names_df
        above_col = columns_type_names_df.iloc[row, col]
        below_col = columns_type_names_df.iloc[row + 1, col]
        for sec in section_areas.keys():
            ret = etabs.prop_frame.compare_two_columns(below_col, above_col, section_areas, above_sec=sec)
            if ret is CompareTwoColumnsEnum.OK:
                desired_sections.append(sec)
        # desired_sections = [sec for sec in section_areas.keys() if section_areas[sec] <= section_area]
        combobox = QComboBox(parent)
        combobox.addItems(desired_sections)
        value_index = combobox.findText(below_section_name)
        if value_index != -1:
            combobox.setCurrentIndex(value_index)
        return combobox

    def setEditorData(self, editor, index):
        # Set the current value of the editor based on the model's data
        value = index.model().data(index)
        if isinstance(editor, QComboBox):
            editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        # Update the model with the current value of the editor
        if isinstance(editor, QComboBox):
            selected_section = editor.currentText()
            print(f"{selected_section=}")
            model.setData(index, selected_section)  # Update the model with the selected value
            etabs = index.model().sourceModel().etabs
            etabs.unlock_model()
            columns_type_names_df = index.model().sourceModel().columns_type_names_df
            col = index.column()
            row = index.row()
            name = columns_type_names_df.iloc[row, col]
            etabs.SapModel.FrameObj.SetSection(name, selected_section)
            return True

    def sizeHint(self, option, index):
        fm = option.fontMetrics
        return QSize(fm.width("2IPE14FPL200X10WP"), fm.height())


