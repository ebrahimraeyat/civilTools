
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui



class CivilOffsetBeam:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_offset_beam",
            "Offset Beam")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_offset_beam",
            "offset beam")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "offset.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        from gui_civiltools import open_etabs
        etabs, filename = open_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget.tools import offset
        win = offset.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        