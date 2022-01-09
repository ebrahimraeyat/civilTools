
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui



class CivilWallLoadOnFrames:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Wall Load")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Wall Load on Frames")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "wall.svg"
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
        from py_widget.assign import wall_load_on_frames
        win = wall_load_on_frames.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        