import sys
from pathlib import Path

# path to FreeCAD.so
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

civiltools_path = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(civiltools_path))
import import_model
document= FreeCAD.newDocument()

def test_import_model():
    import_model.import_model()

if __name__ == '__main__':
    test_import_model()
