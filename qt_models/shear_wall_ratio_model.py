from pathlib import Path
import pandas as pd


from PySide.QtCore import (
    Qt,
)
from PySide.QtGui import QColor #, QIcon

from table_model import PandasModel


civiltools_path = Path(__file__).absolute().parent


class ShearWallsRatio(PandasModel):
    def __init__(self, df, kwargs):
        super(ShearWallsRatio, self).__init__(df, kwargs=kwargs)
        self.df['DCRatio'] = self.df['DCRatio'].astype(float)
        # Group by the key columns and get index of max PMMRatio for each group
        i_pier = tuple(self.df.columns).index("Pier")
        i_story = tuple(self.df.columns).index("Story")
        self.i_ratio = tuple(self.df.columns).index("DCRatio")
        self.col_function = (i_pier, i_story)
        self.min_ratio = self.df['DCRatio'].min()
        self.max_ratio = self.df['DCRatio'].max()
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            value = self.df.iloc[row, col]
            return str(value) if not pd.isna(value) else ""
        
        elif role == Qt.BackgroundRole and col == self.i_ratio:
            value = self.df.iloc[row, self.i_ratio]
            if pd.isna(value):
                return
            # Normalize the PMM value between 0 and 1
            normalized = (value - self.min_ratio) / (self.max_ratio - self.min_ratio)
            # Create color gradient from blue (low) to red (high)
            red = int(255 * normalized)
            blue = int(255 * (1 - normalized))
            green = 0
            return QColor(red, green, blue)
