
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilToolsExpandAreaLoadSets:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Expand Area Load Sets")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Expand Area Load Sets")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "expand_area_load_sets.jpg"
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
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=True)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget.tools import expand_area_load_sets
        expand_area_load_sets.Form(etabs)
        
    def IsActive(self):
        return True
    

Gui.addCommand("expand_area_load_sets", CivilToolsExpandAreaLoadSets())


        