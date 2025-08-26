from pathlib import Path
import enum
import math

import matplotlib.pyplot as plt

from PySide.QtCore import (
    QAbstractTableModel,
    Qt,
    QSize,
)
from PySide.QtGui import QColor #, QIcon
from PySide.QtGui import QComboBox, QItemDelegate
import PySide

from table_model import PandasModel

from prop_frame import CompareTwoColumnsEnum
from python_functions import rectangle_vertexes, rebar_centers


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
    gray = CompareTwoColumnsEnum.material.value
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
                if value is None:
                    return ""
                return str(value)
            elif role == Qt.ItemDataRole.BackgroundRole:
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
        section_name = index.model().data(index)
        if section_name is None:
            return None
        row = index.row()
        col = index.column()
        section_areas = index.model().sourceModel().section_areas
        if row == index.model().rowCount() - 1:
            desired_sections = section_areas.keys()
            below_section_name = ''
        else:
            below_index = index.model().index(row + 1, col)
            below_section_name = index.model().data(below_index)
            section_area = section_areas.get(below_section_name, None)
            if section_area is None or below_section_name == '':
                desired_sections = section_areas.keys()
            else:
                etabs = index.model().sourceModel().etabs
                desired_sections = []
                columns_type_names_df = index.model().sourceModel().columns_type_names_df
                above_col = columns_type_names_df.iloc[row, col]
                below_col = columns_type_names_df.iloc[row + 1, col]
                for sec in section_areas.keys():
                    ret = etabs.prop_frame.compare_two_columns(below_col, above_col, section_areas, above_sec=sec)
                    if ret is CompareTwoColumnsEnum.OK:
                        desired_sections.append(sec)
        combobox = EscapeCloseComboBox(parent)
        combobox.setDelegate(self)
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
        
    def editorEvent(self, event, model, option, index):
        # Open the dialog when a cell is clicked
        if PySide.__version__.startswith('5'):
            if event.type() == event.MouseButtonRelease and event.button() == Qt.RightButton:
                self.draw_sections(index)
                return True
        elif PySide.__version__.startswith('6'):
            if event.type() == event.Type.MouseButtonRelease and event.button() == Qt.RightButton:
                self.draw_sections(index)
                return True
        return super().editorEvent(event, model, option, index)

    def draw_sections(self, index):
        row = index.row()
        col = index.column()
        section_name = index.model().data(index)
        below_index = index.model().index(row + 1, col)
        if row == index.model().rowCount() - 1:
            below_section_name = None
        else:
            below_section_name = index.model().data(below_index)
        if below_section_name == '' or section_name == '':
            return
        print(f'{below_section_name=}')
        etabs = index.model().sourceModel().etabs
        etabs.set_current_unit("kgf", "cm")
        fig, axes = plt.subplots(2, 1)
        _, mat, height, width, *args = etabs.SapModel.PropFrame.GetRectangle(section_name)
        ret = etabs.SapModel.propframe.GetRebarColumn_1(section_name)
        cover = ret[4]
        N = ret[6]
        M = ret[7]
        lon_diameter = math.sqrt(ret[15] * 4 / math.pi)
        corner_diameter = math.sqrt(ret[16] * 4 / math.pi)
        print(f"{lon_diameter=}, {corner_diameter=}, {ret[15]}")
        draw_concrete_section(width, height, N, M, corner_diameter, lon_diameter, 1, cover, ax=axes[0])
        # Draw Below Section
        _, mat, height, width, *args = etabs.SapModel.PropFrame.GetRectangle(below_section_name)
        ret = etabs.SapModel.propframe.GetRebarColumn_1(below_section_name)
        cover = ret[4]
        N = ret[6]
        M = ret[7]
        lon_diameter = math.sqrt(ret[15] * 4 / math.pi)
        corner_diameter = math.sqrt(ret[16] * 4 / math.pi)
        draw_concrete_section(width, height, N, M, corner_diameter, lon_diameter, 1, cover, ax=axes[1])
        plt.show()

    def sizeHint(self, option, index):
        fm = option.fontMetrics
        if PySide.__version__.startswith('5'):
            return QSize(fm.width("2IPE14FPL200X10WP"), fm.height())
        elif PySide.__version__.startswith('6'):
            return QSize(fm.horizontalAdvance("2IPE14FPL200X10WP"), fm.height())
    
class EscapeCloseComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._delegate = None

    def setDelegate(self, delegate):
        self._delegate = delegate

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self._delegate is not None:
            # Close editor and revert changes
            self._delegate.closeEditor.emit(self, QItemDelegate.RevertModelCache)
        else:
            super().keyPressEvent(event)


def draw_concrete_section(
        width: float,
        height: float,
        N: int,
        M: int,
        corner_diameter: float,
        longitudinal_diameter: float,
        tie_diameter: int = 10,
        cover: int = 40,
        center=(0, 0),
        ax=None,
        ):
    # Define the corners of the outer rectangle (concrete section)
    outer_rectangle = rectangle_vertexes(width, height, center)
    inner_rectangle = rectangle_vertexes(width - 2 * cover - tie_diameter, height - 2 * cover - tie_diameter, center)

    # Plot the outer (concrete) rectangle
    ax.plot(*zip(*outer_rectangle), color='black', linewidth=2)  # Concrete section
    ax.plot(*zip(*inner_rectangle), color='black', linewidth=1)  # Concrete section

    corners, longitudinals = rebar_centers(
        width,
        height,
        N,
        M,
        corner_diameter,
        longitudinal_diameter,
        tie_diameter,
        cover,
        center,
        )
    # Draw corner rebars (large dots)
    for rebar in corners:
        ax.plot(rebar[0], rebar[1], 'ro', markersize=corner_diameter * 10 / 2)  # Corner rebars
    for rebar in longitudinals:
        ax.plot(rebar[0], rebar[1], 'bo', markersize=longitudinal_diameter * 10 / 2)  # Corner rebars


    # Set limits
    ax.set_xlim(-1 - width / 2, width / 2 + 1)
    ax.set_ylim(-1 - height / 2, height / 2 + 1)
    ax.set_aspect('equal')
    ax.set_axis_off()

