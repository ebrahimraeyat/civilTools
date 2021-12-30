
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui



class CivilOffsetBeam:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_offset_beam",
            "Offset Beam")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_offset_beam",
            "offset beam")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "offset.svg"
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
        from py_widget.tools import offset
        win = offset.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        