
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
        
        import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not etabs.success:
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        from py_widget.tools import restore_backup
        win = restore_backup.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        