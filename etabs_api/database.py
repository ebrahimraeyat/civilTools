from pathlib import Path
import sys

import pandas as pd

civil_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civil_path))


__all__ = ['DatabaseTables']

class DatabaseTables:
    def __init__(
                self,
                SapModel=None,
                etabs=None,
                ):
        if not SapModel:
            self.etabs = etabs
            self.SapModel = etabs.SapModel
        else:
            self.SapModel = SapModel

    @staticmethod
    def reshape_data(FieldsKeysIncluded, table_data):
        n = len(FieldsKeysIncluded)
        data = [list(table_data[i:i+n]) for i in range(0, len(table_data), n)]
        return data
    
    @staticmethod
    def reshape_data_to_df(
                FieldsKeysIncluded,
                table_data,
                cols:list=None,
                ) -> 'pandas.DataFrame':
        n = len(FieldsKeysIncluded)
        data = [list(table_data[i:i+n]) for i in range(0, len(table_data), n)]
        df = pd.DataFrame(data, columns=FieldsKeysIncluded)
        if cols is not None:
            df = df[cols]
        return df
   

    @staticmethod
    def unique_data(data):
        table_data = []
        for i in data:
            table_data += i
        return table_data

    def apply_table(self):
        if self.SapModel.GetModelIsLocked():
            self.SapModel.SetModelIsLocked(False)
        FillImportLog = True
        NumFatalErrors = 0
        NumErrorMsgs = 0
        NumWarnMsgs = 0
        NumInfoMsgs = 0
        ImportLog = ''
        [NumFatalErrors, NumErrorMsgs, NumWarnMsgs, NumInfoMsgs, ImportLog,
            ret] = self.SapModel.DatabaseTables.ApplyEditedTables(FillImportLog, NumFatalErrors,
                                                            NumErrorMsgs, NumWarnMsgs, NumInfoMsgs, ImportLog)
        return NumFatalErrors, ret

    def read_table(self, table_key):
        GroupName = table_key
        FieldKeyList = []
        TableVersion = 0
        FieldsKeysIncluded = []
        NumberRecords = 0
        TableData = []
        return self.SapModel.DatabaseTables.GetTableForDisplayArray(table_key, FieldKeyList, GroupName, TableVersion, FieldsKeysIncluded, NumberRecords, TableData)

    def write_seismic_user_coefficient(self, TableKey, FieldsKeysIncluded, TableData):
        FieldsKeysIncluded1 = ['Name', 'Is Auto Load', 'X Dir?', 'X Dir Plus Ecc?', 'X Dir Minus Ecc?',
                            'Y Dir?', 'Y Dir Plus Ecc?', 'Y Dir Minus Ecc?',
                            'Ecc Ratio', 'Top Story', 'Bot Story',
                            ]   
        if len(FieldsKeysIncluded) == len(FieldsKeysIncluded1) + 2:
            FieldsKeysIncluded1.extend(['C', 'K'])
        else:
            FieldsKeysIncluded1.extend(['Ecc Overwrite Story', 'Ecc Overwrite Diaphragm',
            'Ecc Overwrite Length', 'C', 'K'])
        assert len(FieldsKeysIncluded) == len(FieldsKeysIncluded1)
        self.SapModel.DatabaseTables.SetTableForEditingArray(TableKey, 0, FieldsKeysIncluded1, 0, TableData)
        NumFatalErrors, ret = self.apply_table()
        return NumFatalErrors, ret

    def get_story_mass(self):
        self.SapModel.SetPresentUnits_2(5, 6, 2)
        self.etabs.run_analysis()
        TableKey = 'Centers Of Mass And Rigidity'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey)
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        i_mass_x = FieldsKeysIncluded.index('MassX')
        # i_mass_y = FieldsKeysIncluded.index('MassY')
        i_story = FieldsKeysIncluded.index('Story')
        story_mass = []
        for row in data[::-1]:
            story = row[i_story]
            massx = row[i_mass_x]
            # massy = data[i_mass_y]
            story_mass.append([story, massx])
        return story_mass

    def write_aj_user_coefficient(self, TableKey, FieldsKeysIncluded, TableData, df):
        if len(df) == 0: return
        FieldsKeysIncluded1 = ['Name', 'Is Auto Load', 'X Dir?', 'X Dir Plus Ecc?', 'X Dir Minus Ecc?',
                            'Y Dir?', 'Y Dir Plus Ecc?', 'Y Dir Minus Ecc?',
                            'Ecc Ratio', 'Top Story', 'Bot Story', 'Ecc Overwrite Story',
                            'Ecc Overwrite Diaphragm', 'Ecc Overwrite Length', 'C', 'K'
                            ]
        import pandas as pd
        TableData = self.reshape_data(FieldsKeysIncluded, TableData)
        df1 = pd.DataFrame.from_records(TableData, columns=FieldsKeysIncluded)
        extra_fields = ('OverStory', 'OverDiaph', 'OverEcc')
        if len(FieldsKeysIncluded) < len(FieldsKeysIncluded1):
            i_ecc_ow_story = FieldsKeysIncluded1.index('Ecc Overwrite Story')
            indexes = range(i_ecc_ow_story, i_ecc_ow_story + 3)
            for i, header in zip(indexes, extra_fields):
                df1.insert(i, header, None)
        cases = df['OutputCase'].unique()
        df1['C'] = df1['C'].astype(str)
        df1 = df1.loc[df1['C'] != 'None']
        for field in extra_fields:
            df1[field] = None
        additional_rows = []
        import copy
        for i, row in df1.iterrows():
            case = row['Name']
            if case in cases:
                ecc_length = df[
                    (df['OutputCase'] == case)]
                for k, (_, row_aj) in enumerate(ecc_length.iterrows()):
                    story = row_aj['Story']
                    diaph = row_aj['Diaph']
                    length = row_aj['Ecc. Length (Cm)']
                    if k == 0:
                        row['OverStory'] = story
                        row['OverDiaph'] = diaph
                        row['OverEcc'] = str(length)
                    else:
                        new_row = copy.deepcopy(row)
                        new_row[2:] = ''
                        new_row['OverStory'] = story
                        new_row['OverDiaph'] = diaph
                        new_row['OverEcc'] = str(length)
                        additional_rows.append(new_row)
        # df1 = df1.append(pd.DataFrame.from_records(additional_rows, columns=FieldsKeysIncluded1))
        for row in additional_rows:
            df1 = df1.append(row)
        TableData = []
        for _, row in df1.iterrows():
            TableData.extend(list(row))
        self.SapModel.DatabaseTables.SetTableForEditingArray(TableKey, 0, FieldsKeysIncluded1, 0, TableData)
        NumFatalErrors, ret = self.apply_table()
        return NumFatalErrors, ret

    def get_center_of_rigidity(self):
        self.etabs.run_analysis()
        self.SapModel.SetPresentUnits_2(5,6,2)
        TableKey = 'Centers Of Mass And Rigidity'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey)
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        i_xcr = FieldsKeysIncluded.index('XCR')
        i_ycr = FieldsKeysIncluded.index('YCR')
        i_story = FieldsKeysIncluded.index('Story')
        story_rigidity = {}
        for row in data:
            story = row[i_story]
            x = row[i_xcr]
            y = row[i_ycr]
            story_rigidity[story] = (x, y)
        return story_rigidity

    def get_stories_displacement_in_xy_modes(self):
        f1, _ = self.etabs.save_as('modal_stiffness.EDB')
        story_point = self.etabs.story.add_points_in_center_of_rigidity_and_assign_diph()
        modal = self.etabs.load_cases.get_modal_loadcase_name()
        self.etabs.analyze.set_load_cases_to_analyze(modal)
        self.SapModel.Analyze.RunAnalysis()
        wx, wy, ix, iy = self.etabs.results.get_xy_frequency()
        TableKey = 'Joint Displacements'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey)
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        i_story = FieldsKeysIncluded.index('Story')
        i_name = FieldsKeysIncluded.index('UniqueName')
        i_case = FieldsKeysIncluded.index('OutputCase')
        i_steptype = FieldsKeysIncluded.index('StepType')
        i_stepnumber = FieldsKeysIncluded.index('StepNumber')
        i_ux = FieldsKeysIncluded.index('Ux')
        i_uy = FieldsKeysIncluded.index('Uy')
        columns = (i_story, i_name, i_case, i_steptype, i_stepnumber)
        x_results = {}
        for story, point in story_point.items():
            values = (story, point, modal, 'Mode', str(ix))
            result = self.etabs.get_from_list_table(data, columns, values)
            result = list(result)
            assert len(result) == 1
            ux = float(result[0][i_ux])
            x_results[story] = ux
        y_results = {}
        for story, point in story_point.items():
            values = (story, point, modal, 'Mode', str(iy))
            result = self.etabs.get_from_list_table(data, columns, values)
            result = list(result)
            assert len(result) == 1
            uy = float(result[0][i_uy])
            y_results[story] = uy
        self.SapModel.File.OpenFile(str(f1))
        return x_results, y_results, wx, wy

    def multiply_seismic_loads(
            self,
            x: float = .67,
            y=None,
            ):
        if not y:
            y = x
        self.SapModel.SetModelIsLocked(False)
        self.etabs.lock_and_unlock_model()
        self.etabs.load_patterns.select_all_load_patterns()
        TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey)
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        names_x, names_y = self.etabs.load_patterns.get_load_patterns_in_XYdirection()
        i_c = FieldsKeysIncluded.index('C')
        i_name = FieldsKeysIncluded.index("Name")
        for earthquake in data:
            if not earthquake[i_c]:
                continue
            name = earthquake[i_name]
            c = float(earthquake[i_c])
            cx = x * c
            cy = y * c
            if name in names_x:
                earthquake[i_c] = str(cx)
            elif name in names_y:
                earthquake[i_c] = str(cy)
        TableData = self.unique_data(data)
        NumFatalErrors, ret = self.write_seismic_user_coefficient(TableKey, FieldsKeysIncluded, TableData)
        # edb_filename, e2k_filename = self.etabs.export('.$et')
        # self.SapModel.File.OpenFile(str(e2k_filename))
        # solver_options = self.SapModel.Analyze.GetSolverOption_2()
        # solver_options[1] = 1
        # self.SapModel.Analyze.SetSolverOption_2(*solver_options[:-1])
        # self.SapModel.File.Save(str(edb_filename))
        return NumFatalErrors, ret

    def get_story_forces(
                    self,
                    loadcases: list=None,
                    ):
        if not loadcases:
            loadcases = self.etabs.load_patterns.get_ex_ey_earthquake_name()
        assert len(loadcases) == 2
        self.SapModel.SetPresentUnits_2(5, 6, 2)
        self.etabs.load_cases.select_load_cases(loadcases)
        TableKey = 'Story Forces'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey)
        i_loc = FieldsKeysIncluded.index('Location')
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        columns = (i_loc,)
        values = ('Bottom',)
        result = self.etabs.get_from_list_table(data, columns, values)
        story_forces = list(result)
        return story_forces, loadcases, FieldsKeysIncluded

    def get_beams_forces(self,
                        load_combinations : list = None,
                        beams : list = None,
                        cols : list = None,
                        ) -> 'pandas.DataFrame':
        '''
        cols : columns in dataframe that we want to get
        '''
        self.etabs.run_analysis()
        if load_combinations is None:
            load_combinations = self.get_concrete_frame_design_load_combinations()
        self.SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay('')
        self.SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(load_combinations)
        TableKey = 'Element Forces - Beams'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey)
        df = self.reshape_data_to_df(FieldsKeysIncluded, TableData, cols)
        if beams is not None:
            df = df[df['UniqueName'].isin(beams)]
        return df

    def get_beams_torsion(self,
                        load_combinations : list = None,
                        beams : list = None,
                        cols : list = None,
                        ) -> pd.DataFrame:
        if cols is None:
            cols = ['Story', 'Beam', 'UniqueName', 'T']
        self.etabs.set_current_unit('tonf', 'm')
        df = self.get_beams_forces(load_combinations, beams, cols)
        df['T'] = pd.to_numeric(df['T']).abs()
        df = df.loc[df.groupby('UniqueName')['T'].idxmax()]
        if len(cols) == 2:
            return dict(zip(df[cols[0]], df[cols[1]]))
        return df

    def get_concrete_frame_design_load_combinations(self):
        TableKey = 'Concrete Frame Design Load Combination Data'
        [_, _, _, _, TableData, _] = self.read_table(TableKey)
        return [i for i in TableData[1::2]]

    def create_section_cuts(self,
            group : str,
            prefix : str = 'SEC',
            angles : list = range(0, 180, 15),
            ):
        fields = ('Name', 'DefinedBy', 'Group', 'ResultType', 'ResultLoc', 'RotAboutZ', 'RotAboutY', 'RotAboutX')
        data = []
        for angle in angles:
            name = f'{prefix}{angle}'
            data.append(
            (name, 'Group', group, 'Analysis', 'Default', f'{angle}', '0', '0')
            )
        data = self.unique_data(data)
        table = 'Section Cut Definitions'
        self.SapModel.DatabaseTables.SetTableForEditingArray(table, 0, fields, 0, data)
        self.apply_table()

if __name__ == '__main__':
    from pathlib import Path
    current_path = Path(__file__).parent
    import sys
    sys.path.insert(0, str(current_path))
    from etabs_obj import EtabsModel
    etabs = EtabsModel()
    SapModel = etabs.SapModel
    ret = etabs.database.create_section_cuts('Group1')
    print('Wow')
