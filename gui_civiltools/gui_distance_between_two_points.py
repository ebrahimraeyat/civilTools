
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


class CivilDistance:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Distance")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Distance Between two points")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "distance.svg"
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
        from py_widget.tools import distance_between_two_points
        win = distance_between_two_points.Form(etabs)
        find_etabs.show_win(win, False)
        
    def IsActive(self):
        return True


        