import os
import sys
from pathlib import Path
# import comtypes.client
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt 
from PyQt5.QtGui import QColor

from PyQt5 import uic

civiltools_path = Path(__file__).parent.parent
sys.path.insert(0, str(civiltools_path))
result_window, result_base = uic.loadUiType(str(civiltools_path / 'widgets' / 'results.ui'))


class ResultsModel(QAbstractTableModel):
    '''
    MetaClass Model for showing Results
    '''
    def __init__(self, data, headers):
        QAbstractTableModel.__init__(self)
        self.df = pd.DataFrame(data, columns=headers)
        self.headers = headers

    def rowCount(self, parent=None):
        return self.df.shape[0]

    def columnCount(self, parent=None):
        return self.df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        return None

    def headerData(self, col, orientation, role):
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return self.headers[col]
        return int(col + 1)


class DriftModel(ResultsModel):
    def __init__(self, data, headers):
        super(DriftModel, self).__init__(data, headers)
        self.df = self.df[[
            'Story',
            'OutputCase',
            'Max Drift',
            'Avg Drift',
            'Allowable Drift'
        ]]
        self.headers = tuple(self.df.columns)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()
        max_i = self.headers.index('Max Drift')
        avg_i = self.headers.index('Avg Drift')
        allow_i = self.headers.index('Allowable Drift')
        red = QColor(255, 0, 0)
        green = QColor(0, 255, 0)
        if index.isValid():
            value = self.df.iloc[row][col]
            allow_drift = float(self.df.iloc[row][allow_i])
            if role == Qt.DisplayRole:
                return str(value)
            elif role == Qt.BackgroundColorRole:
                if col in (avg_i, max_i):
                    if float(value) < allow_drift:
                        return green
                    else:
                        return red
            elif role == Qt.TextAlignmentRole:
                return int(Qt.AlignCenter | Qt.AlignVCenter)


class ResultWidget(result_base, result_window):
    # main widget for user interface
    def __init__(self, data, headers, parent=None):
        super(ResultWidget, self).__init__(parent)
        self.setupUi(self)
        self.data = data
        self.headers = headers

    def show_results(self, model):
        self.model = model(self.data, self.headers)
        self.result_table_view.setModel(self.model)


    # def saveResults(self):
    #     if self.modelPath:
    #         excel_path = self.modelPath + '/results.xlsx'
    #         with pd.ExcelWriter(excel_path) as writer:
    #             self.driftTable.to_excel(writer, sheet_name='drift_results')
    #             self.torsTable.to_excel(writer, sheet_name='torsion_results')
    #         mess_save = 'results saved to excel'
    #     else:
    #         mess_save = 'ETABS file path not found'

    #     self.statustext.setText(mess_save)
    #     pass

def show_results(data, headers, model):
    child_results_win = ResultWidget(data, headers)
    child_results_win.show_results(model)
    child_results_win.exec_()


# class EtabsModel:
#     # my ETABS API class to open and manipulate etabs model
#     def __init__(self, modelpath, etabspath="c:/Program Files/Computers and Structures/ETABS 19/ETABS.exe", existinstance=False, specprogpath=False):
#         # set the following flag to True to attach to an existing instance of the program
#         # otherwise a new instance of the program will be started
#         self.AttachToInstance = existinstance

#         # set the following flag to True to manually specify the path to ETABS.exe
#         # this allows for a connection to a version of ETABS other than the latest installation
#         # otherwise the latest installed version of ETABS will be launched
#         self.SpecifyPath = specprogpath

#         # if the above flag is set to True, specify the path to ETABS below
#         self.ProgramPath = etabspath

#         # full path to the model
#         # set it to the desired path of your model
#         self.FullPath = modelpath
#         [self.modelPath, self.modelName] = os.path.split(self.FullPath)
#         if not os.path.exists(self.modelPath):
#             try:
#                 os.makedirs(self.modelPath)
#             except OSError:
#                 pass

