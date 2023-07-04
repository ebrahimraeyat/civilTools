import sys
from pathlib import Path

FREECADPATH = 'G:\\program files\\FreeCAD 0.21\\bin'
sys.path.append(FREECADPATH)

import FreeCAD

civiltools_path = Path(__file__).absolute().parent.parent.parent
sys.path.insert(0, str(civiltools_path))

dxf_filename = civiltools_path / 'tests' / 'test_files' / 'column_block.dxf'

from freecad_py import dxf_funcs

def test_draw_circle():
    dxf_content = dxf_funcs.ImportDXF(dxf_filename)
    dxf_content.doc = FreeCAD.newDocument()
    dxf_content.create_layer()
    dxf_content.draw_block()
    FreeCAD.ActiveDocument.recompute()
    import tempfile
    temp_path = Path(tempfile.gettempdir())
    test_file_path = temp_path / "column.FCStd"
    dxf_content.doc.saveAs(str(test_file_path))


if __name__ == '__main__':
    test_draw_circle()