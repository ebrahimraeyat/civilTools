from pathlib import Path
import pandas as pd


from PySide2.QtCore import (
    Qt,
)
from PySide2.QtGui import QColor #, QIcon

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
        self.col_function = (i_label, i_story)
        self.i_section = tuple(self.df.columns).index("DesignSect")
        self.i_pmm = tuple(self.df.columns).index("PMMRatio")
        self.min_pmm = self.df['PMMRatio'].min()
        self.max_pmm = self.df['PMMRatio'].max()
        
    def rowCount(self, parent=None):
        return len(self.df.index)

    def columnCount(self, parent=None):
        return len(self.df.columns)

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
            # Normalize the PMM value between 0 and 1
            normalized = (value - self.min_pmm) / (self.max_pmm - self.min_pmm)
            # Create color gradient from blue (low) to red (high)
            red = int(255 * normalized)
            blue = int(255 * (1 - normalized))
            green = 0
            return QColor(red, green, blue)
        
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])
            elif orientation == Qt.Vertical:
                return str(self.df.index[section])