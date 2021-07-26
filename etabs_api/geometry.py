from os.path import sameopenfile
import os
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
    return NumFatalErrors, ret

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

def get_story_boundbox(SapModel, story_name) -> tuple:
    SapModel.SetPresentUnits_2(5, 5, 2)
    points = SapModel.PointObj.GetNameListOnStory(story_name)[1]
    xs = []
    ys = []
    for p in points:
        x, y, _, _ =  SapModel.PointObj.GetCoordCartesian(p)
        xs.append(x)
        ys.append(y)
    x_max = max(xs)
    x_min = min(xs)
    y_max = max(ys)
    y_min = min(ys)
    return x_min, y_min, x_max, y_max

def get_stories_boundbox(SapModel) -> dict:
    stories = SapModel.Story.GetNameList()[1]
    stories_bb = {}
    for story in stories:
        bb = get_story_boundbox(SapModel, story)
        stories_bb[story] = bb
    return stories_bb

def get_stories_length(SapModel):
    story_bb = get_stories_boundbox(SapModel)
    stories_length = {}
    for story, bb in story_bb.items():
        len_x = bb[2] - bb[0]
        len_y = bb[3] - bb[1]
        stories_length[story] = (len_x, len_y)
    return stories_length

            
if __name__ == '__main__':
    etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel