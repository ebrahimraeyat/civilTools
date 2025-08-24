from pathlib import Path
from typing import Iterable

import pandas as pd

from PySide.QtCore import QAbstractTableModel, Qt, QSettings
from PySide.QtGui import QDoubleSpinBox, QItemDelegate, QComboBox, QMessageBox
from PySide.QtGui import QColor
from PySide import QtGui
import FreeCADGui as Gui

from exporter import civiltools_config

from python_functions import change_unit


civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtGui.QWidget):
    def __init__(self, etabs_obj, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'aj_correction.ui'))
        self.etabs = etabs_obj
        self.load_config(d)
        self.stories = self.etabs.SapModel.Story.GetStories()[1]
        story_length = self.etabs.story.get_stories_length()
        self.data = [[key, value[0], value[1]] for key, value in story_length.items()]
        self.headers = ('story', 'x (Cm)', 'y (Cm)')
        self.form.story_model = StoryLengthModel(self.data, self.headers)
        self.form.story_xy_length.setModel(self.form.story_model)
        # self.form.story_xy_length.setItemDelegate(StoryLengthDelegate(self))
        df = self.etabs.get_magnification_coeff_aj()
        self.static_df = self.etabs.get_static_magnification_coeff_aj(df)
        self.dynamic_df = self.etabs.get_dynamic_magnification_coeff_aj(df)
        self.aj_apply_model_static = AjApplyModel(self.static_df)
        self.form.aj_apply_static_view.setModel(self.aj_apply_model_static)
        self.aj_apply_model_dynamic = AjApplyModel(self.dynamic_df)
        self.form.aj_apply_dynamic_view.setModel(self.aj_apply_model_dynamic)
        # self.aj_apply_static_view.setItemDelegate(AjDelegate(self))
        self.form.aj_apply_static_view.resizeColumnsToContents()
        self.form.aj_apply_dynamic_view.resizeColumnsToContents()
        self.form.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.form.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.form.adjustSize()
        # self.load_settings()

        self.create_connections()

    def create_connections(self):
        self.form.static_apply.clicked.connect(self.apply_static_aj)
        self.form.dynamic_apply.clicked.connect(self.apply_dynamic_aj)
        
        # self.form.story_model.dataChanged.connect(self.story_length_changed)

    def load_config(self, d):
        civiltools_config.load(self.etabs, self.form, d)

    @change_unit('N', 'cm')
    def apply_static_aj(self):
        df = self.aj_apply_model_static.df.copy(deep=True)
        load_patterns = self.qlistwidgets_item_text((
            self.form.x_loadcase_list,
            self.form.y_loadcase_list,
        ))
        stories = [item.text() for item in self.form.stories.selectedItems()]
        filt = (df['OutputCase'].isin(load_patterns)) & (df['Story'].isin(stories))
        df = df.loc[filt]
        self.etabs.apply_aj_df(df)
        msg = "Successfully written to Etabs."
        QMessageBox.information(None, "done", msg)
    
    @change_unit('N', 'cm')    
    def apply_dynamic_aj(self):
        df = self.aj_apply_model_dynamic.df.copy(deep=True)
        loadcases = self.qlistwidgets_item_text((
            self.form.x_dynamic_loadcase_list,
            self.form.y_dynamic_loadcase_list,
            self.form.angular_loadcase_list,
        ))
        stories = [item.text() for item in self.form.stories.selectedItems()]
        filt = (df['OutputCase'].isin(loadcases)) & (df['Story'].isin(stories))
        # filt = df['OutputCase'].isin(loadcases)
        df = df.loc[filt]
        self.etabs.database.write_daynamic_aj_user_coefficient(df)
        msg = "Successfully written to Etabs."
        QMessageBox.information(None, "done", msg)

    # def story_length_changed(self, index):
    #     row = index.row()
    #     col = index.column()
    #     value = self.form.story_model.df.iat[row, col]
    #     story = self.form.story_model.df.iat[row, 0]
    #     if col == 1:
    #         dir_ = 'Y'
    #     elif col == 2:
    #         dir_ = 'X'
    #     story_dir = (self.df['Story'] ==story) & (self.df['Dir'] == dir_)
    #     self.df.loc[story_dir, 'Length (Cm)'] = value
    #     self.df.loc[story_dir, 'Ecc. Length (Cm)'] = \
    #             self.df[story_dir]['Ecc. Ratio'] * \
    #             self.df[story_dir]['Length (Cm)'] 
    #     indexes = story_dir.index[story_dir].tolist()
    #     for i in indexes:
    #         index = self.form.aj_model.createIndex(i, self.form.aj_model.i_len)
    #         self.form.aj_model.dataChanged.emit(index, index)
    #         index = self.form.aj_model.createIndex(i, self.form.aj_model.i_ecc_len)
    #         self.form.aj_model.dataChanged.emit(index, index)
    #     stories = self.form.aj_apply_model.df['Story'] == story
    #     indexes = stories.index[stories].tolist()
    #     for i in indexes:
    #         index = self.form.aj_apply_model.createIndex(i, 3)
    #         df = self.df
    #         self.form.aj_apply_model.df.iat[i, 3] = df[(df['Story'] == story) & (df['Dir'] == dir_)]['Ecc. Length (Cm)'].max()
    #         self.form.aj_apply_model.dataChanged.emit(index, index)


    @staticmethod
    def qlistwidgets_item_text(qlistwidgets: Iterable):
        names = []
        for lw in qlistwidgets:
            for i in range(lw.count()):
                item = lw.item(i)
                if item.checkState() == Qt.Checked:
                    names.append(item.text())
        return names

    # def closeEvent(self, event):
    #     qsettings = QSettings("civiltools", 'aj_correction')
    #     qsettings.setValue("geometry", self.saveGeometry())
    #     qsettings.setValue("pos", self.pos())
    #     qsettings.setValue("size", self.size())
    #     qsettings.setValue("splitter", self.form.splitter.saveState())

    # def load_settings(self):
    #     qsettings = QSettings("civiltools", 'aj_correction')
    #     self.restoreGeometry(qsettings.value("geometry", self.saveGeometry()))
    #     self.move(qsettings.value("pos", self.pos()))
    #     self.resize(qsettings.value("size", self.size()))
    #     self.form.splitter.restoreState(qsettings.value("splitter", self.form.splitter.saveState()))

