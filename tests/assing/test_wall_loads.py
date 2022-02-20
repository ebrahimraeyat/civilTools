import sys
from pathlib import Path

# path to FreeCAD.so
FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

civiltools_path = Path(__file__).absolute().parent.parent.parent
sys.path.insert(0, str(civiltools_path))
from freecad_py.assign import wall_loads

tos = civiltools_path / 'tests' / 'test_files' / 'tos.FCStd'
tos = FreeCAD.openDocument(str(tos))

def test_add_wall_on_beams():
    wall_loads.add_wall_on_beams(
        'Dead', 220,
        labels = ('B35',),
        # stories=('Story1', 'Story9'), 
        opening_ratio=0.3,
        #  height=3000,
        )

if __name__ == '__main__':
    test_add_wall_on_beams()
