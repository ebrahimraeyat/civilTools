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
def test_get_beams_columns(shayesteh):
    beams, columns = shayesteh.frame_obj.get_beams_columns()
    assert len(beams) == 92
    assert len(columns) == 48

def test_get_beams_columns_weakness_structure(shayesteh):
    cols_pmm, col_fields, beams_rebars, beam_fields = shayesteh.frame_obj.get_beams_columns_weakness_structure()
    assert len(col_fields) == 5
    assert len(beam_fields) == 9
    assert len(cols_pmm) == 11
    assert len(beams_rebars) == 217