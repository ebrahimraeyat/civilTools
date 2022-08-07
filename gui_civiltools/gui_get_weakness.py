
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilGetWeakness:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_weakness",
            "Get Weakness")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_weakness",
            "Get Weakness")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "weakness.svg"
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
            'weakness.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/3c8c1d0229dc76ec23982af1173aa46a/raw',
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
        from py_widget import get_weakness
        win = get_weakness.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


        