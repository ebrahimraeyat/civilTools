from os.path import sameopenfile
import comtypes.client
from pathlib import Path

civiltools_path = Path(__file__).parent.parent


def reshape_data(FieldsKeysIncluded, table_data):
    n = len(FieldsKeysIncluded)
    data = [list(table_data[i:i+n]) for i in range(0, len(table_data), n)]
    return data

def unique_data(data):
    table_data = []
    for i in data:
        table_data += i
    return table_data

def apply_table(SapModel):
    FillImportLog = True
    NumFatalErrors = 0
    NumErrorMsgs = 0
    NumWarnMsgs = 0
    NumInfoMsgs = 0
    ImportLog = ''
    [NumFatalErrors, NumErrorMsgs, NumWarnMsgs, NumInfoMsgs, ImportLog,
        ret] = SapModel.DatabaseTables.ApplyEditedTables(FillImportLog, NumFatalErrors,
                                                        NumErrorMsgs, NumWarnMsgs, NumInfoMsgs, ImportLog)
    return NumFatalErrors

def read_table(table_key, SapModel):
    GroupName = table_key
    FieldKeyList = []
    TableVersion = 0
    FieldsKeysIncluded = []
    NumberRecords = 0
    TableData = []
    return SapModel.DatabaseTables.GetTableForDisplayArray(table_key, FieldKeyList, GroupName, TableVersion, FieldsKeysIncluded, NumberRecords, TableData)

def close_etabs(ETABSObject):
    SapModel = ETABSObject.SapModel
    SapModel.SetModelIsLocked(False)
    ETABSObject.ApplicationExit(False)
    SapModel = None
    ETABSObject = None

def get_load_patterns(SapModel):
    return SapModel.LoadPatterns.GetNameList(0, [])[1]

def get_special_load_pattern_names(SapModel, n=5):
    '''
    Each load patterns has a special number ID, for example:
    DEAD is 1, SEISMIC is 5
    '''
    lps = get_load_patterns(SapModel)
    names = []
    for lp in lps:
        if SapModel.LoadPatterns.GetLoadType(lp)[0] == n:
            names.append(lp)
    return names
    
def get_drift_load_pattern_names(SapModel):
    '''
    Drift loadType number is 37, when user tick the eccentricity of load,
    etabs create aditional (1/3), (2/3) and (3/3) load when structure is analyzed
    '''
    return get_special_load_pattern_names(SapModel, 37)

def get_load_patterns_in_XYdirection(SapModel):
    '''
    return list of load pattern names, x and y direction separately
    '''
    select_all_load_patterns(SapModel)
    TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
    [_, _, FieldsKeysIncluded, _, TableData, _] = read_table(TableKey, SapModel)
    i_xdir = FieldsKeysIncluded.index('XDir')
    i_xdir_plus = FieldsKeysIncluded.index('XDirPlusE')
    i_xdir_minus = FieldsKeysIncluded.index('XDirMinusE')
    i_ydir = FieldsKeysIncluded.index('YDir')
    i_ydir_plus = FieldsKeysIncluded.index('YDirPlusE')
    i_ydir_minus = FieldsKeysIncluded.index('YDirMinusE')
    i_name = FieldsKeysIncluded.index('Name')
    data = reshape_data(FieldsKeysIncluded, TableData)
    names_x = set()
    names_y = set()
    for earthquake in data:
        name = earthquake[i_name]
        if any((
            earthquake[i_xdir] == 'Yes',
            earthquake[i_xdir_minus] == 'Yes',
            earthquake[i_xdir_plus] == 'Yes',
        )):
            names_x.add(name)
        elif any((
            earthquake[i_ydir] == 'Yes',
            earthquake[i_ydir_minus] == 'Yes',
            earthquake[i_ydir_plus] == 'Yes',
        )):
            names_y.add(name)
        
    return names_x, names_y

def select_all_load_patterns(SapModel):
    load_pattern_names = list(get_load_patterns(SapModel))
    if not SapModel.GetModelIsLocked():
        names = tuple(load_pattern_names)
        for name in names:
            if all((
                '(' in name,
                '/' in name,
                ')' in name,
            )):
                load_pattern_names.remove(name)
    SapModel.DatabaseTables.SetLoadPatternsSelectedForDisplay(load_pattern_names)

def get_load_cases(SapModel):
    load_case_names = SapModel.LoadCases.GetNameList(0, [])[1]
    return load_case_names

