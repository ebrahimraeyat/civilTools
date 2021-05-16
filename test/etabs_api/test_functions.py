import pytest
import comtypes.client
from pathlib import Path
import sys

civil_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civil_path))

from etabs_api import functions

@pytest.fixture
def myETABSObject():
    helper = comtypes.client.CreateObject('ETABSv1.Helper') 
    helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
    myETABSObject = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject")
    myETABSObject.ApplicationStart()
    return myETABSObject

def test_get_drift_periods(myETABSObject):
    edb = "shayesteh.EDB"
    SapModel = myETABSObject.SapModel
    SapModel.InitializeNewModel()
    SapModel.File.OpenFile(str(Path(__file__).parent / edb))
    Tx_drift, Ty_drift = functions.get_drift_periods()
    SapModel.SetModelIsLocked(False)
    # close the program
    myETABSObject.ApplicationExit(False)
    SapModel = None
    myETABSObject = None
    assert pytest.approx(Tx_drift, .01) == 0.888
    assert pytest.approx(Ty_drift, .01) == 0.738

def test_get_drifts(myETABSObject):
    no_story, cdx, cdy = 4, 4.5, 4.5
    edb = "shayesteh.EDB"
    SapModel = myETABSObject.SapModel
    SapModel.InitializeNewModel()
    SapModel.File.OpenFile(str(Path(__file__).parent / edb))
    drifts = functions.get_drifts(no_story, cdx, cdy)
    SapModel.SetModelIsLocked(False)
    # close the program
    myETABSObject.ApplicationExit(False)
    SapModel = None
    myETABSObject = None
    assert len(drifts[0]) == 11
    # assert len(drifts) == 30
    print(drifts)

if __name__ == '__main__':
    myETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    test_get_drifts(myETABSObject)


