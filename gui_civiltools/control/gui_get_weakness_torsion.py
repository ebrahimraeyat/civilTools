
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
        from py_widget.control import get_weakness_torsion
        import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        win = get_weakness_torsion.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        