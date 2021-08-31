from typing import Iterable, Tuple, Union

from numpy import int16


class LoadCases:
    def __init__(
                self,
                etabs=None,
                ):
        self.etabs = etabs
        self.SapModel = etabs.SapModel

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

    def get_spectral_with_angles(self,
                angles : Iterable,
                specs : Iterable = None,
                ) -> dict:
        '''
        return angles and Response spectrum loadcase
        {0: spec}
        '''
        table = 'Load Case Definitions - Response Spectrum'
        df = self.etabs.database.read(table, to_dataframe=True, cols=['Name', 'Angle'])
        df.dropna(inplace=True)
        df['Angle'] = df['Angle'].astype(int16)
        df.drop_duplicates(['Name'], keep=False, inplace=True)
        df = df[df['Angle'].isin(angles)]
        if specs is not None:
            df = df[df['Name'].isin(specs)]
        # df.drop_duplicates(['Angle'], keep='first', inplace=True)
        angles_specs = dict()
        for _, row in df.iterrows():
            angle = row['Angle']
            name = row['Name']
            angles_specs[int(angle)] = name
        return angles_specs

    def reset_scales_for_response_spectrums(self,
                    scale : float = 1,
                    loadcases : Union[list, bool] = None,
                    length_unit : str = 'mm',  # 'cm', 'm'
                    ) -> None:
        self.etabs.unlock_model()
        self.etabs.set_current_unit('N', length_unit)
        if loadcases is None:
            loadcases = self.get_loadcase_withtype(4)
        for name in loadcases:
            ret = self.SapModel.LoadCases.ResponseSpectrum.GetLoads(name)
            scales = (scale,) + tuple(ret[3][1:])
            ret[3] = scales
            self.SapModel.LoadCases.ResponseSpectrum.SetLoads(name, *ret[:-1])
        return None
        
        
        

    