
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui



class CivilToolsControlColumns:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Column Control")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Control the columns for problems")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "columns_control.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=True)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget.control import columns_control
        win = columns_control.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_columns_control", CivilToolsControlColumns())