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

def test_create_wall():
    base = tos.getObjectsByLabel('B35_Story1_CenterLine')[0]
    wall_loads.create_wall(base, 0.2, .8, relative=True)

def test_assign_wall_loads_to_etabs():
    mod_path = civiltools_path.parent
    sys.path.insert(0, str(mod_path))
    import etabs_obj
    etabs = etabs_obj.EtabsModel(backup=False)
    wall_loads.assign_wall_loads_to_etabs(etabs)

if __name__ == '__main__':
    test_create_wall()
