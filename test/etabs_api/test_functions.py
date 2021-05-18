from unittest import mock
import pytest
from unittest.mock import Mock
import comtypes.client
from pathlib import Path
import sys

civil_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civil_path))

from etabs_api import functions

Tx_drift, Ty_drift = 1.085, 1.085

@pytest.fixture
def myETABSObject():
    helper = comtypes.client.CreateObject('ETABSv1.Helper') 
    helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
    ETABSObject = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject")
    ETABSObject.ApplicationStart()
    edb = "shayesteh.EDB"
    SapModel = ETABSObject.SapModel
    SapModel.InitializeNewModel()
    SapModel.File.OpenFile(str(Path(__file__).parent / edb))
    asli_file_path = Path(SapModel.GetModelFilename())
    dir_path = asli_file_path.parent.absolute()
    test_file_path = dir_path / "test.EDB"
    SapModel.File.Save(str(test_file_path))
    return ETABSObject

def close_etabs(ETABS):
    SapModel = ETABS.SapModel
    test_file_path = Path(SapModel.GetModelFilename())
    functions.close_etabs(ETABS)
    test_files = test_file_path.parent.glob('test.*')
    for f in test_files:
        f.unlink()

def test_get_beams_columns(myETABSObject):
    beams, columns = functions.get_beams_columns(myETABSObject)
    close_etabs(myETABSObject)
    assert len(beams) == 92
    assert len(columns) == 48

def test_get_drift_periods(myETABSObject):
    Tx_drift, Ty_drift, file_name = functions.get_drift_periods()
    close_etabs(myETABSObject)
    # assert pytest.approx(Tx_drift, .01) == 0.888
    # assert pytest.approx(Ty_drift, .01) == 0.738
    assert pytest.approx(Tx_drift, .01) == 1.085
    assert pytest.approx(Ty_drift, .01) == 1.085
    assert file_name.name == "test.EDB"

def test_apply_cfactor_to_edb(myETABSObject):
    building = Mock()
    building.results = [True, .123, .108]
    building.kx, building.ky = 1.18, 1.15
    building.results_drift = [True, .89, .98]
    building.kx_drift, building.ky_drift = 1.15, 1.2
    NumFatalErrors = functions.apply_cfactor_to_edb(building)
    close_etabs(myETABSObject)
    assert NumFatalErrors == 0

def test_get_drifts(myETABSObject):
    no_story, cdx, cdy = 4, 4.5, 4.5
    drifts = functions.get_drifts(no_story, cdx, cdy)
    close_etabs(myETABSObject)
    assert len(drifts[0]) == 10
    assert len(drifts) == 30

def test_calculate_drifts(myETABSObject, mocker):
    mocker.patch(
        'etabs_api.functions.get_drift_periods_calculate_cfactor_and_apply_to_edb',
        return_value = 0
    )
    no_story = 4
    widget = Mock()
    widget.final_building.x_system.cd = 4.5
    widget.final_building.y_system.cd = 4.5
    drifts = functions.calculate_drifts(widget, no_story)
    close_etabs(myETABSObject)
    assert len(drifts[0]) == 10


# def test_get_drift_periods_and_calculate_cfactor(mocker):
#     mocker.patch(
#         'etabs_api.functions.get_drift_periods',
#         return_value = (Tx_drift, Ty_drift)
#     )
#     from applications.cfactor.building.build import Building, StructureSystem
#     x = StructureSystem(u'قاب خمشی بتن آرمه متوسط', u"قاب خمشی بتن آرمه متوسط", 'X')
#     myBuilding = Building(
#         u'زیاد',
#         1, 'II', no_story, 15.48, None, x, x,
#         u'قم',
#         Tx_drift, Ty_drift, True)
#     results = myBuilding.results
#     results_drift = myBuilding.results_drift
    
#         cx, cy = results[1], results[2]
#         kx, ky = myBuilding.kx, myBuilding.ky
#         cx_drift, cy_drift = results_drift[1], results_drift[2]
#         kx_drift, ky_drift = myBuilding.kx_drift, myBuilding.ky_drift
#     assert Tx == 0.98
#     assert Ty == 0.84

#     no_story = 4
    


# def test_check_drifts(myETABSObject):


    


if __name__ == '__main__':
    myETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    test_get_drifts(myETABSObject)


