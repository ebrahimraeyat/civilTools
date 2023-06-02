
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilToolsCheckDeflection:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Check Deflection")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Check Deflection for selected beam")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "deflection.svg"
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
        from py_widget.control import control_deflection
        win = control_deflection.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_check_deflection", CivilToolsCheckDeflection())