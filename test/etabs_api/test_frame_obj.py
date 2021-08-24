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
        etabs = etabs_obj.EtabsModel(backup=False)
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
        etabs = etabs_obj.EtabsModel(backup=False)
        return etabs

@pytest.mark.getmethod
def test_get_beams_columns(shayesteh):
    beams, columns = shayesteh.frame_obj.get_beams_columns()
    assert len(beams) == 92
    assert len(columns) == 48

def test_get_beams_columns_weakness_structure(shayesteh):
    cols_pmm, col_fields, beams_rebars, beam_fields = shayesteh.frame_obj.get_beams_columns_weakness_structure('115')
    assert len(col_fields) == 5
    assert len(beam_fields) == 9
    assert len(cols_pmm) == 11
    assert len(beams_rebars) == 217

@pytest.mark.modify
def test_set_constant_j(shayesteh):
    shayesteh.frame_obj.set_constant_j(.15)
    js = set()
    beams, _ = shayesteh.frame_obj.get_beams_columns(2)
    for name in beams:
        j = shayesteh.SapModel.FrameObj.GetModifiers(name)[0][3]
        js.add(j)
    assert js == {.15}

@pytest.mark.getmethod
def test_get_beams_sections(shayesteh):
    beams_names = ('115',)
    beams_sections = shayesteh.frame_obj.get_beams_sections(beams_names)
    assert beams_sections == {'115': 'B35X50'}

@pytest.mark.getmethod
def test_get_t_crack(shayesteh):
    beams_names = ('115',)
    sec_t_crack = shayesteh.frame_obj.get_t_crack(beams_names=beams_names)
    assert pytest.approx(sec_t_crack, abs=.01) == {'B35X50': 2.272}

@pytest.mark.getmethod
def test_get_beams_torsion_prop_modifiers(shayesteh):
    beams_names = ('115', '120')
    beams_j = shayesteh.frame_obj.get_beams_torsion_prop_modifiers(beams_names)
    assert len(beams_j) == 2
    assert pytest.approx(beams_j['115'], abs=.01) == .35
    assert pytest.approx(beams_j['120'], abs=.01) == 1.0
