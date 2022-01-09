
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

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
                   Path(__file__).parent.absolute().parent / "images" / "clear.svg"
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
        from py_widget.tools import delete_backups
        win = delete_backups.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        