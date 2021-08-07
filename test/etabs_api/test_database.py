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

def test_get_story_mass(shayesteh):
    story_mass = shayesteh.database.get_story_mass()
    assert len(story_mass) == 5
    assert pytest.approx(float(story_mass[2][1]), abs=1) == 17696

def test_get_center_of_rigidity(shayesteh):
    cor = shayesteh.database.get_center_of_rigidity()
    assert len(cor) == 5
    assert cor['STORY1'] == ('9.3844', '3.7778')

@pytest.mark.getmethod
def test_get_stories_displacement_in_xy_modes(shayesteh):
    dx, dy, wx, wy = shayesteh.database.get_stories_displacement_in_xy_modes()
    assert len(dx) == 5
    assert len(dy) == 5
    assert pytest.approx(wx, abs=.01) == 4.868
    assert pytest.approx(wy, abs=.01) == 4.868

def test_get_story_forces(shayesteh):
    forces, loadcases, _ = shayesteh.database.get_story_forces()
    assert len(forces) == 10
    assert loadcases == ('QX', 'QY')

def test_multiply_seismic_loads(shayesteh):
    NumFatalErrors, ret = shayesteh.database.multiply_seismic_loads(.67)
    assert NumFatalErrors == ret == 0
    ret = shayesteh.SapModel.Analyze.RunAnalysis()
    assert ret == 0

def test_write_aj_user_coefficient(shayesteh):
    shayesteh.load_patterns.select_all_load_patterns()
    TableKey = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
    [_, _, FieldsKeysIncluded, _, TableData, _] = shayesteh.database.read_table(TableKey)
    import pandas as pd
    df = pd.DataFrame({'OutputCase': 'QXP',
                        'Story': 'Story1',
                        'Diaph': 'D1',
                        'Ecc. Length (Cm)': 82,
                        }, index=range(1))
    NumFatalErrors, ret = shayesteh.database.write_aj_user_coefficient(TableKey, FieldsKeysIncluded, TableData, df)
    assert NumFatalErrors == ret == 0
    ret = shayesteh.SapModel.Analyze.RunAnalysis()
    assert ret == 0