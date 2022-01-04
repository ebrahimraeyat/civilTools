

from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui

from db import ostanha


class CivilToolsSettings:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_settings",
            "Settings")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_settings",
            "Settings")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "automatic.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}

    def Activated(self):
        import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        from py_widget import settings
        win = settings.Form(etabs)
        Gui.Control.showDialog(win)