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
    result = filter(lambda x: itemget(x) == values, list_table)
    return result


def get_story_forces(SapModel, loadcase, direction='X'):
    if not SapModel.GetModelIsLocked():
        return None
    SapModel.SetPresentUnits(units["kgf_m_C"])
    SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay('')
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay([loadcase])
    TableKey = 'Story Forces'
    [_, _, FieldsKeysIncluded, _, TableData, _] = functions.read_table(TableKey, SapModel)
    i_story = FieldsKeysIncluded.index('Story')
    i_loc = FieldsKeysIncluded.index('Location')
    i_case = FieldsKeysIncluded.index('OutputCase')
    data = functions.reshape_data(FieldsKeysIncluded, TableData)
    columns = (i_case, i_loc)
    values = (loadcase, 'Bottom')
    result = get_from_list_table(data, columns, values)
    if direction == 'X':
        i_v = FieldsKeysIncluded.index('VX')
    else:
        i_v = FieldsKeysIncluded.index('VY')
    story_forces = [(row[i_story], abs(float(row[i_v]))) for row in result]
    return story_forces

# def get_stories_with_shear_greater_than_35_base_shear(SapModel):
#     for row in data:

if __name__ == '__main__':
    etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    print('')
    