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

def save_as(SapModel, name):
    if not name.lower().endswith('.edb'):
        name += '.EDB'
    asli_file_path = Path(SapModel.GetModelFilename())
    asli_file_path = asli_file_path.with_suffix('.EDB')
    new_file_path = asli_file_path.with_name(name)
    SapModel.File.Save(str(new_file_path))
    return asli_file_path, new_file_path

def get_etabs_file_name_without_suffix(SapModel=None):
    if not SapModel:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        SapModel = etabs.SapModel
    f = Path(SapModel.GetModelFilename())
    name = f.name.replace(f.suffix, '')
    return name

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
    SapModel.SetPresentUnits_2(5, 5, 2)
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

def save_to_json_in_edb_folder(json_name, data, SapModel=None):
    if not SapModel:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        SapModel = etabs.SapModel
    json_file = Path(SapModel.GetModelFilepath()) / json_name
    save_to_json(json_file, data)

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

def assign_diaph_to_story_points(SapModel, story_name, diaph):
    points = SapModel.PointObj.GetNameListOnStory(story_name)[1]
    for point in points:
        SapModel.PointObj.SetDiaphragm(point, 3, diaph)

def add_points_in_center_of_rigidity_and_assign_diph(SapModel):
    if SapModel.GetModelIsLocked():
        SapModel.SetModelIsLocked(False)
    story_rigidity = get_center_of_rigidity(SapModel)
    story_point_in_center_of_rigidity = {}
    for story, (x, y) in story_rigidity.items():
        z = SapModel.story.GetElevation(story)[0]
        point_name = SapModel.PointObj.AddCartesian(float(x),float(y) , z)[0]  
        diaph = get_story_diaphragm(SapModel, story)
        SapModel.PointObj.SetDiaphragm(point_name, 3, diaph)
        story_point_in_center_of_rigidity[story] = point_name
    return story_point_in_center_of_rigidity

def set_load_cases_to_analyze(SapModel, load_cases):
    all_load_case = SapModel.Analyze.GetCaseStatus()[1]
    for lc in all_load_case:
        if not lc in load_cases:
            SapModel.Analyze.SetRunCaseFlag(lc, False)
        else:
            SapModel.Analyze.SetRunCaseFlag(lc, True)

def get_xy_period(SapModel):
    modal_name = functions.get_modal_loadcase_name(SapModel)
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput(modal_name)
    ux = SapModel.Results.ModalParticipatingMassRatios()[5]
    uy = SapModel.Results.ModalParticipatingMassRatios()[6]
    x_index = ux.index(max(ux))
    y_index = uy.index(max(uy))
    periods = SapModel.Results.ModalParticipatingMassRatios()[4]
    Tx = periods[x_index]
    Ty = periods[y_index]
    return Tx, Ty, x_index + 1, y_index + 1

def get_xy_frequency(SapModel):
    Tx, Ty, i_x, i_y = get_xy_period(SapModel)
    from math import pi
    return (2 * pi / Tx, 2 * pi / Ty, i_x, i_y)

def get_stories_displacement_in_xy_modes(SapModel):
    f1, _ = save_as(SapModel, 'modal_stiffness.EDB')
    story_point = add_points_in_center_of_rigidity_and_assign_diph(SapModel)
    modal = functions.get_modal_loadcase_name(SapModel)
    set_load_cases_to_analyze(SapModel, modal)
    SapModel.Analyze.RunAnalysis()
    wx, wy, ix, iy = get_xy_frequency(SapModel)
    TableKey = 'Joint Displacements'
    [_, _, FieldsKeysIncluded, _, TableData, _] = functions.read_table(TableKey, SapModel)
    data = functions.reshape_data(FieldsKeysIncluded, TableData)
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
        result = get_from_list_table(data, columns, values)
        result = list(result)
        assert len(result) == 1
        ux = float(result[0][i_ux])
        x_results[story] = ux
    y_results = {}
    for story, point in story_point.items():
        values = (story, point, modal, 'Mode', str(iy))
        result = get_from_list_table(data, columns, values)
        result = list(result)
        assert len(result) == 1
        uy = float(result[0][i_uy])
        y_results[story] = uy
    SapModel.File.OpenFile(str(f1))
    return x_results, y_results, wx, wy
    
def add_load_case_in_center_of_rigidity(SapModel, story_name, x, y):
    SapModel.SetPresentUnits(7)
    z = SapModel.story.GetElevation(story_name)[0]
    point_name = SapModel.PointObj.AddCartesian(float(x),float(y) , z)[0]  
    diaph = get_story_diaphragm(SapModel, story_name)
    SapModel.PointObj.SetDiaphragm(point_name, 3, diaph)
    LTYPE_OTHER = 8
    lp_name = f'STIFFNESS_{story_name}'
    SapModel.LoadPatterns.Add(lp_name, LTYPE_OTHER, 0, True)
    load = 1000
    PointLoadValue = [load,load,0,0,0,0]
    SapModel.PointObj.SetLoadForce(point_name, lp_name, PointLoadValue)
    set_load_cases_to_analyze(SapModel, lp_name)
    return point_name, lp_name

