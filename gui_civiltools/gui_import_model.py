
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilToolsImportModel:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Import Model")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Import ETABS Model into FreeCAD")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "import.svg"
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
        from py_widget import import_model
        win = import_model.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        