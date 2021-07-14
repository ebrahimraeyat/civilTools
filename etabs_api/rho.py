from os import spawnl
import sys
import comtypes.client
from pathlib import Path

civiltools_path = Path(__file__).parent.parent
sys.path.insert(0, str(civiltools_path))
from etabs_api import functions

units = {
    "kN_mm_C" : 4,
    "kN_m_C" : 5,
    "kgf_mm_C" : 6,
    "kgf_m_C" : 7,
    "N_mm_C" : 8,
    "N_m_C" : 9,
    "Ton_mm_C" : 10,
    "Ton_m_C" : 11,
    "kN_cm_C" : 12,
    "kgf_cm_C" : 13,
    "N_cm_C" : 14,
    "Ton_cm_C" : 15,
}

def get_ex_ey_earthquake_name(SapModel):
    x_names, y_names = functions.get_load_patterns_in_XYdirection(SapModel)
    x_names = sorted(x_names)
    y_names = sorted(y_names)
    drift_load_patterns = functions.get_drift_load_pattern_names(SapModel)
    for name in x_names:
        if name not in drift_load_patterns:
            x_name = name
            break
    for name in y_names:
        if name not in drift_load_patterns:
            y_name = name
            break
    return x_name, y_name

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


def get_story_forces(
                SapModel=None,
                loadcases: list=None,
                ):
    if not SapModel:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        SapModel = etabs.SapModel
    if not SapModel.GetModelIsLocked():
        return None
    if not loadcases:
        loadcases = get_ex_ey_earthquake_name(SapModel)
    assert len(loadcases) == 2
    SapModel.SetPresentUnits(units["kgf_m_C"])
    functions.select_load_cases(SapModel, loadcases)
    TableKey = 'Story Forces'
    [_, _, FieldsKeysIncluded, _, TableData, _] = functions.read_table(TableKey, SapModel)
    i_loc = FieldsKeysIncluded.index('Location')
    data = functions.reshape_data(FieldsKeysIncluded, TableData)
    columns = (i_loc,)
    values = ('Bottom',)
    result = get_from_list_table(data, columns, values)
    story_forces = list(result)
    return story_forces, loadcases, FieldsKeysIncluded

def get_story_forces_with_percentages(
            SapModel=None,
            loadcases: list=None,
            ):
    vx, vy = get_base_react(SapModel)
    story_forces, _ , fields = get_story_forces(SapModel, loadcases)
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

def get_base_react(SapModel=None):
    if not SapModel:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        SapModel = etabs.SapModel
    SapModel.SetPresentUnits(units["kgf_m_C"])
    loadcases = get_ex_ey_earthquake_name(SapModel)
    SapModel.Results.Setup.SetCaseSelectedForOutput(loadcases[0])
    SapModel.Results.Setup.SetCaseSelectedForOutput(loadcases[1])
    base_react = SapModel.Results.BaseReact()
    vx = base_react[4][0]
    vy = base_react[5][1]
    return vx, vy

def get_columns_pmm(SapModel, frame_names=None):
    if not SapModel.GetModelIsLocked():
        print('Run Alalysis ...')
        SapModel.Analyze.RunAnalysis()
    if frame_names:
        for fname in frame_names:
            SapModel.FrmeObj.SetSelected(fname, True)
    if not SapModel.DesignConcrete.GetResultsAvailable():
        print('Start Design ...')
        SapModel.DesignConcrete.StartDesign()
    _, columns = functions.get_beams_columns(SapModel)
    columns_pmm = dict()
    for col in columns:
        if frame_names and not col in frame_names:
            continue
        pmm = max(SapModel.DesignConcrete.GetSummaryResultsColumn(col)[6])
        columns_pmm[col] = round(pmm, 3)
    return columns_pmm

