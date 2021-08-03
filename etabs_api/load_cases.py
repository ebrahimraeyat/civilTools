class LoadCases:
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