def select_all_load_cases(SapModel):
    load_case_names = get_load_cases(SapModel)
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(load_case_names)

def select_load_cases(SapModel, names):
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(names)
    

def get_beams_columns(
        etabs=None,
        type_=2,
        ):
    '''
    type_: 1=steel and 2=concrete
    '''
    if not etabs:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    beams = []
    columns = []
    others = []
    for label in SapModel.FrameObj.GetLabelNameList()[1]:
        if SapModel.FrameObj.GetDesignProcedure(label)[0] == type_: 
            if SapModel.FrameObj.GetDesignOrientation(label)[0] == 1:
                columns.append(label)
            elif SapModel.FrameObj.GetDesignOrientation(label)[0] == 2:
                beams.append(label)
            else:
                others.append(label)
    return beams, columns

def get_drift_periods(
            etabs=None,
            t_filename="T.EDB",
            ):
    '''
    This function creates an Etabs file called T.EDB from current open Etabs file,
    then in T.EDB file change the stiffness properties of frame elements according 
    to ACI 318 to get periods of structure, for this it set M22 and M33 stiffness of
    beams to 0.5 and column and wall to 1.0. Then it runs the analysis and get the x and y period of structure.
    '''
    print(10 * '-' + "Get drift periods" + 10 * '-' + '\n')
    if not etabs:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    asli_file_path = Path(SapModel.GetModelFilename())
    if asli_file_path.suffix.lower() != '.edb':
        asli_file_path = asli_file_path.with_suffix(".EDB")
    dir_path = asli_file_path.parent.absolute()
    t_file_path = dir_path / t_filename
    print(f"Saving file as {t_file_path}\n")
    SapModel.File.Save(str(t_file_path))
    print("Get beams and columns\n")
    beams, columns = get_beams_columns(etabs)
    print("get frame property modifiers and change I values\n")
    TableKey = "Frame Assignments - Property Modifiers"
    [_, TableVersion, FieldsKeysIncluded, NumberRecords, TableData, _] = read_table(TableKey, SapModel)
    data = reshape_data(FieldsKeysIncluded, TableData)
    i_name = FieldsKeysIncluded.index("UniqueName")
    i_I2Mod = FieldsKeysIncluded.index("I2Mod")
    i_I3Mod = FieldsKeysIncluded.index("I3Mod")
    IMod_beam = "0.5"
    IMod_col_wall = "1"
    for frame_assign in data:
        name = frame_assign[i_name]
        if name in beams:
            IMod = IMod_beam
        elif name in columns:
            IMod = IMod_col_wall
        frame_assign[i_I2Mod] = IMod
        frame_assign[i_I3Mod] = IMod

    TableData1 = unique_data(data)
    FieldsKeysIncluded = ('Story', 'Label', 'UniqueName', 'Area Modifier', 'As2 Modifier', 'As3 Modifier', 'J Modifier', 'I22 Modifier', 'I33 Modifier', 'Mass Modifier', 'Weight Modifier')
    SapModel.DatabaseTables.SetTableForEditingArray(TableKey, TableVersion, FieldsKeysIncluded, NumberRecords, TableData1)
    print("apply table\n")
    log = apply_table(SapModel)
    print(f"number errors = {log}")
    # print(log)

    # run model (this will create the analysis model)
    print("start running T file analysis")
    SapModel.Analyze.RunAnalysis()

    TableKey = "Modal Participating Mass Ratios"
    [_, TableVersion, FieldsKeysIncluded, NumberRecords, TableData, _] = read_table(TableKey, SapModel)
    SapModel.SetModelIsLocked(False)

    data = reshape_data(FieldsKeysIncluded, TableData)
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
    SapModel.File.OpenFile(str(asli_file_path))
    return Tx_drift, Ty_drift, asli_file_path