def get_beams_rebars(SapModel, frame_names=None):
    SapModel.SetPresentUnits(units["kgf_cm_C"])
    if not SapModel.GetModelIsLocked():
        print('Run Alalysis ...')
        SapModel.Analyze.RunAnalysis()
    if frame_names:
        for fname in frame_names:
            SapModel.FrmeObj.SetSelected(fname, True)
    if not SapModel.DesignConcrete.GetResultsAvailable():
        print('Start Design ...')
        SapModel.DesignConcrete.StartDesign()
    beams, _ = functions.get_beams_columns(SapModel)
    beams_rebars = []
    for name in beams:
        if frame_names and not name in frame_names:
            continue
        beam_rebars = SapModel.DesignConcrete.GetSummaryResultsBeam(name)
        label, story, _ = SapModel.FrameObj.GetLabelFromName(name)
        locations = beam_rebars[2]
        top_area = beam_rebars[4]
        bot_area = beam_rebars[6]
        vrebar = beam_rebars[8]
        for l, ta, ba, v in zip(locations, top_area, bot_area, vrebar):
            beams_rebars.append((
                story,
                label,
                l, ta, ba, v,
                ))
    return beams_rebars

def get_columns_pmm_and_beams_rebars(SapModel, frame_names):
    if not SapModel.GetModelIsLocked():
        print('Run Alalysis ...')
        SapModel.Analyze.RunAnalysis()
    set_frame_obj_selected(SapModel, frame_names)
    if not SapModel.DesignConcrete.GetResultsAvailable():
        print('Start Design ...')
        SapModel.DesignConcrete.StartDesign()
    SapModel.SetPresentUnits(units["kgf_cm_C"])
    beams, columns = functions.get_beams_columns(SapModel)
    beams = set(frame_names).intersection(beams)
    columns = set(frame_names).intersection(columns)
    columns_pmm = dict()
    for col in columns:
        pmm = max(SapModel.DesignConcrete.GetSummaryResultsColumn(col)[6])
        columns_pmm[col] = round(pmm, 3)
    beams_rebars = dict()
    for name in beams:
        d = dict()
        beam_rebars = SapModel.DesignConcrete.GetSummaryResultsBeam(name)
        d['location'] = beam_rebars[2]
        d['TopArea'] = beam_rebars[4]
        d['BotArea'] = beam_rebars[6]
        d['VRebar'] = beam_rebars[8]
        beams_rebars[name] = d
    return columns_pmm, beams_rebars

def multiply_seismic_loads(
        SapModel,
        x: float,
        y=None,
        ):
    if not y:
        y = x
    SapModel.SetModelIsLocked(False)
    functions.select_all_load_patterns(SapModel)
    TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
    [_, _, FieldsKeysIncluded, _, TableData, _] = functions.read_table(TableKey, SapModel)
    data = functions.reshape_data(FieldsKeysIncluded, TableData)
    names_x, names_y = functions.get_load_patterns_in_XYdirection(SapModel)
    i_c = FieldsKeysIncluded.index('C')
    i_name = FieldsKeysIncluded.index("Name")
    for earthquake in data:
        name = earthquake[i_name]
        c = float(earthquake[i_c])
        cx = x * c
        cy = y * c
        if name in names_x:
            earthquake[i_c] = str(cx)
        elif name in names_y:
            earthquake[i_c] = str(cy)
    TableData = functions.unique_data(data)
    FieldsKeysIncluded1 = ['Name', 'Is Auto Load', 'X Dir?', 'X Dir Plus Ecc?', 'X Dir Minus Ecc?',
                           'Y Dir?', 'Y Dir Plus Ecc?', 'Y Dir Minus Ecc?',
                           'Ecc Ratio', 'Top Story', 'Bot Story',
                           'C',
                           'K']
    SapModel.DatabaseTables.SetTableForEditingArray(TableKey, 0, FieldsKeysIncluded1, 0, TableData)
    NumFatalErrors, ret = functions.apply_table(SapModel)
    return NumFatalErrors, ret

def set_end_release_frame(SapModel, name):
    end_release = SapModel.FrameObj.GetReleases(name)
    II = list(end_release[0])
    JJ = list(end_release[1])
    II[3:] = [True] * len(II[3:])
    JJ[4:] = [True] * len(II[4:])
    end_release[0] = tuple(II)
    end_release[1] = tuple(JJ)
    end_release.insert(0, name)
    er = SapModel.FrameObj.SetReleases(*end_release)
    return er

