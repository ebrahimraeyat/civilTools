
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilToolsCheckDeflectionOfSlab:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Slab Deflection")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Check Deflection of Selected Slabs")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "deflection_of_slab.png"
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
            'check_deflection.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/74c1a371b99c62de47472a6046a91a97/raw',
            'cfactor'
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
        from py_widget.control import control_deflection_of_slab
        win = control_deflection_of_slab.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_check_deflection_of_slab", CivilToolsCheckDeflectionOfSlab())