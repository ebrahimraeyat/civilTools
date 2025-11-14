from pathlib import Path
import pandas as pd


from PySide.QtCore import (
    Qt,
    QSize,
    QAbstractTableModel
)
from PySide.QtGui import QColor #, QIcon
from PySide.QtGui import QComboBox, QItemDelegate

from table_model import PandasModel


civiltools_path = Path(__file__).absolute().parent



class ColumnsPMM(PandasModel):
    def __init__(self, df, kwargs):
        super(ColumnsPMM, self).__init__(df, kwargs=kwargs)
        self.df = df
        self.df_pmm = df.pivot_table(
            index='Story', 
            columns='Label', 
            values='PMMRatio', 
            aggfunc='max'
        )
        self._pmm_values = self.df_pmm.values.flatten()
        self.min_pmm = min(x for x in self._pmm_values if pd.notna(x))
        self.max_pmm = max(x for x in self._pmm_values if pd.notna(x))
        
    def rowCount(self, parent=None):
        return len(self.df_pmm.index)

    def columnCount(self, parent=None):
        return len(self.df_pmm.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        
        row = index.row()
        col = index.column()
        label = str(self.df_pmm.columns[col])
        story = str(self.df_pmm.index[row])
        filt = (self.df['Story'] == story) & (self.df['Label'] == label)
        if role == Qt.DisplayRole:
            value = self.df.loc[filt, 'DesignSect'].values[0]
            return str(value) if not pd.isna(value) else ""
        
        elif role == Qt.BackgroundRole:
            pmm_value = self.df_pmm.iloc[row, col]
            if pd.isna(pmm_value):
                return
            # Normalize the PMM value between 0 and 1
            normalized = (pmm_value - self.min_pmm) / (self.max_pmm - self.min_pmm)
            # Create color gradient from blue (low) to red (high)
            red = int(255 * normalized)
            blue = int(255 * (1 - normalized))
            green = 0
            return QColor(red, green, blue)
        
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df_pmm.columns[section])
            elif orientation == Qt.Vertical:
                return str(self.df_pmm.index[section])

class ColumnsPMMAll(PandasModel):
    def __init__(self, df, kwargs):
        super(ColumnsPMMAll, self).__init__(df, kwargs=kwargs)
        # Group by the key columns and get index of max PMMRatio for each group
        idx = df.groupby(['Story', 'Label', 'UniqueName', 'DesignSect'])['PMMRatio'].idxmax()
        # Get the rows with these indices
        self.df = df.loc[idx].reset_index()
        del self.df['index']
        i_label = tuple(self.df.columns).index("Label")
        i_story = tuple(self.df.columns).index("Story")
        self.i_name = tuple(self.df.columns).index("UniqueName")
        self.col_function = (i_label, i_story)
        self.i_section = tuple(self.df.columns).index("DesignSect")
        self.i_pmm = tuple(self.df.columns).index("PMMRatio")
        self.min_pmm = self.df['PMMRatio'].min()
        self.max_pmm = 1.0
        self.etabs = self.kwargs['etabs']
        self.sections = self.kwargs['sections']
        
    def rowCount(self, parent=None):
        return len(self.df.index)

    def columnCount(self, parent=None):
        return len(self.df.columns)
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == self.i_section:
            return Qt.ItemFlags(
                QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)
        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index))

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            value = self.df.iloc[row, col]
            return str(value) if not pd.isna(value) else ""
        
        elif role == Qt.BackgroundRole and col in (self.i_pmm, self.i_section):
            value = self.df.iloc[row, self.i_pmm]
            if pd.isna(value):
                return
            value = min(value, self.max_pmm)
            
            # Normalize the PMM value between 0 and 1
            normalized = (value - self.min_pmm) / (self.max_pmm - self.min_pmm)
            
            # Create color gradient: blue → cyan → green → yellow → red
            # Split the normalized range into 4 segments
            if normalized < 0.25:
                # Blue (0.0) to Cyan (0.25)
                t = normalized / 0.25
                red = 0
                green = int(255 * t)
                blue = 255
            elif normalized < 0.5:
                # Cyan (0.25) to Green (0.5)
                t = (normalized - 0.25) / 0.25
                red = 0
                green = 255
                blue = int(255 * (1 - t))
            elif normalized < 0.75:
                # Green (0.5) to Yellow (0.75)
                t = (normalized - 0.5) / 0.25
                red = int(255 * t)
                green = 255
                blue = 0
            else:
                # Yellow (0.75) to Red (1.0)
                t = (normalized - 0.75) / 0.25
                red = 255
                green = int(255 * (1 - t))
                blue = 0
            
            return QColor(red, green, blue)
        
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])
            elif orientation == Qt.Vertical:
                return str(self.df.index[section])
            
class ColumnsPMMDelegate(QItemDelegate):

    def __init__(self,
                 parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        combobox = QComboBox(parent)
        sections = index.model().sourceModel().sections
        combobox.addItems(sections)
        return combobox

    def setEditorData(self, editor, index):
        # Set the current value of the editor based on the model's data
        value = index.model().data(index)
        if isinstance(editor, QComboBox):
            editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        # Update the model with the current value of the editor
        col = index.model().sourceModel().i_section
        if index.column() != col:
            return
        if isinstance(editor, QComboBox):
            selected_section = editor.currentText()
            model.setData(index, selected_section)  # Update the model with the selected value
            etabs = index.model().sourceModel().etabs
            i_name = index.model().sourceModel().i_name
            row, col = self.parent().get_current_row_col(index)
            i = index.model().sourceModel().index(row, i_name)
            name = index.model().sourceModel().data(i)
            etabs.unlock_model()
            etabs.SapModel.FrameObj.SetSection(name, selected_section)
            return True
        
    def sizeHint(self, option, index):
        fm = option.fontMetrics
        if index.column() == index.model().sourceModel().i_section:
            return QSize(fm.width("C45X45-16T20-16T25     "), fm.height())
        return QSize(fm.width("C45X45-16T20"), fm.height())
