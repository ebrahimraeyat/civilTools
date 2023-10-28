
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
        from exporter import civiltools_config
        d = civiltools_config.get_settings_from_etabs(etabs)
        if len(d) == 0:
            QMessageBox.warning(None, 'Settings', 'Please Set Options First!')
            Gui.runCommand("civiltools_settings")
        d = civiltools_config.get_settings_from_etabs(etabs)
        if len(d) == 0:
            return
        from py_widget.control import control_deflection
        win = control_deflection.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_check_deflection", CivilToolsCheckDeflection())