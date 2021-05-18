import comtypes.client
from pathlib import Path


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

def get_beams_columns(etabs=None):
    if not etabs:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    table_key = "Frame Assignments - Summary"
    [_, _, FieldsKeysIncluded, _, TableData, _] = read_table(table_key, SapModel)
    data = reshape_data(FieldsKeysIncluded, TableData)

    beams = []
    columns = []
    i_type = FieldsKeysIncluded.index("Type")
    i_name = FieldsKeysIncluded.index("UniqueName")
    for frame_obj in data:
        name = frame_obj[i_name]
        type_ = frame_obj[i_type]
        if type_ == 'Beam':
            beams.append(name)
        elif type_ == 'Column':
            columns.append(name)
        # else:
        #     print(f"not recognize frame element!, name = {frame_obj}")
    return beams, columns

def get_drift_periods(
            etabs=None,
            t_filename="T.EDB",
            ):
    '''
    This function create an Etabs file called T.EDB from current open Etabs file,
    then in T.EDB file change the stiffness properties of frame elements according 
    to ACI 318 to get periods of structure, for this it set M22 and M33 stiffness of
    beams to 0.5 and column and wall to 1.0. Then it run the analysis and get the x and y period of structure.
    '''
    if not etabs:
        etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    asli_file_path = Path(SapModel.GetModelFilename())
    if asli_file_path.suffix.lower() != '.edb':
        asli_file_path = asli_file_path.with_suffix(".EDB")
    dir_path = asli_file_path.parent.absolute()
    t_file_path = dir_path / t_filename
    SapModel.File.Save(str(t_file_path))
    beams, columns = get_beams_columns(etabs)
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
    log = apply_table(SapModel)
    # print(log)

    # run model (this will create the analysis model)
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
    SapModel.File.OpenFile(str(asli_file_path))
    return Tx_drift, Ty_drift, asli_file_path



def get_drifts(no_story, cdx, cdy, show_table=False):
    myETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = myETABSObject.SapModel
    SapModel.SetModelIsLocked(False)
    SapModel.Analyze.RunAnalysis()
    TableKey = 'Diaphragm Max Over Avg Drifts'
    [_, _, FieldsKeysIncluded, _, TableData, _] = read_table(TableKey, SapModel)
    data = reshape_data(FieldsKeysIncluded, TableData)
    item_index = FieldsKeysIncluded.index("Item")
    # average_drift_index = FieldsKeysIncluded.index("Avg Drift")
    if no_story <= 5:
        limit = .025
    else:
        limit = .02
    for row in data:
        if row[item_index] == 'Diaph D1 X':
            cd = cdx
        elif row[item_index] == 'Diaph D1 Y':
            cd = cdy
        allowable_drift = limit / cd
        row.append(allowable_drift)
    if show_table:
        pass
    return data

def apply_cfactor_to_tabledata(TableData, FieldsKeysIncluded, building):
    data = reshape_data(FieldsKeysIncluded, TableData)
    i_xdir = FieldsKeysIncluded.index('XDir')
    i_ydir = FieldsKeysIncluded.index('YDir')
    i_c = FieldsKeysIncluded.index('C')
    i_k = FieldsKeysIncluded.index('K')
    i_name = FieldsKeysIncluded.index('Name')

    cx, cy = str(building.results[1]), str(building.results[2])
    kx, ky = str(building.kx), str(building.ky)
    cx_drift, cy_drift = str(building.results_drift[1]), str(building.results_drift[2])
    kx_drift, ky_drift = str(building.kx_drift), str(building.ky_drift)
    
    for earthquake in data:
        if 'drift' in earthquake[i_name].lower():
            if earthquake[i_xdir] == 'Yes':
                earthquake[i_c] = str(cx_drift)
                earthquake[i_k] = str(kx_drift)
            elif earthquake[i_ydir] == 'Yes':
                earthquake[i_c] = str(cy_drift)
                earthquake[i_k] = str(ky_drift)
        elif earthquake[i_xdir] == 'Yes':
            earthquake[i_c] = str(cx)
            earthquake[i_k] = str(kx)
        elif earthquake[i_ydir] == 'Yes':
            earthquake[i_c] = str(cy)
            earthquake[i_k] = str(ky)
    table_data = unique_data(data)
    return table_data

def apply_cfactor_to_edb(
        building,
        ):
    myETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = myETABSObject.SapModel
    SapModel.SetModelIsLocked(False)
    TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
    [_, TableVersion, FieldsKeysIncluded, NumberRecords, TableData, _] = read_table(TableKey, SapModel)
    TableData1 = apply_cfactor_to_tabledata(TableData, FieldsKeysIncluded, building)
    FieldsKeysIncluded1 = [
                            'Name',
                            'Is Auto Load',
                            'X Dir?',
                            'X Dir Plus Ecc?',
                            'X Dir Minus Ecc?',
                            'Y Dir?',
                            'Y Dir Plus Ecc?',
                            'Y Dir Minus Ecc?',
                            'Ecc Ratio',
                            'Top Story',
                            'Bot Story',
                            'C',
                            'K',
                            ]
    SapModel.DatabaseTables.SetTableForEditingArray(TableKey, TableVersion, FieldsKeysIncluded1, NumberRecords, TableData1)
    NumFatalErrors = apply_table(SapModel)
    SapModel.File.Save()
    return NumFatalErrors

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
    return num_errors

def calculate_drifts(
            widget,
            no_story=None,
            etabs=None):
    get_drift_periods_calculate_cfactor_and_apply_to_edb(widget, etabs)
    if not no_story:
        no_story = widget.storySpinBox.value()
    cdx = widget.final_building.x_system.cd
    cdy = widget.final_building.y_system.cd
    drifts = get_drifts(no_story, cdx, cdy, True)
    return drifts