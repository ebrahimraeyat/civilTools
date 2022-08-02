
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui



class CivilWallLoadOnFrames:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Wall Load")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Wall Load on Frames")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "wall.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget.assign import wall_load_on_frames
        win = wall_load_on_frames.Form(etabs)
        win.form.show()
        
    def IsActive(self):
        return True


        