
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

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
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget import import_model
        win = import_model.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        