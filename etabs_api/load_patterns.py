class LoadPatterns:
    def __init__(
                self,
                SapModel,
                ):
        self.SapModel = SapModel

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

    def get_load_patterns(self):
        return self.SapModel.LoadPatterns.GetNameList(0, [])[1]

    def get_special_load_pattern_names(self, n=5):
        '''
        Each load patterns has a special number ID, for example:
        DEAD is 1, SEISMIC is 5
        '''
        lps = self.get_load_patterns()
        names = []
        for lp in lps:
            if self.SapModel.LoadPatterns.GetLoadType(lp)[0] == n:
                names.append(lp)
        return names
        
    def get_drift_load_pattern_names(self):
        '''
        Drift loadType number is 37, when user tick the eccentricity of load,
        etabs create aditional (1/3), (2/3) and (3/3) load when structure is analyzed
        '''
        return self.get_special_load_pattern_names(37)

    def get_load_patterns_in_XYdirection(self, only_ecc=False):
        '''
        return list of load pattern names, x and y direction separately
        '''
        self.select_all_load_patterns()
        TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey)
        i_xdir = FieldsKeysIncluded.index('XDir')
        i_xdir_plus = FieldsKeysIncluded.index('XDirPlusE')
        i_xdir_minus = FieldsKeysIncluded.index('XDirMinusE')
        i_ydir = FieldsKeysIncluded.index('YDir')
        i_ydir_plus = FieldsKeysIncluded.index('YDirPlusE')
        i_ydir_minus = FieldsKeysIncluded.index('YDirMinusE')
        i_name = FieldsKeysIncluded.index('Name')
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        names_x = set()
        names_y = set()
        for earthquake in data:
            name = earthquake[i_name]
            if only_ecc:
                if all((
                earthquake[i_xdir] == 'Yes',
                earthquake[i_xdir_minus] == 'No',
                earthquake[i_xdir_plus] == 'No',
                )) or all((
                earthquake[i_ydir] == 'Yes',
                earthquake[i_ydir_minus] == 'No',
                earthquake[i_ydir_plus] == 'No',
                )):
                    continue
            if any((
                earthquake[i_xdir] == 'Yes',
                earthquake[i_xdir_minus] == 'Yes',
                earthquake[i_xdir_plus] == 'Yes',
            )):
                names_x.add(name)
            elif any((
                earthquake[i_ydir] == 'Yes',
                earthquake[i_ydir_minus] == 'Yes',
                earthquake[i_ydir_plus] == 'Yes',
            )):
                names_y.add(name)
            
        return names_x, names_y

    def get_EX_EY_load_pattern(self):
        '''
        return earthquakes in x, y direction that did not ecnetricity
        '''
        self.select_all_load_patterns()
        TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.read_table(TableKey)
        i_xdir = FieldsKeysIncluded.index('XDir')
        i_xdir_plus = FieldsKeysIncluded.index('XDirPlusE')
        i_xdir_minus = FieldsKeysIncluded.index('XDirMinusE')
        i_ydir = FieldsKeysIncluded.index('YDir')
        i_ydir_plus = FieldsKeysIncluded.index('YDirPlusE')
        i_ydir_minus = FieldsKeysIncluded.index('YDirMinusE')
        i_name = FieldsKeysIncluded.index('Name')
        data = self.reshape_data(FieldsKeysIncluded, TableData)
        name_x = None
        name_y = None
        drift_lp_names = self.get_drift_load_pattern_names()
        for earthquake in data:
            name = earthquake[i_name]
            if all((
                    not name_x,
                    not name in drift_lp_names,
                    earthquake[i_xdir] == 'Yes',
                    earthquake[i_xdir_minus] == 'No',
                    earthquake[i_xdir_plus] == 'No',
                )):
                    name_x = name
            if all((
                    not name_y,
                    not name in drift_lp_names,
                    earthquake[i_ydir] == 'Yes',
                    earthquake[i_ydir_minus] == 'No',
                    earthquake[i_ydir_plus] == 'No',
                )):
                    name_y = name
            if name_x and name_y:
                break
        return name_x, name_y

    def get_xy_seismic_load_patterns(self, only_ecc=False):
        x_names, y_names = self.get_load_patterns_in_XYdirection(only_ecc)
        drift_load_pattern_names = self.get_drift_load_pattern_names()
        xy_names = x_names.union(y_names).difference(drift_load_pattern_names)
        return xy_names
      
    def select_all_load_patterns(self):
        load_pattern_names = list(self.get_load_patterns())
        self.SapModel.DatabaseTables.SetLoadPatternsSelectedForDisplay(load_pattern_names) 
