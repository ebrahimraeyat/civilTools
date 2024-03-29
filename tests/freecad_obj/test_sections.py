import sys
from pathlib import Path

FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)

import FreeCAD


punch_path = Path(__file__).absolute().parent.parent.parent
sys.path.insert(0, str(punch_path))

from freecad_obj import sections

def test_make_column_section():
    FreeCAD.newDocument()
    sections.make_column_section(
        400,
        500,
        4,
        6,
        '25',
        '10',
        40,
        rebar_diameters_names={'10': '10d', '25': '25d'},
    )


if __name__ == '__main__':
    test_make_column_section()