class AjApplyModel(QAbstractTableModel):
    def __init__(self, df):
        QAbstractTableModel.__init__(self)
        self.df = df
        self.df = self.df.astype({'Ecc. Length (Cm)': int})
        self.headers = tuple(self.df.columns)
        self.i_story = self.headers.index('Story')
        self.i_ecc_len = self.headers.index('Ecc. Length (Cm)')
        self.i_diaph = self.headers.index('Diaph')
        self.i_case = self.headers.index('OutputCase')
        # self.create_diaphs()
        self.story_colors = {}
        cases = self.df['OutputCase'].unique()
        import random
        for c in cases:
            self.story_colors[c] = random.choices(range(150, 256), k=3)

    def create_diaphs(self):
        self.diaphs = self.df['Diaph'].tolist()
        diaphs = []
        for _, row in self.df.iterrows():
            diaph = row[self.i_diaph].split(',')[0]
            diaphs.append(diaph)
        self.df['Diaph'] = diaphs

    def rowCount(self, parent=None):
        return self.df.shape[0]

    def columnCount(self, parent=None):
        return self.df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()
        if index.isValid():
            value = self.df.iloc[row][col]
            if role == Qt.DisplayRole:
                if col == self.i_ecc_len:
                    return f'{value}'
                return str(value)

            elif role == Qt.ItemDataRole.BackgroundRole:
                case = self.df.iloc[row][self.i_case]
                return QColor(*self.story_colors[case])
            elif role == Qt.TextAlignmentRole:
                return int(Qt.AlignCenter | Qt.AlignVCenter)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        col = index.column()
        if role == Qt.EditRole and col == self.i_ecc_len:
            row = index.row()
            self.df.iat[row, col] = int(value)
            self.form.dataChanged.emit(index, index)
            return True
        return False
    
    # def flags(self, index):
    #     if not index.isValid():
    #         return Qt.ItemIsEnabled
    #     col = index.column()
    #     if col != self.i_diaph:
    #         return Qt.ItemIsEnabled

    #     return Qt.ItemFlags(
    #         QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def headerData(self, col, orientation, role):
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return self.headers[col]
        return int(col + 1)

class AjDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        col = index.column()
        if col == index.model().i_diaph:
            row = index.row()
            combobox = QComboBox(parent)
            diaphs = (index.model().diaphs[row]).split(',')
            combobox.addItems(diaphs)
            # combobox.setEditable(True)
            return combobox
        else:
            return QItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        col = index.column()
        text = index.model().data(index, Qt.DisplayRole)
        if col == index.model().i_diaph:
            i = editor.findText(text)
            if i == -1:
                i = 0
            editor.setCurrentIndex(i)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        col = index.column()
        if col == index.model().i_diaph:
            model.setData(index, editor.currentText())


class StoryLengthModel(QAbstractTableModel):
    def __init__(self, data, headers):
        QAbstractTableModel.__init__(self)
        self.df = pd.DataFrame(data, columns=headers)
        self.headers = headers
        
    def rowCount(self, parent=None):
        return self.df.shape[0]

    def columnCount(self, parent=None):
        return self.df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()
        if index.isValid():
            if role == Qt.DisplayRole:
                value = self.df.iat[row, col]
                if col in (1, 2):
                    return f'{value:.1f}'
                return str(value)
            elif role == Qt.TextAlignmentRole:
                return int(Qt.AlignCenter | Qt.AlignVCenter)
    
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        col = index.column()
        row = index.row()
        # if role == Qt.CheckStateRole and col == 0:
        #     self.levels_state[row] = value
        #     self.form.dataChanged.emit(index, index)
        #     return True
        if role == Qt.EditRole:
            # if col == 3:
            #     self.diaphs[row] = value
            #     self.form.dataChanged.emit(index, index)
            if col in (1,2):
                try:
                    self.df.iat[row, col] = float(value)
                    self.form.dataChanged.emit(index, index)
                except:
                    return False
            return True
        return False
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        col = index.column()
        if col == 0:
            return Qt.ItemIsEnabled

        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def headerData(self, col, orientation, role):
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return self.headers[col]
        return int(col + 1)


# class StoryLengthDelegate(QItemDelegate):
#     def __init__(self, parent=None):
#         super().__init__(parent)

#     def createEditor(self, parent, option, index):
#         col = index.column()
#         row = index.row()
#         # if col == 3:
#         #     combobox = QComboBox(parent)
#         #     diaphs = (index.model().df.iloc[row][3]).split(',')
#         #     combobox.addItems(diaphs)
#         #     # combobox.setEditable(True)
#         #     return combobox
#         if col in (1,2):
#             spinbox = QDoubleSpinBox(parent)
#             spinbox.setRange(1, 20000)
#             spinbox.setSingleStep(10)
#             spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
#             spinbox.setSuffix(' Cm')
#             value = index.model().df.iloc[row][col]
#             spinbox.setValue(float(value))
#             return spinbox
#         else:
#             return QItemDelegate.createEditor(self, parent, option, index)

#     def setEditorData(self, editor, index):
#         col = index.column()
#         text = index.model().data(index, Qt.DisplayRole)
#         if col in (1,2):
#             editor.setValue(float(text))
#         # elif col == 3:
#         #     i = editor.findText(text)
#         #     if i == -1:
#         #         i = 0
#         #     editor.setCurrentIndex(i)
#         else:
#             super().setEditorData(editor, index)

#     def setModelData(self, editor, model, index):
#         col = index.column()
#         # if col == 3:
#         #     model.setData(index, editor.currentText())
#         if col in (1,2):
#             model.setData(index, editor.value())