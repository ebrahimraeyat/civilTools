
from pathlib import Path

from PySide import QtCore

import FreeCADGui as Gui



class CivilHighPressureColumns:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_high_pressure_columns",
            "High Pressure Columns")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_high_pressure_columns",
            "Get High Pressure Columns")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "high_pressure_columns.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        
        from gui_civiltools.gui_check_legal import (
                allowed_to_continue,
                show_warning_about_number_of_use,
                )
        allow, check = allowed_to_continue(
            'high_pressure_columns.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/4800d8c54ee47c50032cd70d45cf43ee/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget.control import high_pressure_columns
        win = high_pressure_columns.Form(etabs)
        Gui.Control.showDialog(win)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


        