#         if self.AttachToInstance:
#             # attach to a running instance of ETABS
#             try:
#                 # get the active ETABS object
#                 self.myETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
#                 self.success = True
#             except (OSError, comtypes.COMError):
#                 print("No running instance of the program found or failed to attach.")
#                 self.success = False
#                 sys.exit(-1)

#         else:
#             # create API helper object
#             self.helper = comtypes.client.CreateObject('ETABSv1.Helper')
#             self.helper = self.helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
#             if self.SpecifyPath:
#                 try:
#                     # 'create an instance of the ETABS object from the specified path
#                     self.myETABSObject = self.helper.CreateObject(self.ProgramPath)
#                 except (OSError, comtypes.COMError):
#                     print("Cannot start a new instance of the program from " + self.ProgramPath)
#                     sys.exit(-1)
#             else:

#                 try:
#                     # create an instance of the ETABS object from the latest installed ETABS
#                     self.myETABSObject = self.helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject")
#                 except (OSError, comtypes.COMError):
#                     print("Cannot start a new instance of the program.")
#                     sys.exit(-1)

#             # start ETABS application
#             self.myETABSObject.ApplicationStart()

#         # create SapModel object
#         self.SapModel = self.myETABSObject.SapModel

#         # initialize model
#         self.SapModel.InitializeNewModel()

#         # create new blank model
#         # ret = self.SapModel.File.NewBlank()

#         # open existing model
#         ret = self.SapModel.File.OpenFile(self.FullPath)

#         """
#         # save model
#         print(self.FullPath)
#         ret = self.SapModel.File.Save(self.FullPath)
#         print(ret)
#         print("ETABS mod - model saved")
#         """

#         # run model (this will create the analysis model)
#         ret = self.SapModel.Analyze.RunAnalysis()

#         # get all load combination names
#         self.NumberCombo = 0
#         self.ComboNames = []
#         [self.NumberCombo, self.ComboNames, ret] = self.SapModel.RespCombo.GetNameList(self.NumberCombo, self.ComboNames)

#         # isolate drift combos by searching for "drift" in combo name
#         self.DriftCombos = []
#         for combo in self.ComboNames:
#             lowerCombo = combo.lower()
#             # skip combinations without drift in name
#             if "drift" not in lowerCombo:
#                 continue
#             self.DriftCombos.append(combo)

#         self.StoryDrifts = []
#         self.JointDisplacements = []
#         pd.set_option("max_columns", 8)
#         # pd.set_option("precision", 4)

#     def story_drift_results(self, dlimit=0.01):
#         # returns dataframe drift results for all drift load combinations
#         self.StoryDrifts = []
#         for dcombo in self.DriftCombos:
#             # deselect all combos and cases, then only display results for combo passed
#             ret = self.SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
#             ret = self.SapModel.Results.Setup.SetComboSelectedForOutput(dcombo)

#             # initialize drift results
#             NumberResults = 0
#             Stories = []
#             LoadCases = []
#             StepTypes = []
#             StepNums = []
#             Directions = []
#             Drifts = []
#             Labels = []
#             Xs = []
#             Ys = []
#             Zs = []

#             [NumberResults, Stories, LoadCases, StepTypes, StepNums, Directions, Drifts, Labels, Xs, Ys, Zs, ret] = \
#                 self.SapModel.Results.StoryDrifts(NumberResults, Stories, LoadCases, StepTypes, StepNums, Directions,
#                                                   Drifts, Labels, Xs, Ys, Zs)
#             # append all drift results to storydrifts list
#             for i in range(0, NumberResults):
#                 self.StoryDrifts.append((Stories[i], LoadCases[i], Directions[i], Drifts[i], Drifts[i] / dlimit))

#         # set up pandas data frame and sort by drift column
#         labels = ['Story', 'Combo', 'Direction', 'Drift', 'DCR(Drift/Limit)']
#         df = pd.DataFrame.from_records(self.StoryDrifts, columns=labels)
#         dfSort = df.sort_values(by=['Drift'], ascending=False)
#         dfSort.Drift = dfSort.Drift.round(4)
#         dfSort['DCR(Drift/Limit)'] = dfSort['DCR(Drift/Limit)'].round(2)
#         return dfSort

