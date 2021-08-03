
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