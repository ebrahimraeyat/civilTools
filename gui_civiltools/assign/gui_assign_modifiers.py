
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


class CivilToolsAssignModifiers:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_assign_modifiers",
            "Property Modifiers")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_assign_modifiers",
            "Assign Property Modifiers to ETABS Model")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "assign_modifiers.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=True)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget.assign import assign_modifiers
        win = assign_modifiers.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        
    def IsActive(self):
        return True

Gui.addCommand("civilTools_assign_modifiers", CivilToolsAssignModifiers())
        