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
                SapModel,
                loadcases: list=None,
                ):
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
    return story_forces, loadcases

def get_stories_with_shear_greater_than_35_base_shear(SapModel, loadcase, direction='X'):
    story_forces = get_story_forces(SapModel, loadcase, direction)
    max_force = max(list(story_forces.values()))
    stories = []
    for key, value in story_forces.items():
        if value / max_force > .35:
            stories.append(key)
    return stories 

if __name__ == '__main__':
    etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    get_story_forces(SapModel)
    print('')
    