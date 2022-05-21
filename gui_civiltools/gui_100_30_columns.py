
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilTools100_30Columns:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Investigate 100-30")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Check if needed apply 100-30")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "100_30.svg"
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
            '100-30.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/bbfab4efcc50cbcfeba7288339b68c90/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        from gui_civiltools import open_etabs
        etabs, filename = open_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        ex, ey = etabs.load_patterns.get_EX_EY_load_pattern()
        if ex is None or ey is None:
            QMessageBox.warning(None, 'ETABS', 'Please Define EX and EY in ETABS Model.')
            return False
        from py_widget.control import columns_100_30
        win = columns_100_30.Form(etabs, ex, ey)
        Gui.Control.showDialog(win)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


        