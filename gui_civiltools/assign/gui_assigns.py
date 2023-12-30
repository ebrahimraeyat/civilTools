
from pathlib import Path

from PySide2 import QtCore
# from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui


class CivilToolsAssigns:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_assigns",
            "Assigns")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_assigns",
            "Assigns to ETABS Model")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "assigns.svg"
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
        from py_widget.assign import assigns
        win = assigns.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        
    def IsActive(self):
        return True

Gui.addCommand("civilTools_assigns", CivilToolsAssigns())
        