from typing import Tuple, Union


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

    def get_loadcase_withtype(self, n) -> list:
        '''
        return load cases that match load case type number:
        1 : LinearStatic
        2 : NonlinearStatic
        3 : Modal
        4 : ResponseSpectrum
        '''
        load_cases = self.get_load_cases()
        ret = []
        for lc in load_cases:
            if self.SapModel.LoadCases.GetTypeOAPI(lc)[0] == n:
                ret.append(lc)
        return ret

    def get_modal_loadcase_name(self):
        load_cases = self.get_load_cases()
        for lc in load_cases:
            if self.SapModel.LoadCases.GetTypeOAPI(lc)[0] == 3:
                return lc
        return None

    def multiply_response_spectrum_scale_factor(self,
            name : str,
            scale : float,
            scale_min : Union[float, bool] = 1.0,
            all : bool = False,
            ):
        self.etabs.unlock_model()
        if scale_min is not None:
            scale = max(scale, scale_min)
        ret = self.SapModel.LoadCases.ResponseSpectrum.GetLoads(name)
        if all:
            scales = (i * scale for i in ret[3])
            scales = tuple(scales)
        else:
            scales = (ret[3][0] * scale,) + tuple(ret[3][1:])
        ret[3] = scales
        self.SapModel.LoadCases.ResponseSpectrum.SetLoads(name, *ret[:-1])
        return None
        
        
        

    