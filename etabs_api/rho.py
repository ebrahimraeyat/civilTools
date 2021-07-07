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

def get_columns_pmm(SapModel):
    _, columns = functions.get_beams_columns(SapModel)
    columns_pmm = dict()
    for col in columns:
        pmm = max(SapModel.DesignConcrete.GetSummaryResultsColumn(col)[6])
        columns_pmm[col] = [pmm]
    return columns_pmm

def get_beams_rebars(SapModel):
    SapModel.SetPresentUnits(units["kgf_cm_C"])
    beams, _ = functions.get_beams_columns(SapModel)
    beams_rebars = dict()
    for name in beams:
        d = dict()
        beam_rebars = SapModel.DesignConcrete.GetSummaryResultsBeam(name)
        d['location'] = beam_rebars[2]
        d['TopArea'] = beam_rebars[4]
        d['BotArea'] = beam_rebars[6]
        d['VRebar'] = beam_rebars[8]
        beams_rebars[name] = d
    return beams_rebars

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

if __name__ == '__main__':
    etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    get_story_forces(SapModel)
    print('')
    