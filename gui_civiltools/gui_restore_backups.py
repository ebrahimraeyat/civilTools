
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui


class CivilRestoreBackups:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Restore Backups")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Restore Previous Saved Backups")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "restore_backup.svg"
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
        from py_widget.tools import restore_backup
        win = restore_backup.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        