
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui


class CivilConnectBeam:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Connect Beam")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Connect Two Beams that selected in ETABS Model")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "connect.svg"
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
        from py_widget.tools import connect
        win = connect.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        