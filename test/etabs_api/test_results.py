import pytest
import comtypes.client
from pathlib import Path
import sys

civil_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civil_path))

from etabs_api import functions

@pytest.fixture
def shayesteh(edb="shayesteh.EDB"):
    try:
        etabs = functions.EtabsModel()
        if etabs.success:
            filepath = Path(etabs.SapModel.GetModelFilename())
            if 'test.' in filepath.name:
                return etabs
            else:
                raise NameError
    except:
        helper = comtypes.client.CreateObject('ETABSv1.Helper') 
        helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
        ETABSObject = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject")
        ETABSObject.ApplicationStart()
        SapModel = ETABSObject.SapModel
        SapModel.InitializeNewModel()
        SapModel.File.OpenFile(str(Path(__file__).parent / edb))
        asli_file_path = Path(SapModel.GetModelFilename())
        dir_path = asli_file_path.parent.absolute()
        test_file_path = dir_path / "test.EDB"
        SapModel.File.Save(str(test_file_path))
        etabs = functions.EtabsModel()
        return etabs

@pytest.mark.getmethod
def test_get_xy_period(shayesteh):
    Tx, Ty, i_x, i_y = shayesteh.results.get_xy_period()
    assert pytest.approx(Tx, abs=.01) == 1.291
    assert pytest.approx(Ty, abs=.01) == 1.291
    assert i_x == 2
    assert i_y == 2

def test_get_base_react(shayesteh):
    vx, vy = shayesteh.results.get_base_react()
    assert vx == pytest.approx(-110709.5, .1)
    assert vy == pytest.approx(-110709.5, .1)