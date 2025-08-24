
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


class CivilDeleteBackups:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Delete Backups")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Delete Backup files that automatically created with Software")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "clear.png"
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
        from py_widget.tools import delete_backups
        win = delete_backups.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        