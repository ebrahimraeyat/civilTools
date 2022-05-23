
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilShowWeakness:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_weakness",
            "Weakness")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_weakness",
            "Show Weakness Tables")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "show_weakness.svg"
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
        from py_widget import show_weakness
        win = show_weakness.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        