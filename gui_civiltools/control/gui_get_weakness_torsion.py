
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilGetWeaknessTorsion:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_weakness",
            "Weakness torsion")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_weakness",
            "Save the current file as new filename and weakness the new structure and then calculate the torsion")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "weakness_torsion.svg"
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
        from py_widget.control import get_weakness_torsion
        win = get_weakness_torsion.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        
    def IsActive(self):
        return True


        