from os import stat
import sys
import comtypes.client
from pathlib import Path

civiltools_path = Path(__file__).parent.parent
sys.path.insert(0, str(civiltools_path))

from etabs_api.load_patterns import LoadPatterns
from etabs_api.load_cases import LoadCases
from etabs_api.story import Story
from etabs_api.frame_obj import FrameObj
from etabs_api.analyze import Analyze
from etabs_api.view import View
from etabs_api.database import DatabaseTables
from etabs_api.sections.sections import Sections
from etabs_api.results import Results
from etabs_api.points import Points

__all__ = ['EtabsModel']


class EtabsModel:
    force_units = dict(N=3, kN=4, kgf=5, tonf=6)
    length_units = dict(mm=4, cm=5, m=6)

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
        self.load_patterns = LoadPatterns(None, self)
        self.load_cases = LoadCases(self.SapModel, None)
        self.story = Story(None, self)
        self.frame_obj = FrameObj(self)
        self.analyze = Analyze(self.SapModel, None)
        self.view = View(self.SapModel, None)
        self.database = DatabaseTables(None, self)
        self.sections = Sections(self.SapModel, None)
        self.results = Results(None, self)
        self.points = Points(None, self)
    
    def close_etabs(self):
        self.SapModel.SetModelIsLocked(False)
        self.etabs.ApplicationExit(False)
        self.SapModel = None
        self.etabs = None

    def run_analysis(self, open_lock=False):
        if self.SapModel.GetModelIsLocked():
            if open_lock:
                self.SapModel.SetModelIsLocked(False)
                print('Run Alalysis ...')
                self.SapModel.analyze.RunAnalysis()
        else:
            print('Run Alalysis ...')
            self.SapModel.analyze.RunAnalysis()

    def set_current_unit(self, force, length):
        force_enum = EtabsModel.force_units[force]
        len_enum = EtabsModel.length_units[length]
        self.SapModel.SetPresentUnits_2(force_enum, len_enum, 2)

    def get_file_name_without_suffix(self):
        f = Path(self.SapModel.GetModelFilename())
        name = f.name.replace(f.suffix, '')
        return name

    @staticmethod
    def get_from_list_table(
            list_table: list,
            columns: list,
            values: list,
            ) -> filter:
        from operator import itemgetter
        itemget = itemgetter(*columns)
        assert len(columns) == len(values)
        if len(columns) == 1:
            result = filter(lambda x: itemget(x) == values[0], list_table)
        else:
            result = filter(lambda x: itemget(x) == values, list_table)
        return result

    def save_as(self, name):
        if not name.lower().endswith('.edb'):
            name += '.EDB'
        asli_file_path = Path(self.SapModel.GetModelFilename())
        asli_file_path = asli_file_path.with_suffix('.EDB')
        new_file_path = asli_file_path.with_name(name)
        self.SapModel.File.Save(str(new_file_path))
        return asli_file_path, new_file_path

    @staticmethod
    def save_to_json(json_file, data):
        import json
        with open(json_file, 'w') as f:
            json.dump(data, f)

    @staticmethod
    def load_from_json(json_file):
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
        return data

    def save_to_json_in_edb_folder(self, json_name, data):
        json_file = Path(self.SapModel.GetModelFilepath()) / json_name
        self.save_to_json(json_file, data)

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
                if self.SapModel.FrameObj.GetDesignOrientation(label)[0] == 1: # Column
                    IMod = IMod_col_wall
                elif self.SapModel.FrameObj.GetDesignOrientation(label)[0] == 2:   # Beam
                    IMod = IMod_beam
                modifiers = list(self.SapModel.FrameObj.GetModifiers(label)[0])
                modifiers[4:6] = [IMod, IMod]
                self.SapModel.FrameObj.SetModifiers(label, modifiers)

        # run model (this will create the analysis model)
        print("start running T file analysis")
        modal_case = self.load_cases.get_modal_loadcase_name()
        self.analyze.set_load_cases_to_analyze(modal_case)
        self.SapModel.Analyze.RunAnalysis()

        TableKey = "Modal Participating Mass Ratios"
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.database.read_table(TableKey)
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
        self.run_analysis()
        if not loadcases:
            xy_names = self.load_patterns.get_xy_seismic_load_patterns(only_ecc)
            all_load_case_names = self.load_cases.get_load_cases()
            loadcases = [i for i in xy_names if i in all_load_case_names]
        print(loadcases)
        x_names, y_names = self.load_patterns.get_load_patterns_in_XYdirection()
        self.load_cases.select_load_cases(loadcases)
        TableKey = 'Diaphragm Max Over Avg Drifts'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.database.read_table(TableKey)
        data = self.database.reshape_data(FieldsKeysIncluded, TableData)
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
        self.run_analysis()
        if loadcases is None:
            drift_load_pattern_names = self.load_patterns.get_drift_load_pattern_names()
            all_load_case_names = self.load_cases.get_load_cases()
            loadcases = [i for i in drift_load_pattern_names if i in all_load_case_names]
        print(loadcases)
        x_names, y_names = self.load_patterns.get_load_patterns_in_XYdirection()
        self.load_cases.select_load_cases(loadcases)
        TableKey = 'Diaphragm Max Over Avg Drifts'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.database.read_table(TableKey)
        data = self.database.reshape_data(FieldsKeysIncluded, TableData)
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
        data = self.database.reshape_data(FieldsKeysIncluded, TableData)
        names_x, names_y = self.load_patterns.get_load_patterns_in_XYdirection()
        i_c = FieldsKeysIncluded.index('C')
        i_k = FieldsKeysIncluded.index('K')
        cx, cy = str(building.results[1]), str(building.results[2])
        kx, ky = str(building.kx), str(building.ky)
        cx_drift, cy_drift = str(building.results_drift[1]), str(building.results_drift[2])
        kx_drift, ky_drift = str(building.kx_drift), str(building.ky_drift)
        drift_load_pattern_names = self.load_patterns.get_drift_load_pattern_names()
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
        table_data = self.database.unique_data(data)
        return table_data

    def apply_cfactor_to_edb(
            self,
            building,
            ):
        print("Applying cfactor to edb\n")
        self.SapModel.SetModelIsLocked(False)
        self.load_patterns.select_all_load_patterns()
        TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.database.read_table(TableKey)
        # if is_auto_load_yes_in_seismic_load_patterns(TableData, FieldsKeysIncluded):
        #     return 1
        TableData = self.apply_cfactor_to_tabledata(TableData, FieldsKeysIncluded, building)
        NumFatalErrors, ret = self.database.write_seismic_user_coefficient(TableKey, FieldsKeysIncluded, TableData)
        print(f"NumFatalErrors, ret = {NumFatalErrors}, {ret}")
        return NumFatalErrors

    def get_drift_periods_calculate_cfactor_and_apply_to_edb(
            self,
            widget,
            ):
        Tx, Ty, _ = self.get_drift_periods()
        widget.xTAnalaticalSpinBox.setValue(Tx)
        widget.yTAnalaticalSpinBox.setValue(Ty)
        widget.calculate()
        num_errors = self.apply_cfactor_to_edb(widget.final_building)
        return num_errors

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
        # if loadcases is not None:
        #     self.analyze.set_load_cases_to_analyze(loadcases)
        self.SapModel.Analyze.RunAnalysis()
        # if loadcases is not None:
        #     self.analyze.set_load_cases_to_analyze()
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

    def get_magnification_coeff_aj(self):
        # sys.path.insert(0, str(civiltools_path))
        x_names, y_names = self.load_patterns.get_load_patterns_in_XYdirection(only_ecc=True)
        story_length = self.story.get_stories_length()
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
            diaphs = self.story.get_story_diaphragms(story_name)
            diaphs = ','.join(list(diaphs))
            d.extend([aj, ecc_ratio, len, ecc_len, dir_, diaphs])
        headers = headers + ('aj', 'Ecc. Ratio', 'Length (Cm)', 'Ecc. Length (Cm)', 'Dir', 'Diaph')
        return data, headers

    def apply_aj_df(self, df):
        print("Applying cfactor to edb\n")
        self.SapModel.SetModelIsLocked(False)
        self.load_patterns.select_all_load_patterns()
        TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.database.read_table(TableKey)
        NumFatalErrors, ret = self.database.write_aj_user_coefficient(TableKey, FieldsKeysIncluded, TableData, df)
        print(f"NumFatalErrors, ret = {NumFatalErrors}, {ret}")
        return NumFatalErrors, ret

    def get_irregularity_of_mass(self, story_mass=None):
        if not story_mass:
            story_mass = self.database.get_story_mass()
        for i, sm in enumerate(story_mass):
            m_neg1 = float(story_mass[i - 1][1]) * 1.5
            m = float(sm[1])
            if i != len(story_mass) - 1:
                m_plus1 = float(story_mass[i + 1][1]) * 1.5
            else:
                m_plus1 = m
            if i == 0:
                m_neg1 = m
            sm.extend([m_neg1, m_plus1])
        fields = ('Story', 'Mass X', '1.5 * Below', '1.5 * Above')
        return story_mass, fields

    def add_load_case_in_center_of_rigidity(self, story_name, x, y):
        self.SapModel.SetPresentUnits(7)
        z = self.SapModel.story.GetElevation(story_name)[0]
        point_name = self.SapModel.PointObj.AddCartesian(float(x),float(y) , z)[0]  
        diaph = self.story.get_story_diaphragms(story_name).pop()
        self.SapModel.PointObj.SetDiaphragm(point_name, 3, diaph)
        LTYPE_OTHER = 8
        lp_name = f'STIFFNESS_{story_name}'
        self.SapModel.LoadPatterns.Add(lp_name, LTYPE_OTHER, 0, True)
        load = 1000
        PointLoadValue = [load,load,0,0,0,0]
        self.SapModel.PointObj.SetLoadForce(point_name, lp_name, PointLoadValue)
        self.analyze.set_load_cases_to_analyze(lp_name)
        return point_name, lp_name

    def get_story_stiffness_modal_way(self):
        story_mass = self.database.get_story_mass()[::-1]
        story_mass = {key: value for key, value in story_mass}
        stories = list(story_mass.keys())
        dx, dy, wx, wy = self.database.get_stories_displacement_in_xy_modes()
        story_stiffness = {}
        n = len(story_mass)
        for i, (phi_x, phi_y) in enumerate(zip(dx.values(), dy.values())):
            if i == n - 1:
                phi_neg_x = 0
                phi_neg_y = 0
            else:
                story_neg = stories[i + 1]
                phi_neg_x = dx[story_neg]
                phi_neg_y = dy[story_neg]
            d_phi_x = phi_x - phi_neg_x
            d_phi_y = phi_y - phi_neg_y
            sigma_x = 0
            sigma_y = 0
            for j in range(0, i + 1):
                story_j = stories[j]
                m_j = float(story_mass[story_j])
                phi_j_x = dx[story_j]
                phi_j_y = dy[story_j]
                sigma_x += m_j * phi_j_x
                sigma_y += m_j * phi_j_y
            kx = wx ** 2 * sigma_x / d_phi_x
            ky = wy ** 2 * sigma_y / d_phi_y
            story_stiffness[stories[i]] = [kx, ky]
        return story_stiffness

    def get_story_stiffness_2800_way(self):
        asli_file_path = Path(self.SapModel.GetModelFilename())
        if asli_file_path.suffix.lower() != '.edb':
            asli_file_path = asli_file_path.with_suffix(".EDB")
        dir_path = asli_file_path.parent.absolute()
        story_names = self.SapModel.Story.GetNameList()[1]
        center_of_rigidity = self.database.get_center_of_rigidity()
        story_stiffness = {}
        import shutil
        for story_name in story_names:
            story_file_path = dir_path / f'STIFFNESS_{story_name}.EDB'
            print(f"Saving file as {story_file_path}\n")
            shutil.copy(asli_file_path, story_file_path)
            print(f"Opening file {story_file_path}\n")
            self.SapModel.File.OpenFile(str(story_file_path))
            x, y = center_of_rigidity[story_name]
            point_name, lp_name = self.add_load_case_in_center_of_rigidity(
                    story_name, x, y)
            self.story.fix_below_stories(story_name)
            self.SapModel.View.RefreshView()
            self.SapModel.Analyze.RunAnalysis()
            disp_x, disp_y = self.results.get_point_xy_displacement(point_name, lp_name)
            kx, ky = 1000 / abs(disp_x), 1000 / abs(disp_y)
            story_stiffness[story_name] = [kx, ky]
        self.SapModel.File.OpenFile(str(asli_file_path))
        return story_stiffness

    def get_story_stiffness_earthquake_way(
                self,
                loadcases: list=None,
                ):
        if loadcases is None:
            loadcases = self.load_patterns.get_EX_EY_load_pattern()
        assert len(loadcases) == 2
        EX, EY = loadcases
        self.run_analysis()
        self.SapModel.SetPresentUnits_2(5, 6, 2)
        self.load_cases.select_load_cases(loadcases)
        TableKey = 'Story Stiffness'
        [_, _, FieldsKeysIncluded, _, TableData, _] = self.database.read_table(TableKey)
        i_story = FieldsKeysIncluded.index('Story')
        i_case = FieldsKeysIncluded.index('OutputCase')
        i_stiff_x = FieldsKeysIncluded.index('StiffX')
        i_stiff_y = FieldsKeysIncluded.index('StiffY')
        data = self.database.reshape_data(FieldsKeysIncluded, TableData)
        columns = (i_case,)
        values_x = (EX,)
        values_y = (EY,)
        result_x = self.get_from_list_table(data, columns, values_x)
        result_y = self.get_from_list_table(data, columns, values_y)
        story_stiffness = {}
        for x, y in zip(list(result_x), list(result_y)):
            story = x[i_story]
            stiff_x = float(x[i_stiff_x])
            stiff_y = float(y[i_stiff_y])
            story_stiffness[story] = [stiff_x, stiff_y]
        return story_stiffness

    def get_story_stiffness_table(self, way='2800', story_stiffness=None):
        '''
        way can be '2800', 'modal' , 'earthquake'
        '''
        name = self.get_file_name_without_suffix()
        if not story_stiffness:
            if way == '2800':
                story_stiffness = self.get_story_stiffness_2800_way()
            elif way == 'modal':
                story_stiffness = self.get_story_stiffness_modal_way()
            elif way == 'earthquake':
                story_stiffness = self.get_story_stiffness_earthquake_way()
        stories = list(story_stiffness.keys())
        retval = []
        for i, story in enumerate(stories):
            stiffness = story_stiffness[story]
            kx = stiffness[0]
            ky = stiffness[1]
            if i == 0:
                stiffness.extend(['-', '-'])
            else:
                k1 = story_stiffness[stories[i - 1]]
                stiffness.extend([
                    kx / k1[0] if k1[0] != 0 else '-',
                    ky / k1[1] if k1[1] != 0 else '-',
                    ])

            if len(stories[:i]) >= 3:
                k2 = story_stiffness[stories[i - 2]]
                k3 = story_stiffness[stories[i - 3]]
                ave_kx = (k1[0] + k2[0] + k3[0]) / 3
                ave_ky = (k1[1] + k2[1] + k3[1]) / 3
                stiffness.extend([kx / ave_kx, ky / ave_ky])
            else:
                stiffness.extend(['-', '-'])
            retval.append((story, *stiffness))
        fields = ('Story', 'Kx', 'Ky', 'Kx / kx+1', 'Ky / ky+1', 'Kx / kx_3ave', 'Ky / ky_3ave')
        json_file = f'{name}_story_stiffness_{way}_table.json'
        self.save_to_json_in_edb_folder(json_file, (retval, fields))
        return retval, fields

    def get_story_forces_with_percentages(
                self,
                loadcases: list=None,
                ):
        vx, vy = self.results.get_base_react()
        story_forces, _ , fields = self.database.get_story_forces(loadcases)
        new_data = []
        i_vx = fields.index('VX')
        i_vy = fields.index('VY')
        for story_force in story_forces:
            fx = float(story_force[i_vx])
            fy = float(story_force[i_vy])
            story_force.extend([f'{fx/vx:.3f}', f'{fy/vy:.3f}'])
            new_data.append(story_force)
        fields = list(fields)
        fields.extend(['Vx %', 'Vy %'])
        return new_data, fields


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
    # [_, TableVersion, FieldsKeysIncluded, NumberRecords, TableData, _] = self.database.read_table(TableKey, self.SapModel)
    # get_load_patterns()
    # x, y = get_load_patterns_in_XYdirection()
    # print(x)
    # print(y)
    # building = Build()
    # apply_cfactor_to_edb(building)
    # get_beqams_columns()
    # self.SapModel = etabs.self.SapModel
    # TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
    # [_, _, FieldsKeysIncluded, _, TableData, _] = self.database.read_table(TableKey, self.SapModel)
    # is_auto_load_yes_in_seismic_load_patterns(TableData, FieldsKeysIncluded)
    get_drifts(4, 4, 4)