#     def story_torsion_check(self):
#         # returns dataframe of torsion results for drift combinations
#         self.JointDisplacements = []
#         for dcombo in self.DriftCombos:
#             # deselect all combos and cases, then only display results for combo passed
#             ret = self.SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
#             ret = self.SapModel.Results.Setup.SetComboSelectedForOutput(dcombo)

#             # initialize joint drift results
#             NumberResults = 0
#             Stories = []
#             LoadCases = []
#             Label  = ''
#             Names = ''
#             StepType = []
#             StepNum = []
#             # Directions = []
#             DispX = []
#             DispY = []
#             DriftX = []
#             DriftY = []

#             [NumberResults, Stories, Label, Names, LoadCases, StepType, StepNum, DispX, DispY, DriftX, DriftY, ret] = \
#                 self.SapModel.Results.JointDrifts(NumberResults, Stories, Label, Names, LoadCases, StepType, StepNum,
#                                                   DispX, DispY, DriftX, DriftY)

#             # append all displacement results to jointdrift list
#             for i in range(0, NumberResults):
#                 self.JointDisplacements.append((Label[i], Stories[i], LoadCases[i], DispX[i], DispY[i]))

#         # set up pandas data frame and sort by drift column
#         jlabels = ['label', 'Story', 'Combo', 'DispX', 'DispY']
#         jdf = pd.DataFrame.from_records(self.JointDisplacements, columns=jlabels)
#         story_names = jdf.Story.unique()
#         # print("story names = " + str(story_names))

#         # set up data frame for torsion displacement results
#         tlabels = ['Story', 'Load Combo', 'Direction', 'Max Displ', 'Avg Displ', 'Ratio']
#         tdf = pd.DataFrame(columns=tlabels)

#         # calculate and append to df the max, avg, and ratio of story displacements in each dir.
#         for dcombo in self.DriftCombos:
#             for story in story_names:
#                 temp_df = jdf[(jdf['Story'] == story) & (jdf['Combo'] == dcombo)]
#                 # assume direction is X
#                 direction = 'X'
#                 averaged = abs(temp_df['DispX'].mean())
#                 maximumd = temp_df['DispX'].abs().max()
#                 averagey = abs(temp_df['DispY'].mean())

#                 # change direction to Y if avg y-dir displacement is higher
#                 if averagey > averaged:
#                     averaged = averagey
#                     maximumd = temp_df['DispY'].abs().max()
#                     direction = 'Y'

#                 ratiod = maximumd / averaged

#                 # append info to torsion dataframe
#                 temp_df2 = pd.DataFrame([[story, dcombo, direction, maximumd, averaged, ratiod]], columns=tlabels)
#                 tdf = tdf.append(temp_df2, ignore_index=True)

#         tdfSort = tdf.sort_values(by=['Ratio'], ascending=False)
#         tdfSort.Ratio = tdfSort.Ratio.round(3)
#         tdfSort['Max Displ'] = tdfSort['Max Displ'].round(3)
#         tdfSort['Avg Displ'] = tdfSort['Avg Displ'].round(3)

#         return tdfSort

#     def model_close(self):
#         # close the program
#         ret = self.myETABSObject.ApplicationExit(False)
#         self.SapModel = None
#         self.myETABSObject = None
#         return 'model closed'

# """
# # define drift limit for DCR calc
# DriftLimit = 0.01
# FilePath = "C:\\Users\\Andrew-V.Young\\Desktop\\ETABS API TEST\\ETABS\\TestModel.EDB"

# testModel = EtabsModel(FilePath)
# drifts = testModel.story_drift_results(DriftLimit)
# torsion = testModel.story_torsion_check()
# print(drifts.head(10))
# print("\n\n")
# print(torsion)

# ret = testModel.model_close()
# print(ret)