def get_columns_pmm_weakness_structure(
                SapModel,
                name: str = '',
                weakness_filename="weakness.EDB"
                ):
    if not name:
        name = SapModel.SelectObj.GetSelected()[2][0]
    asli_file_path = Path(SapModel.GetModelFilename())
    if asli_file_path.suffix.lower() != '.edb':
        asli_file_path = asli_file_path.with_suffix(".EDB")
    dir_path = asli_file_path.parent.absolute()
    weakness_file_path = dir_path / weakness_filename
    print('get columns pmm')
    columns_pmm = get_columns_pmm(SapModel)
    print(f"Saving file as {weakness_filename}\n")
    SapModel.File.Save(str(weakness_file_path))
    print('multiply earthquake factor with 0.67')
    multiply_seismic_loads(SapModel, .67)
    set_end_release_frame(SapModel, name)
    print('get columns pmm')
    columns_pmm_weakness = get_columns_pmm(SapModel)
    columns_pmm_main_and_weakness = []
    for key, value in columns_pmm.items():
        value2 = columns_pmm_weakness[key]
        columns_pmm_main_and_weakness.append((key, value, value2))
    SapModel.File.OpenFile(str(asli_file_path))
    return columns_pmm_main_and_weakness

def get_beams_rebars_weakness_structure(
                SapModel,
                name: str = '',
                weakness_filename="weakness.EDB"
                ):
    if not name:
        try:
            name = SapModel.SelectObj.GetSelected()[2][0]
        except IndexError:
            return None
    asli_file_path = Path(SapModel.GetModelFilename())
    if asli_file_path.suffix.lower() != '.edb':
        asli_file_path = asli_file_path.with_suffix(".EDB")
    dir_path = asli_file_path.parent.absolute()
    weakness_file_path = dir_path / weakness_filename
    print('get beams rebars')
    beams_rebars = get_beams_rebars(SapModel)
    print(f"Saving file as {weakness_filename}\n")
    SapModel.File.Save(str(weakness_file_path))
    print('multiply earthquake factor with 0.67')
    multiply_seismic_loads(SapModel, .67)
    set_end_release_frame(SapModel, name)
    print('get beams rebars')
    beams_rebars_weakness = get_beams_rebars(SapModel)
    beams_rebars_main_and_weakness = []
    for key, d in beams_rebars.items():
        d2 = beams_rebars_weakness[key]
        beams_rebars_main_and_weakness.append((
            key,
            d['location'],
            d['TopArea'],
            d2['TopArea'],
            d['BotArea'],
            d2['BotArea'],
            d['VRebar'],
            d2['VRebar'],
            ))
    SapModel.File.OpenFile(str(asli_file_path))
    return beams_rebars_main_and_weakness

def combine_beams_columns_weakness_structure(
            SapModel,
            columns_pmm,
            beams_rebars,
            columns_pmm_weakness,
            beams_rebars_weakness,
            ):
    columns_pmm_main_and_weakness = []
    for key, value in columns_pmm.items():
        value2 = columns_pmm_weakness[key]
        label, story, _ = SapModel.FrameObj.GetLabelFromName(key)
        ratio = round(value2/value, 3)
        columns_pmm_main_and_weakness.append((story, label, value, value2, ratio))
    col_fields = ('Story', 'Label', 'PMM Ratio1', 'PMM ratio2', 'Ratio')
    beams_rebars_main_and_weakness = []
    for key, d in beams_rebars.items():
        d2 = beams_rebars_weakness[key]
        label, story, _ = SapModel.FrameObj.GetLabelFromName(key)
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
    beam_fields = ('Story', 'Label', 'location',
            'Top Area1', 'Top Area2',
            'Bot Area1', 'Bot Area2',
            'VRebar1', 'VRebar2')
    json_file = Path(SapModel.GetModelFilepath()) / 'columns_pmm_beams_rebars.json'
    save_to_json(json_file, (columns_pmm_main_and_weakness, col_fields,
           beams_rebars_main_and_weakness, beam_fields))

    return (columns_pmm_main_and_weakness, col_fields,
           beams_rebars_main_and_weakness, beam_fields)

