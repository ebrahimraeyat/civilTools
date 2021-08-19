import pytest
import comtypes.client
from pathlib import Path
import sys

civil_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civil_path))
from etabs_api import etabs_obj

@pytest.fixture
def shayesteh(edb="shayesteh.EDB"):
    try:
        etabs = etabs_obj.EtabsModel()
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
        etabs = etabs_obj.EtabsModel()
        return etabs

@pytest.mark.getmethod
def test_get_load_cases(shayesteh):
    load_case_names = shayesteh.load_cases.get_load_cases()
    assert len(load_case_names) == 22

@pytest.mark.getmethod
def test_get_modal_loadcase_name(shayesteh):
    name = shayesteh.load_cases.get_modal_loadcase_name()
    assert name == 'Modal'

@pytest.mark.getmethod
def test_get_loadcase_withtype(shayesteh):
    name = shayesteh.load_cases.get_loadcase_withtype(4)
    assert name == ['SX', 'SY', 'SPX', 'SPY']