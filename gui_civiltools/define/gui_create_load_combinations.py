
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilToolsCreateLoadCombinations:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Create Load Combinations")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Create Load Combinations")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "load_combinations.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        
        # from gui_civiltools.gui_check_legal import (
        #         allowed_to_continue,
        #         show_warning_about_number_of_use,
        #         )
        # allow, check = allowed_to_continue(
        #     '100-30.bin',
        #     'https://gist.githubusercontent.com/ebrahimraeyat/bbfab4efcc50cbcfeba7288339b68c90/raw',
        #     'cfactor',
        #     n=2,
        #     )
        # if not allow:
        #     return
        from gui_civiltools import open_etabs
        etabs, filename = open_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget.define import create_load_combinations
        win = create_load_combinations.Form(etabs)
        Gui.Control.showDialog(win)
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


        