def get_beams_columns_weakness_structure(
                SapModel=None,
                name: str = '',
                weakness_filename="weakness.EDB"
                ):
    if not SapModel:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        SapModel = etabs.SapModel
    if not name:
        try:
            name = SapModel.SelectObj.GetSelected()[2][0]
        except IndexError:
            return None
    story = SapModel.FrameObj.GetLabelFromName(name)[1]
    story_frames = list(SapModel.FrameObj.GetNameListOnStory(story)[1])
    story_frames.remove(name)
    print('get columns pmm and beams rebars')
    columns_pmm, beams_rebars = get_columns_pmm_and_beams_rebars(SapModel, story_frames)
    print(f"Saving file as {weakness_filename}\n")
    asli_file_path = Path(SapModel.GetModelFilename())
    if asli_file_path.suffix.lower() != '.edb':
        asli_file_path = asli_file_path.with_suffix(".EDB")
    dir_path = asli_file_path.parent.absolute()
    weakness_file_path = dir_path / weakness_filename
    SapModel.File.Save(str(weakness_file_path))
    print('multiply earthquake factor with 0.67')
    multiply_seismic_loads(SapModel, .67)
    set_end_release_frame(SapModel, name)
    print('get columns pmm and beams rebars')
    columns_pmm_weakness, beams_rebars_weakness = get_columns_pmm_and_beams_rebars(SapModel, story_frames)
    columns_pmm_main_and_weakness, col_fields, \
        beams_rebars_main_and_weakness, beam_fields = combine_beams_columns_weakness_structure(
            SapModel,
            columns_pmm,
            beams_rebars,
            columns_pmm_weakness,
            beams_rebars_weakness, 
        )
    SapModel.File.OpenFile(str(asli_file_path))
    return (columns_pmm_main_and_weakness, col_fields,
        beams_rebars_main_and_weakness, beam_fields)
    
def set_frame_obj_selected_in_story(SapModel, story_name):
    frames = SapModel.FrameObj.GetNameListOnStory(story_name)[1]
    set_frame_obj_selected(frames)
    return frames

def set_frame_obj_selected(SapModel, frame_objects):
    for fname in frame_objects:
        SapModel.FrameObj.SetSelected(fname, True)
    SapModel.View.RefreshView()

def save_to_json(json_file, data):
    import json
    with open(json_file, 'w') as f:
        json.dump(data, f)

def load_from_json(json_file):
    import json
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def get_story_mass(SapModel):
    SapModel.SetPresentUnits(units["kgf_m_C"])
    TableKey = 'Centers Of Mass And Rigidity'
    [_, _, FieldsKeysIncluded, _, TableData, _] = functions.read_table(TableKey, SapModel)
    data = functions.reshape_data(FieldsKeysIncluded, TableData)
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

def get_irregularity_of_mass(SapModel=None, story_mass=None):
    if not SapModel:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        SapModel = etabs.SapModel
    if not story_mass:
        story_mass = get_story_mass(SapModel)
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

def get_center_of_rigidity(SapModel):
    SapModel.SetPresentUnits(units["kgf_m_C"])
    TableKey = 'Centers Of Mass And Rigidity'
    [_, _, FieldsKeysIncluded, _, TableData, _] = functions.read_table(TableKey, SapModel)
    data = functions.reshape_data(FieldsKeysIncluded, TableData)
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


def get_story_diaphragm(SapModel, story_name):
    '''
    Try to get Story diaphragm with point or area
    '''
    areas = SapModel.AreaObj.GetNameListOnStory(story_name)[1]
    for area in areas:
        diaph = SapModel.AreaObj.GetDiaphragm(area)[0]
        if diaph != 'None':
            return diaph
    points = SapModel.PointObj.GetNameListOnStory(story_name)[1]
    for point in points:
        diaph = SapModel.PointObj.GetDiaphragm(point)[1]
        if diaph:
            return diaph

def disconnect_story_diaphragm(SapModel, story_name):
    areas = SapModel.AreaObj.GetNameListOnStory(story_name)[1]
    for area in areas:
        SapModel.AreaObj.SetDiaphragm(area, 'None')
    points = SapModel.PointObj.GetNameListOnStory(story_name)[1]
    for point in points:
        SapModel.PointObj.SetDiaphragm(point, 1)



if __name__ == '__main__':
    etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    get_story_diaphragm(SapModel, "Story3")
    print('')
    