def get_point_xy_displacement(SapModel, point_name, lp_name):
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput(lp_name)
    results = SapModel.Results.JointDispl(point_name, 0)
    x = results[6][0]
    y = results[7][0]
    return x, y

def set_point_restraint(SapModel,
        point_names,
        restraint: list= [True, True, False, False, False, False]):
    for point_name in point_names:
        SapModel.PointObj.SetRestraint(point_name, restraint)

def fix_below_stories(SapModel, story_name):
    stories_name = SapModel.Story.GetNameList()[1]
    story_level = SapModel.Story.GetElevation(story_name)[0]
    for name in stories_name:
        level = SapModel.Story.GetElevation(name)[0]
        if level < story_level:
            points = SapModel.PointObj.GetNameListOnStory(name)[1]
            set_point_restraint(SapModel, points)

def get_story_stiffness_modal_way(SapModel):
    story_mass = get_story_mass(SapModel)[::-1]
    story_mass = {key: value for key, value in story_mass}
    stories = list(story_mass.keys())
    dx, dy, wx, wy = get_stories_displacement_in_xy_modes(SapModel)
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

def get_story_stiffness_2800_way(SapModel):
    asli_file_path = Path(SapModel.GetModelFilename())
    if asli_file_path.suffix.lower() != '.edb':
        asli_file_path = asli_file_path.with_suffix(".EDB")
    dir_path = asli_file_path.parent.absolute()
    story_names = SapModel.Story.GetNameList()[1]
    center_of_rigidity = get_center_of_rigidity(SapModel)
    story_stiffness = {}
    import shutil
    for story_name in story_names:
        story_file_path = dir_path / f'STIFFNESS_{story_name}.EDB'
        print(f"Saving file as {story_file_path}\n")
        shutil.copy(asli_file_path, story_file_path)
        print(f"Opening file {story_file_path}\n")
        SapModel.File.OpenFile(str(story_file_path))
        x, y = center_of_rigidity[story_name]
        point_name, lp_name = add_load_case_in_center_of_rigidity(SapModel,
                story_name, x, y)
        fix_below_stories(SapModel, story_name)
        SapModel.View.RefreshView()
        SapModel.Analyze.RunAnalysis()
        disp_x, disp_y = get_point_xy_displacement(SapModel, point_name, lp_name)
        kx, ky = 1000 / abs(disp_x), 1000 / abs(disp_y)
        story_stiffness[story_name] = [kx, ky]
    SapModel.File.OpenFile(str(asli_file_path))
    return story_stiffness

def get_story_stiffness_earthquake_way(
                SapModel=None,
                loadcases: list=None,
                ):
    if not SapModel:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        SapModel = etabs.SapModel
    if not loadcases:
        loadcases = functions.get_EX_EY_load_pattern(SapModel)
    assert len(loadcases) == 2
    EX, EY = loadcases
    if not SapModel.GetModelIsLocked():
        return None
    SapModel.SetPresentUnits(units["kgf_m_C"])
    functions.select_load_cases(SapModel, loadcases)
    TableKey = 'Story Stiffness'
    [_, _, FieldsKeysIncluded, _, TableData, _] = functions.read_table(TableKey, SapModel)
    i_story = FieldsKeysIncluded.index('Story')
    i_case = FieldsKeysIncluded.index('OutputCase')
    i_stiff_x = FieldsKeysIncluded.index('StiffX')
    i_stiff_y = FieldsKeysIncluded.index('StiffY')
    data = functions.reshape_data(FieldsKeysIncluded, TableData)
    columns = (i_case,)
    values_x = (EX,)
    values_y = (EY,)
    result_x = get_from_list_table(data, columns, values_x)
    result_y = get_from_list_table(data, columns, values_y)
    story_stiffness = {}
    for x, y in zip(list(result_x), list(result_y)):
        story = x[i_story]
        stiff_x = float(x[i_stiff_x])
        stiff_y = float(y[i_stiff_y])
        story_stiffness[story] = [stiff_x, stiff_y]
    return story_stiffness

def get_story_stiffness_table(way='2800',SapModel=None, story_stiffness=None):
    '''
    way can be '2800', 'modal' , 'earthquake'
    '''
    if not SapModel:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        SapModel = etabs.SapModel
    name = get_etabs_file_name_without_suffix(SapModel)
    if not story_stiffness:
        if way == '2800':
            story_stiffness = get_story_stiffness_2800_way(SapModel)
        elif way == 'modal':
            story_stiffness = get_story_stiffness_modal_way(SapModel)
        elif way == 'earthquake':
            story_stiffness = get_story_stiffness_earthquake_way(SapModel)
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
            # k1 = story_stiffness[stories[i - 1]]
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
    save_to_json_in_edb_folder(json_file, (retval, fields), SapModel)
    return retval, fields



if __name__ == '__main__':
    etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    ss = get_beams_columns_weakness_structure(SapModel)
    print(ss)
    print('')
    