def get_drifts(no_story, cdx, cdy, show_table=False, etabs=None):
    if not etabs:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    if not SapModel.GetModelIsLocked():
        return 'not analyzed', None
    # SapModel.SetModelIsLocked(False)
    # ret = SapModel.Analyze.RunAnalysis()
    # if ret != 0:
    #     raise RuntimeError
    drift_load_pattern_names = get_drift_load_pattern_names(SapModel)
    all_load_case_names = get_load_cases(SapModel)
    names = [i for i in drift_load_pattern_names if i in all_load_case_names]
    print(names)
    select_load_cases(SapModel, names)
    TableKey = 'Diaphragm Max Over Avg Drifts'
    [_, _, FieldsKeysIncluded, _, TableData, _] = read_table(TableKey, SapModel)
    data = reshape_data(FieldsKeysIncluded, TableData)
    try:
        item_index = FieldsKeysIncluded.index("Item")
    except ValueError:
        return None, None
    # average_drift_index = FieldsKeysIncluded.index("Avg Drift")
    if no_story <= 5:
        limit = .025
    else:
        limit = .02
    for row in data:
        if row[item_index].endswith("X"):
            cd = cdx
        elif row[item_index].endswith("Y"):
            cd = cdy
        allowable_drift = limit / cd
        row.append(f'{allowable_drift:.4f}')
    if show_table:
        pass
    fields = list(FieldsKeysIncluded)
    fields.append('Allowable Drift')
    return data, fields

def apply_cfactor_to_tabledata(TableData, FieldsKeysIncluded, building, SapModel):
    data = reshape_data(FieldsKeysIncluded, TableData)
    names_x, names_y = get_load_patterns_in_XYdirection(SapModel)
    i_c = FieldsKeysIncluded.index('C')
    i_k = FieldsKeysIncluded.index('K')
    cx, cy = str(building.results[1]), str(building.results[2])
    kx, ky = str(building.kx), str(building.ky)
    cx_drift, cy_drift = str(building.results_drift[1]), str(building.results_drift[2])
    kx_drift, ky_drift = str(building.kx_drift), str(building.ky_drift)
    drift_load_pattern_names = get_drift_load_pattern_names(SapModel)
    i_name = FieldsKeysIncluded.index("Name")
    for earthquake in data:
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
    table_data = unique_data(data)
    return table_data

def apply_cfactor_to_edb(
        building,
        ):
    print("Applying cfactor to edb\n")
    myETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = myETABSObject.SapModel
    SapModel.SetModelIsLocked(False)
    select_all_load_patterns(SapModel)
    TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
    [_, TableVersion, FieldsKeysIncluded, NumberRecords, TableData, _] = read_table(TableKey, SapModel)
    TableData = apply_cfactor_to_tabledata(TableData, FieldsKeysIncluded, building, SapModel)
    SapModel.DatabaseTables.SetTableForEditingArray(TableKey, TableVersion, FieldsKeysIncluded, NumberRecords, TableData)
    NumFatalErrors = apply_table(SapModel)
    print(f"NumFatalErrors = {NumFatalErrors}")
    SapModel.File.Save()
    return NumFatalErrors

def apply_cfactor_to_edb_and_analyze(building):
    apply_cfactor_to_edb(building)
    myETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = myETABSObject.SapModel
    ret = SapModel.Analyze.RunAnalysis()
    return ret

def get_drift_periods_calculate_cfactor_and_apply_to_edb(
        widget,
        etabs=None,
        ):
    if not etabs:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    Tx, Ty, _ = get_drift_periods(etabs)
    widget.xTAnalaticalSpinBox.setValue(Tx)
    widget.yTAnalaticalSpinBox.setValue(Ty)
    widget.calculate()
    num_errors = apply_cfactor_to_edb(widget.final_building)
    return num_errors, etabs

def calculate_drifts(
            widget,
            no_story=None,
            etabs=None):
    _, etabs = get_drift_periods_calculate_cfactor_and_apply_to_edb(widget, etabs)
    if not no_story:
        no_story = widget.storySpinBox.value()
    cdx = widget.final_building.x_system.cd
    cdy = widget.final_building.y_system.cd
    drifts, _ = get_drifts(no_story, cdx, cdy, True, etabs)
    return drifts

def is_etabs_running():
    try:
        comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
        return True
    except OSError:
        return False

class Build:
    def __init__(self):
        self.kx = 1
        self.ky = 1
        self.kx_drift = 1
        self.ky_drift = 1
        self.results = [True, 1, 1]
        self.results_drift = [True, 1, 1]
            
if __name__ == '__main__':
    # etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    # SapModel = etabs.SapModel
    # x, y = get_load_patterns_in_XYdirection(SapModel)
    # print(x)
    # print(y)
    # building = Build()
    # apply_cfactor_to_edb_and_analyze(building)
    # get_beqams_columns()

    get_drifts(4, 4, 4)