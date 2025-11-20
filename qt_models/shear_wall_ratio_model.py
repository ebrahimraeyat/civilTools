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
        self.max_ratio = 1
        
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
            value = min(value, self.max_ratio)
            
            # Normalize the PMM value between 0 and 1
            normalized = (value - self.min_ratio) / (self.max_ratio - self.min_ratio)
            
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
