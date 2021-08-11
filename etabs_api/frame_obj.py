from pathlib import Path
from typing import Iterable, Union


class FrameObj:
    def __init__(
                self,
                etabs=None,
                ):
        self.etabs = etabs
        self.SapModel = self.etabs.SapModel

    def set_end_release_frame(self, name):
        end_release = self.SapModel.FrameObj.GetReleases(name)
        II = list(end_release[0])
        JJ = list(end_release[1])
        II[3:] = [True] * len(II[3:])
        JJ[4:] = [True] * len(II[4:])
        end_release[0] = tuple(II)
        end_release[1] = tuple(JJ)
        end_release.insert(0, name)
        er = self.SapModel.FrameObj.SetReleases(*end_release)
        return er

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

    def get_columns_pmm_and_beams_rebars(self, frame_names):
        self.SapModel.SelectObj.ClearSelection()
        self.etabs.analyze.set_load_cases_to_analyze()
        self.etabs.run_analysis()
        # set_frame_obj_selected(SapModel, frame_names)
        if not self.SapModel.DesignConcrete.GetResultsAvailable():
            print('Start Design ...')
            self.SapModel.DesignConcrete.StartDesign()
        self.SapModel.SetPresentUnits_2(5, 5, 2)
        beams, columns = self.get_beams_columns()
        beams = set(frame_names).intersection(beams)
        columns = set(frame_names).intersection(columns)
        columns_pmm = dict()
        for col in columns:
            pmm = max(self.SapModel.DesignConcrete.GetSummaryResultsColumn(col)[6])
            columns_pmm[col] = round(pmm, 3)
        beams_rebars = dict()
        for name in beams:
            d = dict()
            beam_rebars = self.SapModel.DesignConcrete.GetSummaryResultsBeam(name)
            d['location'] = beam_rebars[2]
            d['TopArea'] = beam_rebars[4]
            d['BotArea'] = beam_rebars[6]
            d['VRebar'] = beam_rebars[8]
            beams_rebars[name] = d
        return columns_pmm, beams_rebars

    def combine_beams_columns_weakness_structure(
                self,
                columns_pmm,
                beams_rebars,
                columns_pmm_weakness,
                beams_rebars_weakness,
                ):
        columns_pmm_main_and_weakness = []
        for key, value in columns_pmm.items():
            value2 = columns_pmm_weakness[key]
            label, story, _ = self.SapModel.FrameObj.GetLabelFromName(key)
            ratio = round(value2/value, 3)
            columns_pmm_main_and_weakness.append((story, label, value, value2, ratio))
        col_fields = ('Story', 'Label', 'PMM Ratio1', 'PMM ratio2', 'Ratio')
        beams_rebars_main_and_weakness = []
        for key, d in beams_rebars.items():
            d2 = beams_rebars_weakness[key]
            label, story, _ = self.SapModel.FrameObj.GetLabelFromName(key)
            locations = d['location']
            top_area1 = d['TopArea']
            top_area2 = d2['TopArea']
            bot_area1 = d['BotArea']
            bot_area2 = d2['BotArea']
            vrebar1 = d['VRebar']
            vrebar2 = d2['VRebar']
            for l, ta1, ta2, ba1, ba2, v1, v2 in zip(locations,
                    top_area1, top_area2, bot_area1, bot_area2, vrebar1, vrebar2):
                beams_rebars_main_and_weakness.append((
                    story,
                    label,
                    l,
                    ta1, ta2,
                    ba1, ba2,
                    v1, v2,
                    ))
        beam_fields = (
                'Story', 'Label', 'location',
                'Top Area1', 'Top Area2',
                'Bot Area1', 'Bot Area2',
                'VRebar1', 'VRebar2',
                )
        json_name = 'columns_pmm_beams_rebars.json'
        data = (columns_pmm_main_and_weakness, col_fields,
            beams_rebars_main_and_weakness, beam_fields)
        self.etabs.save_to_json_in_edb_folder(json_name, data)
        return (columns_pmm_main_and_weakness, col_fields,
            beams_rebars_main_and_weakness, beam_fields)

    def get_beams_columns_weakness_structure(
                    self,
                    name: str = '',
                    weakness_filename="weakness.EDB"
                    ):
        if not name:
            try:
                name = self.SapModel.SelectObj.GetSelected()[2][0]
            except IndexError:
                return None
        story = self.SapModel.FrameObj.GetLabelFromName(name)[1]
        story_frames = list(self.SapModel.FrameObj.GetNameListOnStory(story)[1])
        story_frames.remove(name)
        print('get columns pmm and beams rebars')
        columns_pmm, beams_rebars = self.get_columns_pmm_and_beams_rebars(story_frames)
        print(f"Saving file as {weakness_filename}\n")
        asli_file_path = Path(self.SapModel.GetModelFilename())
        if asli_file_path.suffix.lower() != '.edb':
            asli_file_path = asli_file_path.with_suffix(".EDB")
        dir_path = asli_file_path.parent.absolute()
        weakness_file_path = dir_path / weakness_filename
        self.SapModel.File.Save(str(weakness_file_path))
        print('multiply earthquake factor with 0.67')
        self.etabs.database.multiply_seismic_loads(.67)
        self.set_end_release_frame(name)
        print('get columns pmm and beams rebars')
        columns_pmm_weakness, beams_rebars_weakness = self.get_columns_pmm_and_beams_rebars(story_frames)
        columns_pmm_main_and_weakness, col_fields, \
            beams_rebars_main_and_weakness, beam_fields = self.combine_beams_columns_weakness_structure(
                columns_pmm,
                beams_rebars,
                columns_pmm_weakness,
                beams_rebars_weakness, 
            )
        self.SapModel.File.OpenFile(str(asli_file_path))
        return (columns_pmm_main_and_weakness, col_fields,
            beams_rebars_main_and_weakness, beam_fields)

    def set_frame_obj_selected_in_story(self, story_name):
        frames = self.SapModel.FrameObj.GetNameListOnStory(story_name)[1]
        self.set_frame_obj_selected(frames)
        return frames

    def set_frame_obj_selected(self, frame_objects):
        for fname in frame_objects:
            self.SapModel.FrameObj.SetSelected(fname, True)
        self.SapModel.View.RefreshView()

    def set_constant_j(self,
                j : float = 1,
                beam_names: list = None,
                ):
        assert j <= 1
        if beam_names is None:
            beam_names, _ = self.get_beams_columns(2)
        self.SapModel.SetModelIsLocked(False)
        for name in beam_names:
            modifiers = list(self.SapModel.FrameObj.GetModifiers(name)[0])
            modifiers[3] = j
            self.SapModel.FrameObj.SetModifiers(name, modifiers)
    
    def apply_torsion_stiffness_coefficient(self,
                beams_coeff : dict,
                ):
        self.SapModel.SetModelIsLocked(False)
        for name, ratio in beams_coeff.items():
            modifiers = list(self.SapModel.FrameObj.GetModifiers(name)[0])
            modifiers[3] = ratio
            self.SapModel.FrameObj.SetModifiers(name, modifiers)
        
    def get_t_crack(self,
                    beams_names = None,
                    phi : float = 0.75,
                    ) -> dict:
        import math
        self.etabs.run_analysis()
        self.etabs.set_current_unit('N', 'mm')
        if beams_names is None:
            beams_names, _ = self.get_beams_columns()
        beams_sections = (self.SapModel.FrameObj.GetSection(name)[0] for name in beams_names)
        beams_sections = set(beams_sections)
        sec_t = {}
        for sec_name in beams_sections:
            _, mat, h, b, *args = self.SapModel.PropFrame.GetRectangle(sec_name)
            fc = self.SapModel.PropMaterial.GetOConcrete(mat)[0]
            A = b * h
            p = 2 * (b + h)
            t_crack = phi * .33 * math.sqrt(fc) * A ** 2 / p 
            sec_t[sec_name] = t_crack / 1000000 / 9.81
        return sec_t

    def get_beams_sections(self,
            beams_names : Iterable[str] = None,
            ) -> dict:
        if beams_names is None:
            beams_names, _  = self.get_beams_columns()
        beams_sections = {name : self.SapModel.FrameObj.GetSection(name)[0] for name in beams_names}
        return beams_sections
    
    def get_beams_torsion_prop_modifiers(self,
            beams_names : Iterable[str] = None,
            ) -> dict:
        if beams_names is None:
            beams_names, _  = self.get_beams_columns()
        beams_j = {}
        for name in beams_names:
            modifiers = list(self.SapModel.FrameObj.GetModifiers(name)[0])
            beams_j[name] = modifiers[3]
        return beams_j

    def correct_torsion_stiffness_factor(self,
                load_combinations : Iterable[str] = None,
                beams_names : Iterable[str] = None,
                phi : float = 0.75,
                num_iteration : int = 5,
                tolerance : float = .1,
                j_max_value = 1.0,
                j_min_value = 0.01,
                initial_j : Union[float, None] = None,
                ):
        import numpy as np
        if beams_names is None:
            beams_names, _  = self.get_beams_columns()
        if initial_j is not None:
            self.set_constant_j(initial_j, beams_names)
        section_t_crack = self.get_t_crack(beams_names, phi=phi)
        beams_sections = self.get_beams_sections(beams_names)
        beams_j = self.get_beams_torsion_prop_modifiers(beams_names)
        df = self.etabs.database.get_beams_torsion(load_combinations, beams_names)
        df['section'] = df['UniqueName'].map(beams_sections)
        df['j'] = df['UniqueName'].map(beams_j)
        df['init_j'] = df['j']
        df['phi_Tcr'] = df['section'].map(section_t_crack)
        low = 1 - tolerance
        for i in range(num_iteration):
            df['ratio'] = df['phi_Tcr'] / df['T']
            df['ratio'].replace([np.inf, -np.inf], 1, inplace=True)
            df['ratio'].fillna(1, inplace=True)
            df['ratio'] = df['ratio'].clip(j_min_value, j_max_value)
            # df[f'Ratio_{i + 1}'] = df['ratio']
            if df['ratio'].between(low, 1.01).all():
                break
            else:
                df['ratio'] = df['ratio'] * df['j']
                df['j'] = df['ratio']
                j_dict = dict(zip(df['UniqueName'], df['j']))
                self.apply_torsion_stiffness_coefficient(j_dict)
                self.etabs.run_analysis()
                cols=['UniqueName', 'T']
                torsion_dict = self.etabs.database.get_beams_torsion(load_combinations, beams_names, cols)
                # df[f'Tu_{i + 1}'] = torsion_df['T']
                df['T'] = df['UniqueName'].map(torsion_dict)
        df.drop(columns=['ratio'], inplace=True)
        df = df[['Story', 'Beam', 'UniqueName', 'section', 'phi_Tcr', 'T', 'j', 'init_j']]
        return df



if __name__ == '__main__':
    import comtypes.client
    from pathlib import Path
    current_path = Path(__file__).parent
    import sys
    sys.path.insert(0, str(current_path))
    from etabs_obj import EtabsModel
    etabs = EtabsModel()
    SapModel = etabs.SapModel
    beams_names = ('115', '120')
    df = etabs.frame_obj.correct_torsion_stiffness_factor(tolerance=.1, num_iteration=3, initial_j=1)
    df.to_excel('c:\\alaki\\beam_torsion.xlsx')
    print('Wow')




    
        