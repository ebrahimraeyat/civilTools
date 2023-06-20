import pytest
from pathlib import Path
import tempfile

import etabs_obj

@pytest.fixture
def zoghian(edb="zoghian.EDB"):
    try:
        etabs = etabs_obj.EtabsModel(backup=False)
        if etabs.success:
            filepath = Path(etabs.SapModel.GetModelFilename())
            if 'test.' in filepath.name:
                return etabs
            else:
                return create_test_file(etabs)
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        etabs = etabs_obj.EtabsModel(
                attach_to_instance=False,
                backup = False,
                model_path = Path(__file__).parent / 'test_files' / edb,
                software_exe_path=r'G:\program files\Computers and Structures\ETABS 19\ETABS.exe'
            )
        return create_test_file(etabs)

def create_test_file(etabs, suffix='EDB', filename='test'):
    temp_path = Path(tempfile.gettempdir())
    test_file_path = temp_path / f"{filename}.{suffix}"
    etabs.SapModel.File.Save(str(test_file_path))
    return etabs

def get_temp_filepath(suffix='EDB', filename='test') -> Path:
    temp_path = Path(tempfile.gettempdir())
    temp_file_path = temp_path / f"{filename}.{suffix}"
    return temp_file_path
