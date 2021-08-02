import sys
import comtypes.client
from pathlib import Path

civiltools_path = Path(__file__).parent.parent
from etabs_api.load_patterns import LoadPatterns

class EtabsModel:
    def __init__(
                self,
                attach_to_instance: bool = True,
                # model_path: Path = '',
                # etabs_path: Path = '',
                ):
        if attach_to_instance:
            try:
                self.etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
                self.success = True
            except (OSError, comtypes.COMError):
                print("No running instance of the program found or failed to attach.")
                self.success = False
                sys.exit(-1)
        else:
            self.success = False
            sys.exit(-1)
            # helper = comtypes.client.CreateObject('ETABSv1.Helper')
            # helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
            # if etabs_path:
            #     try:
            #         self.etabs = helper.CreateObject(etabs_path)
            #     except (OSError, comtypes.COMError):
            #         print(f"Cannot start a new instance of the program from {etabs_path}")
            #         sys.exit(-1)
            # else:
            #     try:
            #         self.etabs = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject")
            #     except (OSError, comtypes.COMError):
            #         print("Cannot start a new instance of the program.")
            #         sys.exit(-1)
            # self.etabs.ApplicationStart()
        self.SapModel = self.etabs.SapModel
        self.load_patterns = LoadPatterns(self.SapModel)

    @staticmethod
    def reshape_data(FieldsKeysIncluded, table_data):
        n = len(FieldsKeysIncluded)
        data = [list(table_data[i:i+n]) for i in range(0, len(table_data), n)]
        return data

    @staticmethod
    def unique_data(data):
        table_data = []
        for i in data:
            table_data += i
        return table_data

    def apply_table(self):
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

    def close_etabs(self):
        self.SapModel.SetModelIsLocked(False)
        self.etabs.ApplicationExit(False)
        self.SapModel = None
        self.etabs = None

    def set_load_cases_to_analyze(self, load_cases='All'):
        all_load_case = self.SapModel.Analyze.GetCaseStatus()[1]
        for lc in all_load_case:
            if not load_cases == 'All' and not lc in load_cases:
                self.SapModel.Analyze.SetRunCaseFlag(lc, False)
            else:
                self.SapModel.Analyze.SetRunCaseFlag(lc, True)

    def get_top_bot_stories(self):
        '''
        return bot_x, top_x, bot_y, top_y stories name"
        '''
        # x_names, y_names = get_load_patterns_in_XYdirection()
        # TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
        # [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey, self.SapModel)
        # data = self.reshape_data(FieldsKeysIncluded, TableData)
        # i_top_story = FieldsKeysIncluded.index('TopStory')
        # i_bot_story = FieldsKeysIncluded.index('BotStory')
        # i_name = FieldsKeysIncluded.index('Name')
        # for e in data:
        #     if e[i_name] in x_names:
        #         bot_story_x = e[i_bot_story]
        #         top_story_x = e[i_top_story]
        #         break
        # for e in data:
        #     if e[i_name] in y_names:
        #         bot_story_y = e[i_bot_story]
        #         top_story_y = e[i_top_story]
        #         break
        stories = self.SapModel.Story.GetStories()[1]
        bot_story_x = bot_story_y = stories[0]
        top_story_x = top_story_y = stories[-1]
        return bot_story_x, top_story_x, bot_story_y, top_story_y

    def get_top_bot_levels(
                        self,
                        bot_story_x='',
                        top_story_x='',
                        bot_story_y='',
                        top_story_y='',
                        auto_story=True,
                        ):
        self.SapModel.setPresentUnits_2(5, 6, 2)
        if auto_story and not all([bot_story_x, top_story_x, bot_story_y, top_story_y]):
            bot_story_x, top_story_x, bot_story_y, top_story_y = self.get_top_bot_stories()
        bot_level_x = self.SapModel.Story.GetElevation(bot_story_x)[0]    
        top_level_x = self.SapModel.Story.GetElevation(top_story_x)[0]
        bot_level_y = self.SapModel.Story.GetElevation(bot_story_y)[0]    
        top_level_y = self.SapModel.Story.GetElevation(top_story_y)[0]
        return bot_level_x, top_level_x, bot_level_y, top_level_y

    def get_heights(
                    self,
                    bot_story_x='',
                    top_story_x='',
                    bot_story_y='',
                    top_story_y='',
                    auto_story=True,
                    ):
        bot_level_x, top_level_x, bot_level_y, top_level_y = self.get_top_bot_levels(
            bot_story_x, top_story_x, bot_story_y, top_story_y, auto_story)
        hx = top_level_x - bot_level_x
        hy = top_level_y - bot_level_y
        return hx, hy

    def get_no_of_stories(
                        self,
                        bot_level_x = None,
                        top_level_x = None,
                        bot_level_y = None,
                        top_level_y = None,
                        ):
        # bot_story_x, top_story_x, bot_story_y, top_story_y = get_top_bot_stories()
        if not bot_level_x:
            bot_level_x, top_level_x, bot_level_y, top_level_y = self.get_top_bot_levels()
        levels = self.SapModel.Story.GetStories()[2]
        no_of_x_story = len([i for i in levels if bot_level_x < i <= top_level_x])
        no_of_y_story = len([i for i in levels if bot_level_y < i <= top_level_y])
        return no_of_x_story, no_of_y_story

    def get_story_names(self):
        return self.SapModel.Story.GetNameList()[1]
        
    def select_all_load_patterns(self):
        load_pattern_names = list(self.load_patterns.get_load_patterns())
        self.SapModel.DatabaseTables.SetLoadPatternsSelectedForDisplay(load_pattern_names)

    def get_load_cases(self):
        load_case_names = self.SapModel.LoadCases.GetNameList(0, [])[1]
        return load_case_names

    def select_all_load_cases(self):
        load_case_names = self.get_load_cases()
        self.SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(load_case_names)

    def select_load_cases(self, names):
        self.SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay('')
        self.SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(names)

    def get_modal_loadcase_name(self):
        load_cases = self.get_load_cases()
        for lc in load_cases:
            if self.SapModel.LoadCases.GetTypeOAPI(lc)[0] == 3:
                return lc
        return None  

    def get_beams_columns(
            self,
            type_=2,
            ):
        '''
        type_: 1=steel and 2=concrete
        '''
        beams = []
        columns = []
        others = []
        for label in self.SapModel.FrameObj.GetLabelNameList()[1]:
            if self.SapModel.FrameObj.GetDesignProcedure(label)[0] == type_: 
                if self.SapModel.FrameObj.GetDesignOrientation(label)[0] == 1:
                    columns.append(label)
                elif self.SapModel.FrameObj.GetDesignOrientation(label)[0] == 2:
                    beams.append(label)
                else:
                    others.append(label)
        return beams, columns

    def get_drift_periods(
                self,
                t_filename="T.EDB",
                ):
        '''
        This function creates an Etabs file called T.EDB from current open Etabs file,
        then in T.EDB file change the stiffness properties of frame elements according 
        to ACI 318 to get periods of structure, for this it set M22 and M33 stiffness of
        beams to 0.5 and column and wall to 1.0. Then it runs the analysis and get the x and y period of structure.
        '''
        print(10 * '-' + "Get drift periods" + 10 * '-' + '\n')
        asli_file_path = Path(self.SapModel.GetModelFilename())
        if asli_file_path.suffix.lower() != '.edb':
            asli_file_path = asli_file_path.with_suffix(".EDB")
        dir_path = asli_file_path.parent.absolute()
        t_file_path = dir_path / t_filename
        print(f"Saving file as {t_file_path}\n")
        self.SapModel.File.Save(str(t_file_path))
        print("get frame property modifiers and change I values\n")
        IMod_beam = 0.5
        IMod_col_wall = 1
        for label in self.SapModel.FrameObj.GetLabelNameList()[1]:
            if self.SapModel.FrameObj.GetDesignProcedure(label)[0] == 2:  # concrete
                if self.SapModel.FrameObj.GetDesignOrientation(label)[0] == 1:   # Beam
                    IMod = IMod_beam
                elif self.SapModel.FrameObj.GetDesignOrientation(label)[0] in (2, 5): # Column, other, but not brace and null
                    IMod = IMod_col_wall
                modifiers = list(self.FrameObj.GetModifiers(label)[0])
                modifiers[4:6] = [IMod, IMod]
                self.SapModel.FrameObj.SetModifiers(label, modifiers)

        # run model (this will create the analysis model)
        print("start running T file analysis")
        modal_case = self.get_modal_loadcase_name()
        self.set_load_cases_to_analyze(modal_case)
        self.SapModel.Analyze.RunAnalysis()

        TableKey = "Modal Participating Mass Ratios"
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey, self.SapModel)
        self.SapModel.SetModelIsLocked(False)
        ux_i = FieldsKeysIncluded.index("UX")
        uy_i = FieldsKeysIncluded.index("UY")
        period_i = FieldsKeysIncluded.index("Period")
        uxs = [float(TableData[i]) for i in range(ux_i, len(TableData), len(FieldsKeysIncluded))]
        uys = [float(TableData[i]) for i in range(uy_i, len(TableData), len(FieldsKeysIncluded))]
        periods = [float(TableData[i]) for i in range(period_i, len(TableData), len(FieldsKeysIncluded))]
        ux_max_i = uxs.index(max(uxs))
        uy_max_i = uys.index(max(uys))
        Tx_drift = periods[ux_max_i]
        Ty_drift = periods[uy_max_i]
        print(f"Tx_drift = {Tx_drift}, Ty_drift = {Ty_drift}\n")
        print("opening the main file\n")
        self.SapModel.File.OpenFile(str(asli_file_path))
        return Tx_drift, Ty_drift, asli_file_path

    def get_diaphragm_max_over_avg_drifts(
                    self,
                    loadcases=[],
                    only_ecc=False,
                    ):
        if not self.SapModel.GetModelIsLocked():
            self.SapModel.Analyze.RunAnalysis()
        if not loadcases:
            xy_names = self.get_xy_seismic_load_patterns(only_ecc)
            all_load_case_names = self.get_load_cases()
            loadcases = [i for i in xy_names if i in all_load_case_names]
        print(loadcases)
        x_names, y_names = self.get_load_patterns_in_XYdirection()
        self.select_load_cases(loadcases)
        TableKey = 'Diaphragm Max Over Avg Drifts'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey)
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        try:
            item_index = FieldsKeysIncluded.index("Item")
            case_name_index = FieldsKeysIncluded.index("OutputCase")
        except ValueError:
            return None
        new_data = []
        for row in data:
            name = row[case_name_index]
            if row[item_index].endswith("X"):
                if not name in x_names:
                    continue
            elif row[item_index].endswith("Y"):
                if not name in y_names:
                    continue
            new_data.append(row)
        return new_data, FieldsKeysIncluded

    def get_drifts(self, no_story, cdx, cdy, loadcases=None):
        if not self.SapModel.GetModelIsLocked():
            self.SapModel.Analyze.RunAnalysis()
        if not loadcases:
            drift_load_pattern_names = self.get_drift_load_pattern_names()
            all_load_case_names = self.get_load_cases()
            loadcases = [i for i in drift_load_pattern_names if i in all_load_case_names]
        print(loadcases)
        self.select_load_cases(loadcases)
        TableKey = 'Diaphragm Max Over Avg Drifts'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey, self.SapModel)
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        try:
            item_index = FieldsKeysIncluded.index("Item")
            case_name_index = FieldsKeysIncluded.index("OutputCase")
        except ValueError:
            return None, None
        # average_drift_index = FieldsKeysIncluded.index("Avg Drift")
        if no_story <= 5:
            limit = .025
        else:
            limit = .02
        x_names, y_names = self.get_load_patterns_in_XYdirection()
        new_data = []
        for row in data:
            name = row[case_name_index]
            if row[item_index].endswith("X"):
                if not name in x_names:
                    continue
                cd = cdx
            elif row[item_index].endswith("Y"):
                if not name in y_names:
                    continue
                cd = cdy
            allowable_drift = limit / cd
            row.append(f'{allowable_drift:.4f}')
            new_data.append(row)
        fields = list(FieldsKeysIncluded)
        fields.append('Allowable Drift')
        return new_data, fields

    def apply_cfactor_to_tabledata(self, TableData, FieldsKeysIncluded, building):
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        names_x, names_y = self.get_load_patterns_in_XYdirection()
        i_c = FieldsKeysIncluded.index('C')
        i_k = FieldsKeysIncluded.index('K')
        cx, cy = str(building.results[1]), str(building.results[2])
        kx, ky = str(building.kx), str(building.ky)
        cx_drift, cy_drift = str(building.results_drift[1]), str(building.results_drift[2])
        kx_drift, ky_drift = str(building.kx_drift), str(building.ky_drift)
        drift_load_pattern_names = self.get_drift_load_pattern_names()
        i_name = FieldsKeysIncluded.index("Name")
        for earthquake in data:
            if not earthquake[i_c]:
                continue
            name = earthquake[i_name]
            if name in drift_load_pattern_names:
                if name in names_x:
                    earthquake[i_c] = str(cx_drift)
                    earthquake[i_k] = str(kx_drift)
                elif name in names_y:
                    earthquake[i_c] = str(cy_drift)
                    earthquake[i_k] = str(ky_drift)
            elif name in names_x:
                earthquake[i_c] = str(cx)
                earthquake[i_k] = str(kx)
            elif name in names_y:
                earthquake[i_c] = str(cy)
                earthquake[i_k] = str(ky)
        table_data = self.unique_data(data)
        return table_data

    def apply_section_props_to_tabledata(self, TableData, FieldsKeysIncluded, sections):
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        i_shape = FieldsKeysIncluded.index('Shape')
        i_name = FieldsKeysIncluded.index('Name')
        for prop in data:
            if prop[i_shape] == 'Steel I/Wide Flange':
                name = prop[i_name]
                for section in sections:
                    if section.name == name:
                        prop[FieldsKeysIncluded.index('Area')] = str(section.area)
                        prop[FieldsKeysIncluded.index('J')] = str(section.J)
                        prop[FieldsKeysIncluded.index('I33')] = str(section.Ix)
                        prop[FieldsKeysIncluded.index('I22')] = str(section.Iy)
                        prop[FieldsKeysIncluded.index('As2')] = str(section.ASy)
                        prop[FieldsKeysIncluded.index('As3')] = str(section.ASx)
                        prop[FieldsKeysIncluded.index('S33Pos')] = str(section.Sx)
                        prop[FieldsKeysIncluded.index('S33Neg')] = str(section.Sx)
                        prop[FieldsKeysIncluded.index('S22Pos')] = str(section.Sy)
                        prop[FieldsKeysIncluded.index('S22Neg')] = str(section.Sy)
                        prop[FieldsKeysIncluded.index('Z33')] = str(section.Zx)
                        prop[FieldsKeysIncluded.index('Z22')] = str(section.Zy)
                        prop[FieldsKeysIncluded.index('R33')] = str(section.Rx)
                        prop[FieldsKeysIncluded.index('R22')] = str(section.Ry)
                        prop[FieldsKeysIncluded.index('Cw')] = str(section.cw)
                        break
        table_data = self.unique_data(data)
        return table_data

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
            # story = row['OverStory']
            case = row['Name']
            if case in cases:
                ecc_length = df[
                    # (df['Story'] == story) & 
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

    def apply_cfactor_to_edb(
            self,
            building,
            ):
        print("Applying cfactor to edb\n")
        self.SapModel.SetModelIsLocked(False)
        self.select_all_load_patterns()
        TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey, self.SapModel)
        # if is_auto_load_yes_in_seismic_load_patterns(TableData, FieldsKeysIncluded):
        #     return 1
        TableData = self.apply_cfactor_to_tabledata(TableData, FieldsKeysIncluded, building, self.SapModel)
        NumFatalErrors, ret = self.write_seismic_user_coefficient(TableKey, FieldsKeysIncluded, TableData)
        print(f"NumFatalErrors, ret = {NumFatalErrors}, {ret}")
        return NumFatalErrors

    def apply_cfactor_to_edb_and_analyze(self, building):
        self.apply_cfactor_to_edb(building)
        ret = self.SapModel.Analyze.RunAnalysis()
        return ret

    def get_drift_periods_calculate_cfactor_and_apply_to_edb(
            self,
            widget,
            ):
        Tx, Ty, _ = self.get_drift_periods()
        widget.xTAnalaticalSpinBox.setValue(Tx)
        widget.yTAnalaticalSpinBox.setValue(Ty)
        widget.calculate()
        num_errors = self.apply_cfactor_to_edb(widget.final_building)
        return num_errors, etabs

    def calculate_drifts(
                self,
                widget,
                no_story=None,
                auto_no_story=False,
                auto_height=False,
                loadcases=None,
                ):
        if auto_height:
            hx = self.get_heights()[0]
            widget.HSpinBox.setValue(hx)
        if auto_no_story:
            no_story = self.get_no_of_stories()[0]
            widget.storySpinBox.setValue(no_story)
        if not no_story:
            no_story = widget.storySpinBox.value()
        self.get_drift_periods_calculate_cfactor_and_apply_to_edb(widget)
        if loadcases:
            self.set_load_cases_to_analyze(loadcases)
        self.SapModel.Analyze.RunAnalysis()
        if loadcases:
            self.set_load_cases_to_analyze()
        cdx = widget.final_building.x_system.cd
        cdy = widget.final_building.y_system.cd
        drifts, headers = self.get_drifts(no_story, cdx, cdy, loadcases)
        return drifts, headers

    def is_etabs_running(self):
        try:
            comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
            return True
        except OSError:
            return False

    def write_section_names_to_etabs(self, sections, mat_name='STEEL_CIVILTOOLS'):
        mat_names = self.SapModel.Propmaterial.GetNameList()[1]
        if not mat_name in mat_names:
            self.SapModel.Propmaterial.SetMaterial(mat_name, 1)
        ret = set()
        for section in sections:
            d = section.d_equivalentI
            bf = section.bf_equivalentI
            tw = section.tw_equivalentI
            tf = section.tf_equivalentI
            name = section.name
            r = self.SapModel.PropFrame.SetISection(name, mat_name, d, bf, tf, tw, bf, tf, -1, "", "")
            ret.add(r)
        return ret 

    @staticmethod
    def get_section_property_FieldsKeysIncluded(in_fields):
        convert_keys = {
            'FilletRad' : 'Fillet Radius',
            'CGOffset3' : 'CG Offset 3', 
            'CGOffset2' : 'CG Offset 2',
            'PNAOffset3': 'PNA Offset 3',
            'PNAOffset2': 'PNA Offset 2',
            'SCOffset3' : 'SC Offset 3',
            'SCOffset2' : 'SC Offset 2',
            'AMod' : 'Area Modifier',
            'A2Mod' : 'As2 Modifier',
            'A3Mod' : 'As3 Modifier',
            'JMod' : 'J Modifier',
            'I3Mod' : 'I33 Modifier',
            'I2Mod' :  'I22 Modifier',
            'MMod' : 'Mass Modifier',
            'WMod' : 'Weight Modifier',
        }

        out_fields = []
        for f in in_fields:
            out_f = convert_keys.get(f, f)
            out_fields.append(out_f)
        return out_fields

    def write_section_props_to_etabs(self, sections):
        TableKey = 'Frame Section Property Definitions - Summary'
        [_, TableVersion, FieldsKeysIncluded, NumberRecords, TableData, _] = self.read_table(TableKey, self.SapModel)
        TableData = self.apply_section_props_to_tabledata(TableData, FieldsKeysIncluded, sections)
        FieldsKeysIncluded1 = self.get_section_property_FieldsKeysIncluded(FieldsKeysIncluded)
        self.SapModel.DatabaseTables.SetTableForEditingArray(TableKey, TableVersion, FieldsKeysIncluded1, NumberRecords, TableData)
        NumFatalErrors, ret = self.apply_table()
        print(f"NumFatalErrors, ret = {NumFatalErrors}, {ret}")
        return NumFatalErrors, ret

    def apply_sections_to_etabs(self, sections, mat_name='STEEL_CIVILTOOLS'):
        self.write_section_names_to_etabs(sections, mat_name)
        print('writed sections name to etabs')
        self.SapModel.File.Save()
        NumFatalErrors, ret =self.write_section_props_to_etabs(sections)
        print('writed sections properties to etabs')
        return NumFatalErrors, ret

    def import_sections_to_etabs(self, sections, mat_name='STEEL_CIVILTOOLS'):
        if not sections:
            return
        mat_names = self.SapModel.Propmaterial.GetNameList()[1]
        if not mat_name in mat_names:
            self.SapModel.Propmaterial.SetMaterial(mat_name, 1)
        import tempfile
        default_tmp_dir = tempfile._get_default_tempdir()
        name = 'civiltools.xml'
        filename = Path(default_tmp_dir) /  name
        section = sections[0]
        section.exportXml(filename, sections)
        ret = set()
        for section in sections:
            name = section.name
            r = self.SapModel.PropFrame.ImportProp(name, mat_name, str(filename), name)
            ret.add(r)
        return ret

    def show_point(self, story, label):
        self.SapModel.SelectObj.ClearSelection()
        name = self.SapModel.PointObj.GetNameFromLabel(label, story)[0]
        self.SapModel.PointObj.SetSelected(name, True)
        self.SapModel.View.RefreshView()
        return True
        
    def get_magnification_coeff_aj(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import geometry, rho
        x_names, y_names = self.get_load_patterns_in_XYdirection(only_ecc=True)
        story_length = geometry.get_stories_length(self.SapModel)
        data, headers = self.get_diaphragm_max_over_avg_drifts(only_ecc=True)
        i_ratio = headers.index('Ratio')
        i_story = headers.index('Story')
        i_case = headers.index('OutputCase')
        for d in data:
            ratio = float(d[i_ratio])
            story_name = d[i_story]
            loadcase = d[i_case]
            aj = (ratio / 1.2) ** 2
            if aj < 1:
                aj = 1
            elif aj > 3:
                aj = 3
            ecc_ratio = aj * .05
            length = story_length[story_name]
            if loadcase in x_names:
                len = length[1]
                dir_ = 'X'
            elif loadcase in y_names:
                len = length[0]
                dir_ = 'Y'
            ecc_len = ecc_ratio * len
            diaphs = rho.get_story_diaphragms(self.SapModel, story_name)
            diaphs = ','.join(list(diaphs))
            d.extend([aj, ecc_ratio, len, ecc_len, dir_, diaphs])
        headers = headers + ('aj', 'Ecc. Ratio', 'Length (Cm)', 'Ecc. Length (Cm)', 'Dir', 'Diaph')
        return data, headers

    def apply_aj_df(self, df):
        print("Applying cfactor to edb\n")
        self.SapModel.SetModelIsLocked(False)
        self.select_all_load_patterns()
        TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey, self.SapModel)
        NumFatalErrors, ret = self.write_aj_user_coefficient(TableKey, FieldsKeysIncluded, TableData, df)
        print(f"NumFatalErrors, ret = {NumFatalErrors}, {ret}")
        return NumFatalErrors, ret

class Build:
    def __init__(self):
        self.kx = 1
        self.ky = 1
        self.kx_drift = 1
        self.ky_drift = 1
        self.results = [True, 1, 1]
        self.results_drift = [True, 1, 1]

                
if __name__ == '__main__':
    etabs = EtabsModel()
    etabs.apply_cfactor_to_edb()
    # TableKey = 'Frame Section Property Definitions - Summary'
    # [_, TableVersion, FieldsKeysIncluded, NumberRecords, TableData, _] = self.read_table(TableKey, self.SapModel)
    # get_load_patterns()
    # x, y = get_load_patterns_in_XYdirection()
    # print(x)
    # print(y)
    # building = Build()
    # apply_cfactor_to_edb(building)
    # get_beqams_columns()
    # self.SapModel = etabs.self.SapModel
    # TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
    # [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey, self.SapModel)
    # is_auto_load_yes_in_seismic_load_patterns(TableData, FieldsKeysIncluded)
    get_drifts(4, 4, 4)