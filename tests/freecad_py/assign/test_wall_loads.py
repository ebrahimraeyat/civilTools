import sys
from pathlib import Path

FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)

import FreeCAD

civiltools_path = Path(__file__).absolute().parent.parent.parent.parent
sys.path.insert(0, str(civiltools_path))

wall = civiltools_path / 'tests' / 'test_files' / 'wall.FCStd'
wall = FreeCAD.openDocument(str(wall))

from tests.etabs_files import zoghian
from freecad_py.assign.wall_loads import update_levels

def test_update_levels(zoghian):
    update_levels(zoghian, wall)
    zoghian.set_current_unit('N', 'mm')
    stories_levels = zoghian.story.storyname_and_levels()
    for o in wall.Objects:
        if hasattr(o, 'IfcType') and o.IfcType == 'Building Storey':
            label = o.Label
            current_level = o.Placement.Base.z
            new_level = stories_levels.get(label, current_level)
            assert current_level == new_level


if __name__ == '__main__':
    test_make_column_section()